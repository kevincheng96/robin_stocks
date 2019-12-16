import os
import sys
project_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, project_dir)

from flask import Flask
from flask_assistant import Assistant, ask, tell
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
assist = Assistant(app, route='/')

# Set up SQLite DB.
db_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(db_dir, "auth_token.db"))
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Import these only after db is instantiated.
from actions import generate_portfolio_summary
from actions import generate_top_news

@app.route('/')
def index():
	# return generate_portfolio_summary()
	return generate_top_news()

@assist.action('get-market-news')
def get_top_news():
	# TODO: Optimize this call since it breaches the 5 second timeout for AoG.
	# TODO: Run Cron job to cache DB with top news for each stock to reduce latency.
    return tell(generate_top_news())

@assist.action('generate-portfolio-summary')
def get_portfolio_summary():
	# TODO: Create a JSON to text (speech) generator.
	return tell(generate_portfolio_summary())

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(host='0.0.0.0', threaded=True, debug=True)
    