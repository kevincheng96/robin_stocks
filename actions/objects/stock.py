class Stock:
	def __init__(self, name, ticker, news = []):
		self.name = name
		self.ticker = ticker
		self.news = news

	def __str__(self):
		return self.name + " - " + self.ticker