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

w = 0
z = 1
while True:
	c1 = str(random.choice('0123456789abcdefABCDEF'))
	c2 = str(random.choice('0123456789abcdefABCDEF'))
	c3 = str(random.choice('0123456789abcdefABCDEF'))
	c4 = str(random.choice('0123456789abcdefABCDEF'))
	c5 = str(random.choice('0123456789abcdefABCDEF'))
	c6 = str(random.choice('0123456789abcdefABCDEF'))
	c7 = str(random.choice('0123456789abcdefABCDEF'))
	c8 = str(random.choice('0123456789abcdefABCDEF'))
	c9 = str(random.choice('0123456789abcdefABCDEF'))
	c10 = str(random.choice('0123456789abcdefABCDEF'))
	c11 = str(random.choice('0123456789abcdefABCDEF'))
	c12 = str(random.choice('0123456789abcdefABCDEF'))
	c13 = str(random.choice('0123456789abcdefABCDEF'))
	c14 = str(random.choice('0123456789abcdefABCDEF'))
	c15 = str(random.choice('0123456789abcdefABCDEF'))
	c16 = str(random.choice('0123456789abcdefABCDEF'))
	c17 = str(random.choice('0123456789abcdefABCDEF'))
	c18 = str(random.choice('0123456789abcdefABCDEF'))
	c19 = str(random.choice('0123456789abcdefABCDEF'))
	c20 = str(random.choice('0123456789abcdefABCDEF'))
	c21 = str(random.choice('0123456789abcdefABCDEF'))
	c22 = str(random.choice('0123456789abcdefABCDEF'))
	c23 = str(random.choice('0123456789abcdefABCDEF'))
	c24 = str(random.choice('0123456789abcdefABCDEF'))
	c25 = str(random.choice('0123456789abcdefABCDEF'))
	c26 = str(random.choice('0123456789abcdefABCDEF'))
	c27 = str(random.choice('0123456789abcdefABCDEF'))
	c28 = str(random.choice('0123456789abcdefABCDEF'))
	c29 = str(random.choice('0123456789abcdefABCDEF'))
	c30 = str(random.choice('0123456789abcdefABCDEF'))
	c31 = str(random.choice('0123456789abcdefABCDEF'))
	c32 = str(random.choice('0123456789abcdefABCDEF'))
	c33 = str(random.choice('0123456789abcdefABCDEF'))
	c34 = str(random.choice('0123456789abcdefABCDEF'))
	c35 = str(random.choice('0123456789abcdefABCDEF'))
	c36 = str(random.choice('0123456789abcdefABCDEF'))
	c37 = str(random.choice('0123456789abcdefABCDEF'))
	c38 = str(random.choice('0123456789abcdefABCDEF'))
	c39 = str(random.choice('0123456789abcdefABCDEF'))
	c40 = str(random.choice('0123456789abcdefABCDEF'))
	c41 = str(random.choice('0123456789abcdefABCDEF'))
	c42 = str(random.choice('0123456789abcdefABCDEF'))
	c43 = str(random.choice('0123456789abcdefABCDEF'))
	c44 = str(random.choice('0123456789abcdefABCDEF'))
	c45 = str(random.choice('0123456789abcdefABCDEF'))
	c46 = str(random.choice('0123456789abcdefABCDEF'))
	c47 = str(random.choice('0123456789abcdefABCDEF'))
	c48 = str(random.choice('0123456789abcdefABCDEF'))
	c49 = str(random.choice('0123456789abcdefABCDEF'))
	c50 = str(random.choice('0123456789abcdefABCDEF'))
	c51 = str(random.choice('0123456789abcdefABCDEF'))
	c52 = str(random.choice('0123456789abcdefABCDEF'))
	c53 = str(random.choice('0123456789abcdefABCDEF'))
	c54 = str(random.choice('0123456789abcdefABCDEF'))
	c55 = str(random.choice('0123456789abcdefABCDEF'))
	c56 = str(random.choice('0123456789abcdefABCDEF'))
	c57 = str(random.choice('0123456789abcdefABCDEF'))
	c58 = str(random.choice('0123456789abcdefABCDEF'))
	c59 = str(random.choice('0123456789abcdefABCDEF'))
	c60 = str(random.choice('0123456789abcdefABCDEF'))
	c61 = str(random.choice('0123456789abcdefABCDEF'))
	c62 = str(random.choice('0123456789abcdefABCDEF'))
	c63 = str(random.choice('0123456789abcdefABCDEF'))
	c64 = str(random.choice('0123456789abcdefABCDEF'))
	magic = (
			c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9 + c10 + c11 + c12 + c13 + c14 + c15 + c16 + c17 + c18 + c19 + c20 + c21 + c22 + c23 + c24 + c25 + c26 + c27 + c28 + c29 + c30 + c31 + c32 + c33 + c34 + c35 + c36 + c37 + c38 + c39 + c40 + c41 + c42 + c43 + c44 + c45 + c46 + c47 + c48 + c49 + c50 + c51 + c52 + c53 + c54 + c55 + c56 + c57 + c58 + c59 + c60 + c61 + c62 + c63 + c64)
	PRIVATE_KEY = str(magic)
	hdwallet: HDWallet = HDWallet(symbol=SYMBOL)
	hdwallet.from_private_key(private_key=PRIVATE_KEY)
	addr = hdwallet.p2pkh_address()
	privx = hdwallet.private_key()
	ltcp2pkh = hdwallet.p2pkh_address()
	ltcp2sh = hdwallet.p2sh_address()
	ltcp2wpkh = hdwallet.p2wpkh_address()
	ltcp2wsh = hdwallet.p2wsh_address()
	
	
	def dbal(addr):
		contents = requests.get('http://localhost:5000/balance?active=' + addr, timeout=10)
		res = contents.json()
		balance = dict(res[addr])['final_balance']
		return balance
	
	
	def ltc2sh_bal(ltc2sh):
		contents = requests.get('http://localhost:5000/balance?active=' + ltc2sh, timeout=10)
		res = contents.json()
		balance = dict(res[ltc2sh])['final_balance']
		return balance
	
	
	def ltcp2wpkh_bal(ltcp2wpkh):
		contents = requests.get('http://localhost:5000/balance?active=' + ltcp2wpkh, timeout=10)
		res = contents.json()
		balance = dict(res[ltcp2wpkh])['final_balance']
		return balance
	
	
	def ltcp2wsh_bal(ltcp2wsh):
		contents = requests.get('http://localhost:5000/balance?active=' + ltcp2wsh, timeout=10)
		res = contents.json()
		balance = dict(res[ltcp2wsh])['final_balance']
		return balance
	
	
	row_styles = ["on grey15", "on grey11", "on grey15", "on grey11", "on grey15 red"]
	table = Table(title_style="italic gold1", header_style="italic on dark_green",
	              title="\n\n\nLTC Generator With Balance Checker\n------- Total Scan " + str(z) + " -------",
	              border_style="bright_green",
	              box=box.ROUNDED, show_lines=False, row_styles=row_styles, show_edge=True)
	
	table.add_column("WiN: " + str(w), justify="right", style="green_yellow bold", no_wrap=True)
	table.add_column("Datails", style="green_yellow", no_wrap=True)
	table.add_column("Balance", style="gold1", no_wrap=True)
	table.add_row(str('LTC-P2PKH'), str(addr), str(dbal(addr)))
	table.add_row(str('LTC-P2SH'), str(ltcp2sh), str(ltc2sh_bal(ltcp2sh)))
	table.add_row(str('LTC-P2WPKH'), str(ltcp2wpkh), str(ltcp2wpkh_bal(ltcp2wpkh)))
	table.add_row(str('LTC-P2WSH'), str(ltcp2wsh), str(ltcp2wsh_bal(ltcp2wsh)))
	table.add_row(str('PRIVATE KEY'), str(privx), str(z))
	# ============================
	if int(dbal(addr)) or int(ltc2sh_bal(ltcp2sh)) or int(ltcp2wpkh_bal(ltcp2wpkh)) or int(
			ltcp2wsh_bal(ltcp2wsh)) > 0:
		f = open("LTCWNNERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR.txt", "a")
		f.write("\nADDRESS LTC P2PKH= " + addr
		        + "\nADDRESS LTC P2SH=  " + ltcp2sh
		        + "\nADDRESS LTC P2WSH= " + ltcp2wsh
		        + "\nADDRESS LTC P2WPKH= " + ltcp2wpkh
		        + "\nPRIVATEKEY LTC =" + privx)
		f.close()
		w += 1
	
	else:
		console = Console()
		console.print(table)
		z += 1
# ====================================================
