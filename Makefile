dev:
	uvicorn src.main.app_entry:app --env-file .env --port 3000

dev-ingestion:
	uvicorn lambda_functions.ingestion.core.main.app_entry:app --env-file .env --port 3000



docker-build:
	docker build --platform linux/arm64 -t accelerate/r2r-lambda -f Dockerfile.dev .

docker-build-ingestion:
	docker build --platform linux/arm64 -t accelerate/r2r-lambda-ingestion -f Dockerfile.ingestion .

docker-build-auth:
	docker build --platform linux/arm64 -t r2r-lambda-auth -f ./docker/Dockerfile.auth .



docker-compose-build-auth:
	docker compose -f ./docker/docker-compose.auth.yml -p auth-worker build

docker-compose-build-retrieval:
	docker compose -f ./docker/docker-compose.retrieval.yml -p retrieval-worker build



docker-run:
	docker run --env-file .env -p 9000:8080 accelerate/r2r-lambda

docker-run-ingestion:
	docker compose -f ./docker/docker-compose.ingestion.yml -p ingestion-worker up -d

docker-run-auth:
	docker compose -f ./docker/docker-compose.auth.yml -p auth-worker up -d

docker-run-retrieval:
	docker compose -f ./docker/docker-compose.retrieval.yml -p retrieval-worker up -d



deploy:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 548557419475.dkr.ecr.ap-northeast-1.amazonaws.com
	docker tag accelerate/r2r-lambda:latest 548557419475.dkr.ecr.ap-northeast-1.amazonaws.com/accelerate/r2r-lambda:latest
	docker push 548557419475.dkr.ecr.ap-northeast-1.amazonaws.com/accelerate/r2r-lambda:latest

deploy-ingestion:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 548557419475.dkr.ecr.ap-northeast-1.amazonaws.com
	docker tag accelerate/r2r-lambda-ingestion:latest 548557419475.dkr.ecr.ap-northeast-1.amazonaws.com/accelerate/r2r-lambda-ingestion:latest
	docker push 548557419475.dkr.ecr.ap-northeast-1.amazonaws.com/accelerate/r2r-lambda-ingestion:latest

deploy-auth:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 548557419475.dkr.ecr.ap-northeast-1.amazonaws.com
	docker build --platform linux/arm64 -t r2r-lambda-auth -f ./docker/Dockerfile.auth .
	docker tag r2r-lambda-auth:latest 548557419475.dkr.ecr.ap-northeast-1.amazonaws.com/r2r-lambda-auth:latest
	docker push 548557419475.dkr.ecr.ap-northeast-1.amazonaws.com/r2r-lambda-auth:latest

deploy-retrieval-search:
