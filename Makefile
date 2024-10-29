dev:
	uvicorn src.main.app_entry:app --env-file .env --port 3000

dev-ingestion:
	uvicorn lambda_functions.ingestion.core.main.app_entry:app --env-file .env --port 3000

docker-build:
	docker build -t accelerate/r2r-lambda -f Dockerfile.dev .

docker-run:
	docker run --env-file .env -p 9000:8080 accelerate/r2r-lambda

deploy:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 548557419475.dkr.ecr.ap-northeast-1.amazonaws.com
	docker tag accelerate/r2r-lambda:latest 548557419475.dkr.ecr.ap-northeast-1.amazonaws.com/accelerate/r2r-lambda:latest
	docker push 548557419475.dkr.ecr.ap-northeast-1.amazonaws.com/accelerate/r2r-lambda:latest