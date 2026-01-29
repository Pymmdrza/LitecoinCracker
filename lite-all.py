# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Litecoin Wallet Scanner - Professional Edition            ║
║══════════════════════════════════════════════════════════════════════════════║
║  Description : High-performance Litecoin address generator & balance checker ║
║  Author      : M M D R Z A                                                   ║
║  Website     : Mmdrza.Com                                                    ║
║  Contact     : Info@Mmdrza.Com | Telegram: @Mr1Mmdrza                        ║
║  Repository  : Github.Com/Pymmdrza/LitecoinCracker                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import asyncio
import logging
import os
import random
import signal
import sys
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import AsyncIterator, Optional

import aiohttp
from libcrypto import Wallet
from rich import box
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

# ══════════════════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Config:
    """Application configuration settings."""

    # API Configuration
    API_BASE_URL: str = "https://litecoin.atomicwallet.io/api/address"
    API_TIMEOUT: int = 10
    API_RETRY_ATTEMPTS: int = 3
    API_RETRY_DELAY: float = 1.0

    # Concurrency Settings
    MAX_CONCURRENT_REQUESTS: int = 4
    REQUEST_DELAY: float = 0.25

    # Output Configuration
    OUTPUT_DIR: Path = field(default_factory=lambda: Path("output"))
    WINNER_FILE: str = "ltc_winners_{date}.txt"
    LOG_FILE: str = "ltc_scanner_{date}.log"

    # Display Settings
    REFRESH_RATE: float = 0.1
    SHOW_PROGRESS: bool = True

    def __post_init__(self) -> None:
        """Ensure output directory exists."""
        object.__setattr__(self, "OUTPUT_DIR", Path(self.OUTPUT_DIR))
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Enums & Data Classes
# ══════════════════════════════════════════════════════════════════════════════

class AddressType(Enum):
    """Litecoin address types."""

    P2PKH = "p2pkh"
    P2SH_P2WPKH = "p2sh-p2wpkh"
    P2WPKH = "p2wpkh"

    @property
    def display_name(self) -> str:
        """Human-readable address type name."""
        return {
            AddressType.P2PKH: "LTC-P2PKH",
            AddressType.P2SH_P2WPKH: "LTC-P2SH-P2WPKH",
            AddressType.P2WPKH: "LTC-P2WPKH",
        }[self]


@dataclass
class WalletAddress:
    """Represents a wallet address with its metadata."""

    address: str
    address_type: AddressType
    balance: int = 0
    total_received: int = 0
    total_sent: int = 0
    tx_count: int = 0

    @property
    def has_balance(self) -> bool:
        """Check if address has positive balance."""
        return self.balance > 0

    @property
    def has_history(self) -> bool:
        """Check if address has any transaction history."""
        return self.tx_count > 0 or self.total_received > 0


@dataclass
class GeneratedWallet:
    """Represents a complete generated wallet with all address types."""

    private_key: str
    addresses: list[WalletAddress] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)

    @property
    def has_any_balance(self) -> bool:
        """Check if any address has balance."""
        return any(addr.has_balance for addr in self.addresses)

    @property
    def total_balance(self) -> int:
        """Sum of all address balances."""
        return sum(addr.balance for addr in self.addresses)


@dataclass
class ScannerStats:
    """Scanner statistics tracker."""

    total_scanned: int = 0
    winners_found: int = 0
    api_errors: int = 0
    start_time: datetime = field(default_factory=datetime.now)

    @property
    def scan_rate(self) -> float:
        """Calculate scans per second."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return self.total_scanned / max(elapsed, 1)

    @property
    def elapsed_time(self) -> str:
        """Format elapsed time."""
        elapsed = datetime.now() - self.start_time
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# ══════════════════════════════════════════════════════════════════════════════
# Logging Setup
# ══════════════════════════════════════════════════════════════════════════════

def setup_logging(config: Config) -> logging.Logger:
    """Configure application logging."""
    log_file = config.OUTPUT_DIR / config.LOG_FILE.format(
        date=datetime.now().strftime("%Y%m%d_%H%M%S")
    )

    logger = logging.getLogger("LTCScanner")
    logger.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


# ══════════════════════════════════════════════════════════════════════════════
# Abstract Base Classes
# ══════════════════════════════════════════════════════════════════════════════


class IBlockchainAPI(ABC):
    """Interface for blockchain API interactions."""

    @abstractmethod
    async def get_address_info(self, address: str) -> dict:
        """Fetch address information from blockchain."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Clean up resources."""
        pass


