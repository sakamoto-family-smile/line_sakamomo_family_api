GOOGLE_CLOUD_PROJECT=youyaku-ai # 将来的には変更したい
DOCKER_BASE_URL=asia-northeast1-docker.pkg.dev
DOCKER_URL=${DOCKER_BASE_URL}/${GOOGLE_CLOUD_PROJECT}/line-sakamomo-family-api
SERVICE_NAME=line-sakamomo-family-api
LINE_CHANNEL_ACCESS_TOKEN=xxx
LINE_CHANNEL_SECRET=xxx


setup:
	gcloud auth configure-docker ${DOCKER_BASE_URL}

build:
	docker build -t ${DOCKER_URL}:latest .

push_image:
	docker push ${DOCKER_BASE_URL}:latest

deploy:
	gcloud run deploy ${SERVICE_NAME} --image ${DOCKER_URL} --update-env-vars LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN},LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET}
