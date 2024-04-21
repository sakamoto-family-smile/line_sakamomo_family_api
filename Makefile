GOOGLE_CLOUD_PROJECT=youyaku-ai
GOOGLE_REGION=asia-northeast1
DOCKER_BASE_URL=${GOOGLE_REGION}-docker.pkg.dev
DOCKER_URL=${DOCKER_BASE_URL}/${GOOGLE_CLOUD_PROJECT}/line-sakamomo-family-api/api
SERVICE_NAME=line-sakamomo-family-api
LINE_CHANNEL_ACCESS_TOKEN=xxx
LINE_CHANNEL_SECRET=xxx
OPEN_WEATHER_KEY=xxx
API_PORT=8080


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
		--update-env-vars LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN},LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET} \
		--port ${API_PORT} \
		--allow-unauthenticated

delete_run:
	gcloud run services delete ${SERVICE_NAME} --region ${GOOGLE_REGION}
