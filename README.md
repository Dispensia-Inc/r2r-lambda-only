# R2R Lambda

## 起動時間

- lambda-auth
  - コールドスタート状態：5500ms
  - ウォームスタート状態：130ms

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

## 実行

### Auth Worker

- ビルド

```bash
make docker-compose-build-auth
```

> [!IMPORTANT]
> 前回ビルドしたイメージが上書きされるわけではなく、ビルドごとに蓄積されていくため、不要なイメージは定期的に削除することをおすすめします。

- 起動

```bash
make docker-run-auth
```

## 動作確認

- ローカルの Docker で R2R に対してヘルスチェックを行うリクエスト

```bash
curl -X "POST" "http://localhost:7272/health"
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

- デプロイが完了したら、AWS にログインして Lambda のイメージを更新してください。

- 画像付きの説明は以下のページをご覧ください。
- [FastAPI (mangum) を AWS Lambda で動かす](https://zenn.dev/alleeks/articles/a286144465cb6b#aws%E3%81%B8%E3%81%AE%E3%83%87%E3%83%97%E3%83%AD%E3%82%A4)

## 一時的な認証情報の取得

- ローカルでの開発時では Cognito にアクセスするために一時的な認証情報が必要になります。
- 一時的な認証情報は発行してから 12 時間が経過すると失効するため、その際には再度発行が必要になります。
- 以下のコマンドで発行してください。

```bash
aws sts get-session-token --profile developer
```

- 出力された結果を環境変数に設定してください。

```bash
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```

> [!WARNING]
> 以下は必要ないかも

- ローカルでの開発時では Cognito にアクセスするために一時的な認証情報が必要になります。
- 一時的な認証情報は発行してから 12 時間が経過すると失効するため、その際には再度発行が必要になります。
- まだ aws-cli に developer アカウントを登録していない場合は次のコマンド（`aws configure --profile developer`）で登録してください。（登録情報は git 管理できないためテキストでお渡しします。）

```bash
aws sts assume-role --role-arn arn:aws:iam::548557419475:role/accelerate-r2r-lambda --profile developer --role-session-name "RoleSession1" > assume-role-output.txt
```
