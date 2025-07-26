// callback.js

// デバッグ用：起動時に環境変数の中身をログに出す
console.log("▶ CLIENT_KEY:", process.env.CLIENT_KEY);

exports.handler = async (event) => {
  if (!process.env.CLIENT_KEY) {
    console.error("ERROR: CLIENT_KEY が設定されていません！"); 
    return {
      statusCode: 500,
      body: "Server Error: Missing CLIENT_KEY",
    };
  }

  // 以降は process.env.CLIENT_KEY を使ってリクエストを組み立てる…
};

const fetch = require("node-fetch");

exports.handler = async (event, context) => {
  try {
    // 1) code をクエリパラメータから取得
    const code = event.queryStringParameters && event.queryStringParameters.code;
    if (!code) {
      return { statusCode: 400, body: JSON.stringify({ error: "code parameter is required" }) };
    }

    // 2) TikTok へ token 交換リクエスト
    const params = new URLSearchParams({
      client_key:    process.env.CLIENT_KEY,
      client_secret: process.env.CLIENT_SECRET,
      code:          code,
      grant_type:    "authorization_code",
      redirect_uri:  process.env.REDIRECT_URI
    });
    const tokenRes = await fetch("https://open.tiktokapis.com/v2/oauth/token/", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: params
    });

    if (!tokenRes.ok) {
      const errText = await tokenRes.text();
      return { statusCode: tokenRes.status, body: JSON.stringify({ error: errText }) };
    }

    const tokenJson = await tokenRes.json();

    // 3) 必要ならデータベース保存などの処理をここで入れる

    // 4) レスポンスとして token を返却
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tokenJson)
    };

  } catch (e) {
    return { statusCode: 500, body: JSON.stringify({ error: e.message }) };
  }
};