"""Contains all functions for the purpose of logging in and out to Robinhood."""
import robin_stocks.urls as urls
import robin_stocks.helper as helper
import random
import os
from getpass import getpass

from models import AuthToken, store_auth_token
from server import db

def generate_device_token():
    """This function will generate a token used when loggin on.

    :returns: A string representing the token.

    """
    rands = []
    for i in range(0,16):
        r = random.random()
        rand = 4294967296.0 * r
        rands.append((int(rand) >> ((3 & i) << 3)) & 255)

    hexa = []
    for i in range(0,256):
        hexa.append(str(hex(i+256)).lstrip("0x").rstrip("L")[1:])

    id = ""
    for i in range(0,16):
        id += hexa[rands[i]]

        if (i == 3) or (i == 5) or (i == 7) or (i == 9):
            id += "-"

    return(id)

def respond_to_challenge(challenge_id, sms_code):
    """This functino will post to the challenge url.

    :param challenge_id: The challenge id.
    :type challenge_id: str
    :param sms_code: The sms code.
    :type sms_code: str
    :returns:  The response from requests.

    """
    url = urls.challenge_url(challenge_id)
    payload = {
        'response': sms_code
    }
    return(helper.request_post(url,payload))

def login(username,password,expiresIn=86400,scope='internal',by_sms=True,store_session=True):
    """This function will effectivly log the user into robinhood by getting an
    authentication token and saving it to the session header. By default, it will store the authentication
    token in SQLite and load that value on subsequent logins.

    :param username: The username for your robinhood account. Usually your email.
    :type username: str
    :param password: The password for your robinhood account.
    :type password: str
    :param expiresIn: The time until your login session expires. This is in seconds.
    :type expiresIn: Optional[int]
    :param scope: Specifies the scope of the authentication.
    :type scope: Optional[str]
    :param by_sms: Specifies whether to send an email(False) or an sms(True)
    :type by_sms: Optional[boolean]
    :param store_session: Specifies whether to save the log in authorization for future log ins.
    :type store_session: Optional[boolean]
    :returns:  A dictionary with log in information. The 'access_token' keyword contains the access token, and the 'detail' keyword \
    contains information on whether the access token was generated or loaded from SQLite.

    """
    username = username.lower()
    device_token = generate_device_token()
    # Challenge type is used if not logging in with two-factor authentication.
    if by_sms:
        challenge_type = "sms"
    else:
        challenge_type = "email"

    url = urls.login_url()
    payload = {
    'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
    'expires_in': expiresIn,
    'grant_type': 'password',
    'password': password,
    'scope': scope,
    'username': username,
    'challenge_type': challenge_type,
    'device_token': device_token
    }
    auth_token = AuthToken.query.filter_by(username=username).first()
    if auth_token:
        # If store_session has been set to false then delete the SQLite entry, otherwise try to load it.
        # Loading from SQLite will fail if the access_token has expired.
        if store_session:
            try:
                access_token = auth_token.access_token
                token_type = auth_token.token_type
                refresh_token = auth_token.refresh_token
                # Set device_token auth_token be the original device token when first logged in.
                stored_device_token = auth_token.device_token
                payload['device_token'] = stored_device_token
                # Set login status to True in order to try and get account info.
                helper.set_login_state(True)
                helper.update_session('Authorization','{0} {1}'.format(token_type, access_token))
                # Try to load account profile to check that authorization token is still valid.
                res = helper.request_get(urls.portfolio_profile(),'regular',payload,jsonify_data=False)
                # Raises exception if response code is not 200.
                res.raise_for_status()
                return({'access_token': access_token,'token_type': token_type,
                'expires_in': expiresIn, 'scope': scope, 'detail': 'logged in using authentication in SQLite',
                'backup_code': None, 'refresh_token': refresh_token})
            except:
                print("ERROR: There was an issue loading data from SQLite. Authentication may be expired - logging in normally.")
                helper.set_login_state(False)
                helper.update_session('Authorization',None)
        else:
            # Delete auth token entry from SQLite.
            auth_token.delete()
            db.session.commit()
            pass
    # Try to log in normally.
    if not username:
        username = input("Please enter your username: ")
        payload['username'] = username
    if not password:
        password = getpass(prompt="Please enter your password: ")
        payload['password'] = password
        payload['device_token'] = device_token
    data = helper.request_post(url,payload)
    # Handle case where mfa or challenge is required.
    if 'mfa_required' in data:
        mfa_token = input("Please type in the MFA code: ")
        payload['mfa_code'] = mfa_token
        res = helper.request_post(url,payload,jsonify_data=False)
        while (res.status_code != 200):
            mfa_token = input("That MFA code was not correct. Please type in another MFA code: ")
            payload['mfa_code'] = mfa_token
            res = helper.request_post(url,payload,jsonify_data=False)
        data = res.json()
    elif 'challenge' in data:
        challenge_id = data['challenge']['id']
        sms_code = input('Enter Robinhood code for validation: ')
        res = respond_to_challenge(challenge_id, sms_code)
        while 'challenge' in res and res['challenge']['remaining_attempts'] > 0:
            sms_code = input('That code was not correct. {0} tries remaining. Please type in another code: '.format(res['challenge']['remaining_attempts']))
            res = respond_to_challenge(challenge_id, sms_code)
        helper.update_session('X-ROBINHOOD-CHALLENGE-RESPONSE-ID', challenge_id)
        data = helper.request_post(url,payload)
    # Update Session data with authorization or raise exception with the information present in data.
    if 'access_token' in data:
        token = '{0} {1}'.format(data['token_type'],data['access_token'])
        helper.update_session('Authorization',token)
        helper.set_login_state(True)
        data['detail'] = "logged in with brand new authentication code."
        # Store the new auth token in DB.
        store_auth_token(username, data)
    else:
        raise Exception(data['detail'])
    return(data)

@helper.login_required
def logout():
    """Removes authorization from the session header.

    :returns: None

    """
    helper.set_login_state(False)
    helper.update_session('Authorization',None)
