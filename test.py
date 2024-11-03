import json
import http.client
import uuid
import base64

files = []
document_ids = []
metadatas = []
chat_text = "Hello World! with custom boundary."
document_id = str(uuid.uuid4())
document_ids.append(document_id)
metadatas.append({})

# カスタムバウンダリ生成
boundary = f'-----------{uuid.uuid4().hex}'

# JSONデータの準備
json_data = {
    "document_ids": json.dumps(document_ids),
    "metadatas": json.dumps(metadatas)
}

# JSONを文字列へ変換
json_string = json.dumps(json_data)

# ファイルデータの準備（例として）
file_data = chat_text.encode()
files = {
    'file1': (f"{document_id}.txt", file_data)
}

# マルチパートフォームデータの構築
def build_multipart_form_data(json_string, files, boundary) -> str:
    lines = []

    # JSONデータの追加
    lines.append(f'--{boundary}')
    lines.append('Content-Disposition: form-data; name="json_data"')
    lines.append('Content-Type: application/json')
    lines.append('')
    lines.append(json_string)

    # ファイル追加
    for name, (filename, content) in files.items():
        lines.append(f'--{boundary}')
        lines.append(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"')
        lines.append('Content-Type: application/octet-stream')
        lines.append('')
        lines.append(content)

    # 最後にバウンダリを追加
    lines.append(f'--{boundary}--')
    lines.append('')

    # データを結合し、すべての文字列データをバイトにエンコードする
    data = b'\r\n'.join(part.encode('utf-8') if isinstance(part, str) else part for part in lines)
    return base64.b64encode(data).decode('utf-8')

# マルチパートデータを構築
body = build_multipart_form_data(json_string, files, boundary)

payload = {
    "path": "/v2/ingest_files",
    "requestContext": {},
    "httpMethod": "POST",
    "multiValueQueryStringParameters": {},
    "headers": {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsImV4cCI6MTcyOTUzNTkxMC4yNjczMzYsInRva2VuX3R5cGUiOiJhY2Nlc3MifQ.E98hYEpGpCiD0qyhCQ1dEaSw-7L9b7n-UjUNrxXPi24",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    },
    "body": body # byte型をbase64エンコードしてstr型にしている
}

# サーバーへの接続とリクエスト
conn = http.client.HTTPConnection('localhost', 9000)
conn.request('POST', '/2015-03-31/functions/function/invocations', json.dumps(payload), {})

# レスポンスの取得
response = conn.getresponse()
print(response.status, response.reason)
response_data = response.read().decode()
print(response_data)

conn.close()

