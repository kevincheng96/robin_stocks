import sys
sys.path.insert(1,'/Users/Kevincheng96/Documents/Coding Projects/Python projects/robin_stocks')

from actions.objects import Stock
import robin_stocks as r
import heapq

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

def generate_top_news():
	r.login(username,password)

	# Get list of stocks in watchlist and positions.
	stocks_dict = {}
	watchlist = r.get_watchlist_by_name()
	for element in watchlist:
		instrument = element['instrument']
		stock_info = r.request_get(instrument)
		ticker = stock_info['symbol']
		stock = Stock(stock_info['simple_name'], ticker)
		stocks_dict[ticker] = stock
	positions = r.get_current_positions()
	for position in positions:
		instrument = position['instrument']
		ticker = stock_info['symbol']
		stock = Stock(stock_info['simple_name'], ticker)
		stocks_dict[ticker] = stock
	for stock in stocks_dict.values():
		print(stock)

	# Get top news for all stocks (prioritized by num_clicks).
	# TODO: Consider prioritizing by date also.
	news_heap = []
	for stock in stocks_dict.values():
		news = r.get_news(stock.ticker)
		if not news:
			continue
		recent_news = news[0]
		# Rank news by views. Need to retain metadata for ticker, source, title, and views.
		num_clicks = recent_news['num_clicks']
		source = recent_news['api_source']
		title = recent_news['title']
		# (-views, ticker, source, title)
		heapq.heappush(news_heap, (-num_clicks, stock.ticker, source, title))

	# TTS for top news.
	news_aggregate = []
	for news in news_heap[:5]:
		ticker, source, title = news[1], news[2], news[3]
		stock_news_string = "Top news for stock " + stocks_dict[ticker].name
		news_source_string = "From source, " + source
		news_aggregate.append(stock_news_string + "\n" + news_source_string + "\n" + title)
	return ''.join(news_aggregate)
