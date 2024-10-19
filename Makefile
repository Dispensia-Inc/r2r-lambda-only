dev:
	uvicorn core.main.app_entry:app --env-file .env --port 3000
docker-build:
	docker build -t r2r-lambda-only -f Dockerfile.dev .
docker-run:
	docker run --env-file .env -p 9000:8080 r2r-lambda-only