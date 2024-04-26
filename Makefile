GOOGLE_CLOUD_PROJECT=youyaku-ai
GOOGLE_REGION=asia-northeast1
DOCKER_BASE_URL=${GOOGLE_REGION}-docker.pkg.dev
DOCKER_URL=${DOCKER_BASE_URL}/${GOOGLE_CLOUD_PROJECT}/line-sakamomo-family-api/api
SERVICE_NAME=line-sakamomo-family-api
LINE_CHANNEL_ACCESS_TOKEN=xxx
LINE_CHANNEL_SECRET=xxx
OPEN_WEATHER_KEY=xxx
OPEN_AI_API_KEY=xxx
GOOGLE_API_KEY=xxx
API_PORT=8080
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=xxx


setup:
	gcloud auth configure-docker ${DOCKER_BASE_URL}

build:
	docker build -t ${DOCKER_URL}:latest .

push_image:
	docker push ${DOCKER_URL}:latest

deploy:
	gcloud run deploy ${SERVICE_NAME} --region ${GOOGLE_REGION} --image ${DOCKER_URL} --update-env-vars LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN},LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET}

deploy_public:
	gcloud run deploy ${SERVICE_NAME} \
		--region ${GOOGLE_REGION} \
		--image ${DOCKER_URL} \
		--update-env-vars LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN},LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET},OPEN_WEATHER_KEY=${OPEN_WEATHER_KEY},OPENAI_API_KEY=${OPENAI_API_KEY},GOOGLE_API_KEY=${GOOGLE_API_KEY},GCP_PROJECT=${GOOGLE_CLOUD_PROJECT},GCP_LOCATION=${GOOGLE_REGION} \
		--update-env-vars LANGCHAIN_ENDPOINT=${LANGCHAIN_ENDPOINT},LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY},LANGCHAIN_TRACING_V2=true\
		--port ${API_PORT} \
		--allow-unauthenticated

delete_run:
	gcloud run services delete ${SERVICE_NAME} --region ${GOOGLE_REGION}
