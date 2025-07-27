// functions/callback.js
// Node 18 以降なら fetch がグローバルにあるため node-fetch は不要
// もし node 16 ランタイムなら node-fetch@2 を require してください。

exports.handler = async (event) => {
  // 1) クエリから code を取得
  const code =
    event.queryStringParameters && event.queryStringParameters.code;

  if (!code) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "code parameter is required" }),
    };
  }

  // 2) 必要であればここで DB などに code を保存する
  // 例:
  // await saveCodeToDynamoDB(code);

  // 3) code をそのまま JSON で返す
  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  };
};

/* --- CLI からテスト実行できるスニペット（任意）--- */
if (require.main === module) {
  const code = process.argv[2];
  if (!code) {
    console.error("Usage: node callback.js <code>");
    process.exit(1);
  }
  console.log(JSON.stringify({ code }));
}