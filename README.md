# R2R Lambda Only

## Environments
- Python 3.12

## Requirements

- `requirements.txt`に記述しています

> [!CAUTION]  
> mangum==0.11.0のバージョンは固定です。これ以上上げると動きません。

## Setup

###  環境変数の設定

- `.env.example`をコピーして`.env`というファイル名で同じ階層に保存してください
- `R2R_PROJECT_NAME`はPostgreSQLのスキーマ名になります
- `OPENAI_API_KEY`にはOpenAIのAPIキーを指定します

### Dockerを使わないローカル環境のみ
> [!NOTE]  
> Dockerを使わない場合のみ以下のセットアップ作業を行ってください

- 仮想環境を作成する

```bash
python -m venv accelerate-workspace
```

- 仮想環境に入る

```bash
# Windows
.\accelerate-workspace\Scripts\activate

# Mac
. accelerate-worksprace/bin/activate
```

- モジュールのインストール

```bash
pip install -r requirements.txt
```

## Run (ローカル環境)

```bash
make dev
```

## Run (Docker環境)
```bash
make docker-build
```

```bash
make docker-run
```

## 動作確認

- R2Rのヘルスチェックを行うリクエスト

```bash
curl -X "POST" "http://localhost:9000/2015-03-31/functions/function/invocations" \
-H 'Content-Type: application/json; charset=utf-8' \
-d $'{
  "path": "/v2/health",
  "requestContext": {},
  "httpMethod": "GET",
  "multiValueQueryStringParameters": {}
}'
```

- レスポンス

```bash
{"isBase64Encoded": false, "statusCode": 200, "headers": {"content-length": "18", "content-type": "application/json"}, "body": "{\"message\":\"test\"}"}
```


## リファレンス
- [FastAPI (mangum) を AWS Lambda で動かす](https://zenn.dev/alleeks/articles/a286144465cb6b)