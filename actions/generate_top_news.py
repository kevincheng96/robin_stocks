import sys
sys.path.insert(1,'/Users/Kevincheng96/Documents/Coding Projects/Python projects/robin_stocks')

from actions.objects import Stock
from concurrent.futures import ThreadPoolExecutor, as_completed
import robin_stocks as r
import heapq
import time

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
	start_time = time.time()
	r.login(username,password)

	# Get list of stocks in watchlist and positions.
	stocks_dict = {}
	watchlist = r.get_watchlist_by_name()
	positions = r.get_current_positions()
	stocks = watchlist + positions

	# Get stock info (e.g. ticker, name) for each stock.
	with ThreadPoolExecutor(max_workers=20) as executor:
		stock_info_futures = [executor.submit(r.request_get, stock['instrument']) for stock in stocks]
	for stock_info_future in as_completed(stock_info_futures):
		stock_info = stock_info_future.result()
		ticker = stock_info['symbol']
		stock = Stock(stock_info['simple_name'], ticker)
		stocks_dict[ticker] = stock
	print("--- %s seconds --- (Got all tickers)" % (time.time() - start_time))

	# Get top news for all stocks (prioritized by num_clicks).
	# TODO: Consider prioritizing by date also.
	news_heap = []
	news_dict = {}
	with ThreadPoolExecutor(max_workers=20) as executor:
		news_futures_to_ticker = {executor.submit(r.get_news, stock.ticker): stock.ticker for stock in stocks_dict.values()}
	for news_future in as_completed(news_futures_to_ticker):
		ticker = news_futures_to_ticker[news_future]
		news = news_future.result()
		if not news:
			continue
		recent_news = news[0]
		# Rank news by views. Need to retain metadata for ticker, source, title, and views.
		num_clicks = recent_news['num_clicks']
		source = recent_news['api_source']
		title = recent_news['title']
		# (-views, ticker, source, title)
		heapq.heappush(news_heap, (-num_clicks, ticker, source, title))
	print("--- %s seconds --- (Got all news)" % (time.time() - start_time))

	# TTS for top news.
	news_aggregate = []
	for news in news_heap[:5]:
		ticker, source, title = news[1], news[2], news[3]
		stock_news_string = "Top news for stock " + stocks_dict[ticker].name + ", "
		news_source_string = "from " + source + ": "
		news_aggregate.append(stock_news_string + news_source_string + title + "\n")
	print("--- %s seconds --- (End)" % (time.time() - start_time))
	return ''.join(news_aggregate)
