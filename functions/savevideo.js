const fs   = require("fs").promises;
const path = require("path");

exports.handler = async (event) => {
  // 1. POST 以外は受け付けない
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  // 2. 送られてきた JSON を読み取る
  const { password, video } = JSON.parse(event.body);

  // 3. 環境変数で設定したパスワードと比較
  if (password !== process.env.ADMIN_PASS) {
    return { statusCode: 401, body: "Unauthorized" };
  }

  // 4. public/videos.json を読み込んで、該当レコードを更新
  const filePath = path.join(__dirname, "../public/videos.json");
  const raw      = await fs.readFile(filePath, "utf8");
  const data     = JSON.parse(raw);

  const idx = data.findIndex(v => v.id === video.id);
  if (idx !== -1) data[idx] = video;

  // 5. 更新後の JSON をファイルへ書き込み
  await fs.writeFile(filePath, JSON.stringify(data, null, 2), "utf8");

  return { statusCode: 200, body: "OK" };
};