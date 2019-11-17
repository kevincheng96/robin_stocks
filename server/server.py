import sys
sys.path.insert(1,'/Users/Kevincheng96/Documents/Coding Projects/Python projects/examples')
sys.path.insert(2,'/Users/Kevincheng96/Documents/Coding Projects/Python projects/robin_stocks')

from flask import Flask
from flask_assistant import Assistant, ask, tell

from actions import generate_portfolio_summary
from actions import generate_top_news

app = Flask(__name__)
assist = Assistant(app, route='/')

@app.route('/')
def index():
	return generate_top_news()

@assist.action('get-market-news')
def get_top_news():
	# TODO: Optimize this call since it breaches the 5 second timeout for AoG.
    return tell(generate_top_news())

@assist.action('generate-portfolio-summary')
def get_portfolio_summary():
	# TODO: Create a JSON to text (speech) generator.
	return tell(generate_portfolio_summary())

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, debug=True)