class IWalletGenerator(ABC):
    """Interface for wallet generation."""

    @abstractmethod
    def generate(self) -> GeneratedWallet:
        """Generate a new wallet."""
        pass


class IResultWriter(ABC):
    """Interface for writing scan results."""

    @abstractmethod
    async def write_winner(self, wallet: GeneratedWallet) -> None:
        """Write winning wallet to storage."""
        pass


# ══════════════════════════════════════════════════════════════════════════════
# Implementation Classes
# ══════════════════════════════════════════════════════════════════════════════


class LitecoinAPI(IBlockchainAPI):
    """Litecoin blockchain API client with retry logic."""

    def __init__(
        self,
        config: Config,
        logger: logging.Logger,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self._config = config
        self._logger = logger
        self._session = session
        self._semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)

    @asynccontextmanager
    async def _get_session(self) -> AsyncIterator[aiohttp.ClientSession]:
        """Get or create HTTP session."""
        if self._session is not None:
            yield self._session
        else:
            async with aiohttp.ClientSession() as session:
                yield session

    async def get_address_info(self, address: str) -> dict:
        """Fetch address information with retry logic."""
        url = f"{self._config.API_BASE_URL}/{address}?details=basic"

        async with self._semaphore:
            for attempt in range(self._config.API_RETRY_ATTEMPTS):
                try:
                    async with self._get_session() as session:
                        async with session.get(
                            url,
                            timeout=aiohttp.ClientTimeout(
                                total=self._config.API_TIMEOUT
                            ),
                        ) as response:
                            if response.status == 200:
                                return await response.json()

                            self._logger.warning(
                                f"API returned status {response.status} for {address}"
                            )

                except asyncio.TimeoutError:
                    self._logger.warning(
                        f"Timeout fetching {address} (attempt {attempt + 1})"
                    )
                except aiohttp.ClientError as e:
                    self._logger.warning(
                        f"Client error for {address}: {e} (attempt {attempt + 1})"
                    )

                if attempt < self._config.API_RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(self._config.API_RETRY_DELAY * (attempt + 1))

            return {"balance": 0, "error": True}

    async def close(self) -> None:
        """Close the session if owned."""
        if self._session is not None:
            await self._session.close()


class LitecoinWalletGenerator(IWalletGenerator):
    """Generates Litecoin wallets with multiple address types."""

    def generate(self) -> GeneratedWallet:
        """Generate a new wallet with all address types."""
        private_key = "%064x" % random.getrandbits(256)
        wallet = Wallet(private_key)

        addresses = [
            WalletAddress(
                address=wallet.get_address("litecoin", address_type=addr_type.value),
                address_type=addr_type,
            )
            for addr_type in AddressType
        ]

        return GeneratedWallet(private_key=private_key, addresses=addresses)


class FileResultWriter(IResultWriter):
    """Writes winning wallets to file."""

    def __init__(self, config: Config, logger: logging.Logger) -> None:
        self._config = config
        self._logger = logger
        self._file_path = config.OUTPUT_DIR / config.WINNER_FILE.format(
            date=datetime.now().strftime("%Y%m%d")
        )
        self._lock = asyncio.Lock()

    async def write_winner(self, wallet: GeneratedWallet) -> None:
        """Write winning wallet to file with async lock."""
        async with self._lock:
            content = self._format_wallet(wallet)

            # Use sync file I/O in executor for better performance
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._write_to_file, content)

            self._logger.info(f"Winner saved: Total balance {wallet.total_balance}")

    def _write_to_file(self, content: str) -> None:
        """Synchronous file write operation."""
        with open(self._file_path, "a", encoding="utf-8") as f:
            f.write(content)

    def _format_wallet(self, wallet: GeneratedWallet) -> str:
        """Format wallet data for file output."""
        lines = [
            f"{'═' * 60}",
            f"Found: {wallet.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Private Key: {wallet.private_key}",
            f"{'─' * 60}",
        ]

        for addr in wallet.addresses:
            lines.append(
                f"{addr.address_type.display_name}: {addr.address} | "
                f"Balance: {addr.balance} | TxCount: {addr.tx_count}"
            )

        lines.extend([f"{'═' * 60}", ""])
        return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# Display Manager
