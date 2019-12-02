import robin_stocks as r

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

def generate_portfolio_summary():
	r.login(username,password)

	d = r.build_holdings()
	d.update(r.build_user_profile())
	return d
