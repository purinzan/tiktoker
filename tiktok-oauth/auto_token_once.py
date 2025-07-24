import threading, webbrowser, urllib.parse
from flask import Flask, request
import requests, json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
CLIENT_KEY    = os.getenv("CLIENT_KEY")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI  = os.getenv("REDIRECT_URI")
SCOPES        = ["user.info.basic"]
PORT          = int(urllib.parse.urlparse(REDIRECT_URI).port or 8765)

# Initialize Flask app and global storage for code
app = Flask(__name__)
code_value = None

@app.route('/callback')
def callback():
    global code_value
    code_value = request.args.get('code')
    # Shut down the Flask development server gracefully
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if shutdown:
        shutdown()
    return '<h2>認証完了。ターミナルを確認してください。</h2>'

if __name__ == '__main__':
    # Start Flask server in a background thread
    server = threading.Thread(
        target=lambda: app.run(host='localhost', port=PORT, debug=False, use_reloader=False),
        daemon=True
    )
    server.start()

    # Open the browser for user consent
    params = {
        'client_key':    CLIENT_KEY,
        'redirect_uri':  REDIRECT_URI,
        'response_type': 'code',
        'scope':         ' '.join(SCOPES),
        'state':         'local'
    }
    auth_url = 'https://www.tiktok.com/v2/auth/authorize/?' + urllib.parse.urlencode(params)
    print('Opening browser for consent...')
    webbrowser.open(auth_url, new=1)

    # Wait for the callback to store the code
    print('Waiting for authorization code...')
    while code_value is None:
        pass

    # Exchange code for access token
    token_resp = requests.post(
        'https://open.tiktokapis.com/v2/oauth/token/',
        data={
            'client_key':    CLIENT_KEY,
            'client_secret': CLIENT_SECRET,
            'code':          code_value,
            'grant_type':    'authorization_code',
            'redirect_uri':  REDIRECT_URI
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=15
    ).json()

    # Save tokens to JSON file
    with open('tokens.json', 'w', encoding='utf-8') as f:
        json.dump(token_resp, f, ensure_ascii=False, indent=2)

    print('Tokens saved to tokens.json')
