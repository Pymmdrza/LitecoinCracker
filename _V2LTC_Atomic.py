#              ||================================||
#              ||- ╔╦╗╔╦╗╔╦╗╦═╗╔═╗╔═╗ ╔═╗╔═╗╔╦╗ -||
#              ||- ║║║║║║ ║║╠╦╝╔═╝╠═╣ ║  ║ ║║║║ -||
#              ||- ╩ ╩╩ ╩═╩╝╩╚═╚═╝╩ ╩o╚═╝╚═╝╩ ╩ -||
#              ||--------------------------------||
#              ||-| WebSite : Mmdrza.Com        -||
#              ||-| Mail : X4@Mmdrza.Com        -||
#              ||-| Telegram : @PyMmdrza        -||
#              ||-| Github.Com/PyMmdrza         -||
#              ||-| PythonWithMmdrza.Medium.Com -||
#              ||================================||
#              ||================================||
#              ||================================||


import random
import requests
from hdwallet import HDWallet
from hdwallet.symbols import LTC as SYMBOL
from rich import box
from rich.console import Console
from rich.table import Table


def getGenKey():
    e = ""
    for i in range(64):
        k = str(random.choice("0123456789abcdef"))
        e += f"{k}"
    return e


def getBal(address):
    url_link = f"https://litecoin.atomicwallet.io/api/v2/address/{address}"
    r = requests.get(url_link).json()
    return dict(r)['balance']


w = 0
z = 1
while True:

    PRIVATE_KEY: str = getGenKey()
    hdwallet: HDWallet = HDWallet(symbol=SYMBOL)
    hdwallet.from_private_key(private_key=PRIVATE_KEY)
    ltcp2pkh = hdwallet.p2pkh_address()
    ltcp2sh = hdwallet.p2sh_address()
    ltcp2wpkh = hdwallet.p2wpkh_address()
    ltcp2wsh = hdwallet.p2wsh_address()
    ltcp2pkh_bal = getBal(ltcp2pkh)
    ltcp2wpkh_bal = getBal(ltcp2wpkh)
    ltcp2sh_bal = getBal(ltcp2sh)
    ltcp2wsh_bal = getBal(ltcp2wsh)

    row_styles = ["on grey15", "on grey11", "on grey15", "on grey11", "on grey15 red"]
    table = Table(title_style="italic gold1", header_style="italic on dark_green",
                  title="\n\n\nLTC Generator With Balance Checker\n------- Total Scan " + str(z) + " -------",
                  border_style="bright_green",
                  box=box.ROUNDED, show_lines=False, row_styles=row_styles, show_edge=True)

    table.add_column("WiN: " + str(w), justify="right", style="green_yellow bold", no_wrap=True)
    table.add_column("Datails", style="green_yellow", no_wrap=True)
    table.add_column("Balance", style="gold1", no_wrap=True)
    table.add_row(str('LTC-P2PKH'), str(ltcp2pkh), str(ltcp2pkh_bal))
    table.add_row(str('LTC-P2SH'), str(ltcp2sh), str(ltcp2sh_bal))
    table.add_row(str('LTC-P2WPKH'), str(ltcp2wpkh), str(ltcp2wpkh_bal))
    table.add_row(str('LTC-P2WSH'), str(ltcp2wsh), str(ltcp2wsh_bal))
    table.add_row(str('PRIVATE KEY'), str(PRIVATE_KEY), str(z))
    # ============================
    if str(ltcp2pkh_bal) != '0' or str(ltcp2wpkh_bal) != '0' or str(ltcp2sh_bal) != '0' or str(ltcp2wsh_bal) != '0':
        w += 1
        open("Found_Ltc.txt", "a").write(f"{ltcp2pkh} : Balance:{ltcp2pkh_bal}\n"
                                         f"{ltcp2wpkh} : Balance: {ltcp2wpkh_bal}\n"
                                         f"{ltcp2sh} : Balance: {ltcp2sh_bal}\n"
                                         f"{ltcp2wsh} : Balance: {ltcp2wsh_bal}\n"
                                         f"Private Key: {PRIVATE_KEY}\n")
    else:
        console = Console()
        console.print(table)
        z += 1
# ====================================================
