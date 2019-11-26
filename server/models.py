from server import db

class AuthToken(db.Model):
    username = db.Column(db.String(50), unique=True, nullable=False, primary_key=True)
    token_type = db.Column(db.String(100), unique=True, nullable=False)
    access_token = db.Column(db.String(100), unique=True, nullable=False)
    refresh_token = db.Column(db.String(100), unique=True, nullable=False)
    device_token = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return "<Username: {0}, Token Type: {1}>".format(self.username, self.token_type)

def store_auth_token(username, login_data):
	username = username.lower()
	auth_token = AuthToken(
		username = username, 
		token_type = login_data['token_type'], 
		access_token = login_data['access_token'], 
		refresh_token = login_data['refresh_token'], 
		device_token = login_data['refresh_token'])
	db.session.merge(auth_token)
	db.session.commit()