FROM public.ecr.aws/lambda/python:3.12

# AWS Lambda Web Adapter
# COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/lambda-adapter

WORKDIR ${LAMBDA_TASK_ROOT}

# ファイルのコピー
COPY requirements.txt ./
COPY r2r.toml ./
COPY pyproject.toml ./
COPY core/ ./core/
COPY shared/ ./shared/

# タイムゾーンの設定
RUN ln -sf  /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# パッケージインストール
RUN pip install -r requirements.txt

# ENTRYPOINT ["/bin/sh", "-c", "while :; do sleep 200; done"]
# CMD ["core.main.app_entry:app", "--host", "0.0.0.0", "--port", "8080"]
CMD ["core.main.app_entry.handler"]