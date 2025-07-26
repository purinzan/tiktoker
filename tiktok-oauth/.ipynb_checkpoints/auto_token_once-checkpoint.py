import http.server
import socketserver
import threading
import webbrowser
import urllib.parse
import requests
import json
import os
from dotenv import load_dotenv

#── 設定セクション ──────────────────────────────────────

# .env を使う場合はプロジェクト直下に .env を置き、load_dotenv() を有効に
load_dotenv()
CLIENT_KEY    = os.getenv("CLIENT_KEY")    # または直書き "sbawd6f9kgtu4fstl5"
CLIENT_SECRET = os.getenv("CLIENT_SECRET") # または直書き "YOUR_CLIENT_SECRET"
REDIRECT_URI  = os.getenv("REDIRECT_URI")  # "http://localhost:8765/callback"
SCOPES        = ["user.info.basic"]

# REDIRECT_URI からポート番号を取得
parsed = urllib.parse.urlparse(REDIRECT_URI)
PORT = parsed.port or 8765

if not CLIENT_KEY or not CLIENT_SECRET or not REDIRECT_URI:
    raise RuntimeError("CLIENT_KEY, CLIENT_SECRET, REDIRECT_URI を .env か直書きで設定してください")

#── HTTP サーバー定義 ────────────────────────────────────

code_value = None

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global code_value
        u = urllib.parse.urlparse(self.path)
        if u.path != "/callback":
            self.send_error(404, "Not found")
            return
        params = urllib.parse.parse_qs(u.query)
        code_value = params.get("code", [None])[0]
        if not code_value:
            self.send_error(400, "code parameter is required")
            return

        # レスポンス
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<h2>認証完了しました。ターミナルを確認してください。</h2>")

        # サーバーシャットダウンを別スレッドで
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    # ログを抑制
    def log_message(self, format, *args):
        return


#── 認可 URL を開く ──────────────────────────────────────

def open_authorize_url():
    params = {
        "client_key":    CLIENT_KEY,
        "redirect_uri":  REDIRECT_URI,
        "response_type": "code",
        "scope":         " ".join(SCOPES),
        "state":         "local"
    }
    url = "https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode(params)
    print("ブラウザを開きます。TikTok でログイン＆許可を押してください…")
    webbrowser.open(url, new=1)


#── メインフロー ────────────────────────────────────────

def main():
    # 1) ローカルサーバー起動
    with socketserver.TCPServer(("localhost", PORT), CallbackHandler) as httpd:
        threading.Thread(target=open_authorize_url, daemon=True).start()
        print(f"Listening on http://localhost:{PORT}/callback …")
        httpd.serve_forever()

    # 2) code の取得待ち
    if not code_value:
        print("認可コードを取得できませんでした。")
        return
    print("取得した code:", code_value)

    # 3) code → token 交換
    resp = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data={
            "client_key":    CLIENT_KEY,
            "client_secret": CLIENT_SECRET,
            "code":          code_value,
            "grant_type":    "authorization_code",
            "redirect_uri":  REDIRECT_URI
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15
    )
    token_json = resp.json()
    if resp.status_code != 200:
        print("トークン取得に失敗:", token_json)
        return

    # 4) tokens.json に保存
    with open("tokens.json", "w", encoding="utf-8") as f:
        json.dump(token_json, f, ensure_ascii=False, indent=2)
    print("トークンを tokens.json に保存しました。内容:")
    print(json.dumps(token_json, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()