# ══════════════════════════════════════════════════════════════════════════════


class DisplayManager:
    """Manages rich console output."""

    def __init__(self, console: Console) -> None:
        self._console = console

    def create_wallet_table(
        self, wallet: GeneratedWallet, stats: ScannerStats
    ) -> Table:
        """Create a formatted table for wallet display."""
        table = Table(
            title=self._create_title(stats),
            title_style="bold cyan",
            header_style="bold white on dark_green",
            border_style="bright_green",
            box=box.ROUNDED,
            show_lines=False,
            row_styles=["on grey15", "on grey11", "on grey15"],
            padding=(0, 1),
            expand=False,
        )

        table.add_column("Type", justify="right", style="green_yellow bold", width=18)
        table.add_column("Address", style="white", width=45)
        table.add_column("Balance", justify="right", style="gold1", width=15)
        table.add_column("TxCount", justify="right", style="cyan", width=10)

        for addr in wallet.addresses:
            balance_style = "bold green" if addr.has_balance else "dim"
            table.add_row(
                addr.address_type.display_name,
                addr.address,
                f"[{balance_style}]{addr.balance:,}[/]",
                str(addr.tx_count),
            )

        return table

    def create_stats_panel(self, stats: ScannerStats) -> Panel:
        """Create statistics panel."""
        content = (
            f"[cyan]Scanned:[/] {stats.total_scanned:,} | "
            f"[green]Winners:[/] {stats.winners_found} | "
            f"[yellow]Rate:[/] {stats.scan_rate:.2f}/s | "
            f"[magenta]Elapsed:[/] {stats.elapsed_time} | "
            f"[red]Errors:[/] {stats.api_errors}"
        )
        return Panel(content, title="Statistics", border_style="blue")

    def _create_title(self, stats: ScannerStats) -> str:
        """Create table title with stats."""
        return (
            f"[bold gold1]⚡ Litecoin Scanner[/] │ "
            f"[cyan]Scan #{stats.total_scanned:,}[/] │ "
            f"[green]Winners: {stats.winners_found}[/]"
        )

    def print_banner(self) -> None:
        """Print application banner."""
        banner = """
[bold cyan]╔══════════════════════════════════════════════════════════════════╗
║[/][bold gold1]          ⚡ LITECOIN WALLET SCANNER - PRO EDITION ⚡            [/][bold cyan]║
║══════════════════════════════════════════════════════════════════║
║[/]  [dim]High-Performance Address Generator & Balance Checker[/]         [bold cyan]║
║[/]  [dim]Press Ctrl+C to stop scanning gracefully[/]                     [bold cyan]║
╚══════════════════════════════════════════════════════════════════╝[/]
"""
        self._console.print(banner)


# ══════════════════════════════════════════════════════════════════════════════
# Main Scanner Engine
# ══════════════════════════════════════════════════════════════════════════════


