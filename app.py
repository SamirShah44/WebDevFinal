from flask import Flask, redirect, url_for, session, render_template_string
from authlib.integrations.flask_client import OAuth
from flask_session import Session
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.config.update({
    "SESSION_TYPE": "filesystem",
    "SESSION_COOKIE_NAME": "auth0_session",
    "SESSION_COOKIE_SAMESITE": "Lax",  # "None" breaks it in non-HTTPS!
    "SESSION_COOKIE_SECURE": False,    # True only for HTTPS!
})
Session(app)

APP_PUBLIC_URL = 'http://34.59.153.155:8000'

oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=os.getenv('AUTH0_CLIENT_ID'),
    client_secret=os.getenv('AUTH0_CLIENT_SECRET'),
    client_kwargs={
        'scope': 'openid profile email',
    },
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)


# HTML template
login_template = """
<!doctype html>
<title>Teen Patti Login</title>
<h2>Welcome to Teen Patti</h2>
<p><a href="{{ url_for('login') }}">Login with Auth0</a></p>
{% if user %}
    <p><strong>Hello {{ user['name'] }}</strong></p>
    <img src="{{ user['picture'] }}" width="100">
    <p><a href="{{ url_for('logout') }}">Logout</a></p>
{% endif %}
<hr>
<pre>Session Debug: {{ session | tojson(indent=2) }}</pre>
"""

@app.route('/')
def home():
    user = session.get('user')
    import json
    return f'''
    <h1>Welcome to Teen Patti</h1>
    <a href="/login">Login with Auth0</a>
    <pre>Session Debug:\n{json.dumps(dict(session), indent=4)}</pre>
    '''
    return render_template_string(login_template, user=user)

@app.route('/login')
def login():
    print("[DEBUG] Starting login...")
    return auth0.authorize_redirect(redirect_uri=os.getenv("AUTH0_CALLBACK_URL"))

@app.route('/callback')
def callback():
    try:
        token = auth0.authorize_access_token()
        print("[DEBUG] Access token:", token)
        resp = auth0.get(f'https://{os.getenv("AUTH0_DOMAIN")}/userinfo')
        userinfo = resp.json()
        session['user'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'email': userinfo['email'],
            'picture': userinfo['picture']
        }
        return redirect('/dashboard')
    except Exception as e:
        print("[ERROR] Callback failed:", e)
        session.clear()
        return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(
        f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?returnTo={APP_PUBLIC_URL}&client_id={os.getenv('AUTH0_CLIENT_ID')}"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

@app.route('/callback')
def callback_handling():
    token = auth0.authorize_access_token()
    userinfo = auth0.get('userinfo').json()
    session['user'] = userinfo
    return redirect('/')

@app.route('/play')
def play():
    if 'user' not in session:
        return redirect('/login')
    return "You are logged in and ready to play Teen Patti!"

app.config.update({
    "SESSION_TYPE": "filesystem",
    "SESSION_COOKIE_NAME": "auth0_session",
    "SESSION_COOKIE_SAMESITE": "Lax",  # If NOT using HTTPS
    "SESSION_COOKIE_SECURE": False,    # If NOT using HTTPS
    "SECRET_KEY": os.getenv("FLASK_SECRET_KEY"),
})

@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    if user:
        return f"""
            Hello {user['name']}!<br>
            <img src="{user['picture']}" alt="Profile Picture"><br>
            <p>Email: {user['email']}</p>
            <a href="/logout">Logout</a>
        """
    return redirect('/')
