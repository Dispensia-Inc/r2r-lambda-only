dev:
	uvicorn src.main.app_entry:app --env-file .env --port 3000

dev-ingestion:
	uvicorn lambda_functions.ingestion.core.main.app_entry:app --env-file .env --port 3000

docker-compose-build:
	docker compose -f ./docker/docker-compose.${WORKER_NAME}.yml -p ${WORKER_NAME}-worker build

docker-run:
	docker compose -f ./docker/docker-compose.${WORKER_NAME}.yml -p ${WORKER_NAME}-worker up -d

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
