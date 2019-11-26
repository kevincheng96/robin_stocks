import robin_stocks as r

from models import store_auth_token

'''
Robinhood includes dividends as part of your net gain. This script removes
dividends from net gain to figure out how much your stocks/options have paid
off.

Note: load_portfolio_profile() contains some other useful breakdowns of equity.
Print profileData and see what other values you can play around with.

'''

#!!! Fill out username and password
username = ''
password = ''
#!!!

# TODO: Calculate total portfolio change. Then largest gainers and losers.

class Stock:
	def __init__(self, name, ticker, news = []):
		self.name = name
		self.ticker = ticker
		self.news = news

	def __str__(self):
		return self.name + " - " + self.ticker

def generate_portfolio_summary():
	r.login(username,password)

	d = r.build_holdings()
	d.update(r.build_user_profile())
	return d