class LitecoinScanner:
    """Main scanner orchestrator."""

    def __init__(
        self,
        config: Config,
        api: IBlockchainAPI,
        generator: IWalletGenerator,
        writer: IResultWriter,
        display: DisplayManager,
        logger: logging.Logger,
    ) -> None:
        self._config = config
        self._api = api
        self._generator = generator
        self._writer = writer
        self._display = display
        self._logger = logger
        self._stats = ScannerStats()
        self._running = True
        self._console = Console()

    async def scan_wallet(self, wallet: GeneratedWallet) -> None:
        """Scan all addresses in a wallet for balances."""
        tasks = [self._fetch_address_info(addr) for addr in wallet.addresses]
        await asyncio.gather(*tasks)

    async def _fetch_address_info(self, address: WalletAddress) -> None:
        """Fetch and update address information."""
        try:
            info = await self._api.get_address_info(address.address)
            address.balance = int(info.get("balance", 0))
            address.total_received = int(info.get("totalReceived", 0))
            address.total_sent = int(info.get("totalSent", 0))
            address.tx_count = int(info.get("txs", 0))

            if info.get("error"):
                self._stats.api_errors += 1

        except (ValueError, TypeError) as e:
            self._logger.error(f"Error parsing response for {address.address}: {e}")
            self._stats.api_errors += 1

    async def process_wallet(self, wallet: GeneratedWallet) -> None:
        """Process a single wallet: scan and handle results."""
        await self.scan_wallet(wallet)

        if wallet.has_any_balance:
            self._stats.winners_found += 1
            await self._writer.write_winner(wallet)
            self._logger.info(f"🎉 WINNER FOUND! Balance: {wallet.total_balance}")

        self._stats.total_scanned += 1

    def stop(self) -> None:
        """Signal scanner to stop."""
        self._running = False
        self._logger.info("Shutdown signal received")

    async def run(self) -> None:
        """Main scanning loop."""
        self._display.print_banner()
        self._logger.info("Scanner started")

        try:
            with Live(
                self._display.create_stats_panel(self._stats),
                console=self._console,
                refresh_per_second=10,
                transient=True,
            ) as live:
                while self._running:
                    wallet = self._generator.generate()
                    await self.process_wallet(wallet)

                    # Update display
                    table = self._display.create_wallet_table(wallet, self._stats)
                    stats_panel = self._display.create_stats_panel(self._stats)

                    from rich.layout import Layout

                    layout = Layout()
                    layout.split_column(Layout(stats_panel, size=3), Layout(table))
                    live.update(layout)

                    # Rate limiting
                    await asyncio.sleep(self._config.REQUEST_DELAY)

        except asyncio.CancelledError:
            self._logger.info("Scanner cancelled")
        finally:
            self._print_summary()

    def _print_summary(self) -> None:
        """Print final summary."""
        summary = f"""
[bold green]╔══════════════════════════════════════════════════════════════════╗
║                        SCAN COMPLETE                             ║
╠══════════════════════════════════════════════════════════════════╣
║  Total Scanned  : {self._stats.total_scanned:>10,}               ║
║  Winners Found  : {self._stats.winners_found:>10,}               ║
║  API Errors     : {self._stats.api_errors:>10,}                  ║
║  Elapsed Time   : {self._stats.elapsed_time:>10}                 ║
║  Scan Rate      : {self._stats.scan_rate:>10.2f}/s               ║
╚══════════════════════════════════════════════════════════════════╝[/]
"""
        self._console.print(summary)
        self._logger.info(
            f"Scan complete: {self._stats.total_scanned} scanned, "
            f"{self._stats.winners_found} winners"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Application Entry Point
# ══════════════════════════════════════════════════════════════════════════════

async def main() -> None:
    """Application entry point."""
    config = Config()
    console = Console()
    logger = setup_logging(config)

    # Initialize components
    async with aiohttp.ClientSession() as session:
        api = LitecoinAPI(config, logger, session)
        generator = LitecoinWalletGenerator()
        writer = FileResultWriter(config, logger)
        display = DisplayManager(console)

        scanner = LitecoinScanner(
            config=config,
            api=api,
            generator=generator,
            writer=writer,
            display=display,
            logger=logger,
        )

        # Setup signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()

        def signal_handler():
            scanner.stop()

        if sys.platform != "win32":
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, signal_handler)

        try:
            await scanner.run()
        except KeyboardInterrupt:
            scanner.stop()
            console.print("\n[yellow]Shutting down gracefully...[/]")
        finally:
            await api.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScanner terminated by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
