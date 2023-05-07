helm plugin install https://github.com/hayorov/helm-gcs.git --version 0.4.0
helm plugin update gcs
cp -rf /root/.config ${HOME}/.config
echo $GCLOUD_KEY > ${HOME}/.config/gcloud/application_default_credentials.json
gcloud auth activate-service-account --key-file ${HOME}/.config/gcloud/application_default_credentials.json
gcloud config set core/project  $PROJECT_ID --quiet
helm repo add gcs-repo gs://chart-museum-007/charts
gcloud auth configure-docker --quiet
gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://gcr.io
