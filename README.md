# R2R Lambda

## Environments

- Python 3.12

## Requirements

- `requirements.txt`に記述しています

> [!CAUTION]  
> mangum==0.11.0 のバージョンは固定です。これ以上上げると動きません。

## Setup

### 環境変数の設定

- `.env.example`をコピーして`.env`というファイル名で同じ階層に保存してください
- `R2R_PROJECT_NAME`は PostgreSQL のスキーマ名になります
- `OPENAI_API_KEY`には OpenAI の API キーを指定します

### Docker を使わないローカル環境のみ

> [!NOTE]  
> Docker を使わない場合のみ以下のセットアップ作業を行ってください

- 仮想環境を作成する

```bash
python -m venv accelerate-workspace
```

- 仮想環境に入る

```bash
# Windows
.\accelerate-workspace\Scripts\activate

# Mac
. accelerate-workspace/bin/activate
```

- 仮想環境から出る

```bash
deactivate
```

- モジュールのインストール

```bash
pip install -r requirements.txt
```

## Run (ローカル環境)

```bash
make dev
```

## Run (Docker 環境)

```bash
make docker-build
```

```bash
make docker-run
```

## 動作確認

- ローカルの Docker で R2R に対してヘルスチェックを行うリクエスト

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

### モジュールインポート時間の計測

```bash
pip install tuna
```

```bash
python -X importtime test.py 2> prof.txt
```

```bash
tuna prof.txt
```

## AWS ECR にデプロイ

> [!IMPORTANT]
> 以下のコマンドを実行するには aws-cli をインストールし事前のログインが必要です。
> https://zenn.dev/konatsu/articles/5574c1f83757b6

```bash
make build
```

```bash
make deploy
```

- デプロイが完了したら、AWSにログインしてLambdaのイメージを更新してください。

- 画像付きの説明は以下のページをご覧ください。
- [FastAPI (mangum) を AWS Lambda で動かす](https://zenn.dev/alleeks/articles/a286144465cb6b#aws%E3%81%B8%E3%81%AE%E3%83%87%E3%83%97%E3%83%AD%E3%82%A4)
