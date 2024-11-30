GOOGLE_REGION=asia-northeast1
DOCKER_BASE_URL=${GOOGLE_REGION}-docker.pkg.dev
DOCKER_URL=${DOCKER_BASE_URL}/${GOOGLE_CLOUD_PROJECT}/line-sakamomo-family-api/api
SERVICE_NAME=line-sakamomo-family-api
API_PORT=8080
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

include .env
setup:
	gcloud auth configure-docker ${DOCKER_BASE_URL}

build:
	docker build -t ${DOCKER_URL}:latest .

push_image:
	docker push ${DOCKER_URL}:latest

deploy_api:
	gcloud run deploy ${SERVICE_NAME} \
		--region ${GOOGLE_REGION} \
		--image ${DOCKER_URL} \
		--update-env-vars LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN},LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET},OPEN_WEATHER_KEY=${OPEN_WEATHER_KEY},OPENAI_API_KEY=${OPENAI_API_KEY},GCP_PROJECT=${GOOGLE_CLOUD_PROJECT},GCP_LOCATION=${GOOGLE_REGION} \
		--update-env-vars LANGCHAIN_ENDPOINT=${LANGCHAIN_ENDPOINT},LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY},LANGCHAIN_TRACING_V2=true \
		--update-env-vars GOOGLE_API_KEY=${GOOGLE_API_KEY},GOOGLE_CSE_ID=${GOOGLE_CSE_ID} \
		--update-env-vars EDINET_API_KEY=${EDINET_API_KEY} \
		--port ${API_PORT}

deploy_public_api:
	gcloud run deploy ${SERVICE_NAME} \
		--region ${GOOGLE_REGION} \
		--image ${DOCKER_URL} \
		--update-env-vars LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN},LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET},OPEN_WEATHER_KEY=${OPEN_WEATHER_KEY},OPENAI_API_KEY=${OPENAI_API_KEY},GCP_PROJECT=${GOOGLE_CLOUD_PROJECT},GCP_LOCATION=${GOOGLE_REGION} \
		--update-env-vars LANGCHAIN_ENDPOINT=${LANGCHAIN_ENDPOINT},LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY},LANGCHAIN_TRACING_V2=true \
		--update-env-vars GOOGLE_API_KEY=${GOOGLE_API_KEY},GOOGLE_CSE_ID=${GOOGLE_CSE_ID} \
		--update-env-vars EDINET_API_KEY=${EDINET_API_KEY} \
		--port ${API_PORT} \
		--allow-unauthenticated

all_process:
	make build
	make push_image
	make deploy_api

delete_run:
	gcloud run services delete ${SERVICE_NAME} --region ${GOOGLE_REGION}

lint:
	pysen run lint

format:
	pysen run format

debug_line_request:
	curl -X POST https://line-sakamomo-family-api-m544onxfdq-an.a.run.app/line_callback -H "x-line-signature:hoge" --data "data=hoge"
