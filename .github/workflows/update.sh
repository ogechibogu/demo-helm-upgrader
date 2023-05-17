echo "lets do this shiiii"
: '
CHARTS=$(ls -d */ | sed 's|/||')
for C in $CHARTS;do
   echo "checking $C for updates" 
   VENDOR_REPO_NAME=$(yq -e .repo.name ${C}/mirror.yaml)
   VENDOR_REPO=$(yq -e .repo.repository ${C}/mirror.yaml)
   helm repo add ${VENDOR_REPO_NAME} ${VENDOR_REPO}
   CHART_VERSION=$(yq -e .version ${C}/mirror.yaml)
   VENDOR_VERSION=$(helm search repo ${VENDOR_REPO_NAME}/${C} -o yaml | yq -r '.[].version')
            
   if [ $CHART_VERSION == $VENDOR_VERSION ];then
      echo " $C chart is up to date" 
   else
      echo " updating $C from version $CHART_VERSION to version $VENDOR_VERSION"
      if [ -d "temp" ]; then
         echo "Deleting existing temp folder..."
         rm -rf temp
       fi
       mkdir temp && cd temp
       helm pull ${VENDOR_REPO_NAME}/${C} --untar
              
       if [ -f "../$C/modify.sh" ]; then
          echo "Running modify.sh..."
        fi
              
        DOCKER_IMAGES=$(helm template $C |grep image: | sed 's/image://' | sed 's/^[[:space:]]*//')
        docker pull $DOCKER_IMAGES
        IMAGE_NAME=$(echo $DOCKER_IMAGES | sed 's|docker.io/||' | awk -F: '{print $1}')
        TAG=$(echo $DOCKER_IMAGES | awk -F: '{print $2}')
              
        docker tag $IMAGE_NAME:$TAG $GCR/$IMAGE_NAME:$TAG
        docker push $GCR/$IMAGE_NAME:$TAG
        DIGEST=$(gcloud container images describe $GCR/$IMAGE_NAME:$TAG | yq -e .image_summary.digest -)
              
        echo "checking something"
        REPLACE_KEY=$(yq e -o=json $C/values.yaml | jq -r --arg TAG "$TAG" 'paths as $p | select(getpath($p) == $TAG) | $p | map(if type=="number" then "["+tostring+"]" else tostring end) | join(".")' | sed 's/.tag//g')
        echo $REPLACE_KEY
              
              
        yq e ".$REPLACE_KEY.digest = \"$DIGEST\"" -i $C/values.yaml
                
        docker image rm $IMAGE_NAME:$TAG
        docker image rm $GCR/$IMAGE_NAME:$TAG
            
        yq e ".global.imageRegistry = \"$GCR\"" -i $C/values.yaml
              
        helm template ${C} |grep image:
        helm package ${C}
        helm gcs push ${C}-${VENDOR_VERSION}.tgz gcs-repo             
        helm repo update 
        cd .. && rm -rf temp
              
        yq e ".version = \"$VENDOR_VERSION\"" -i $C/mirror.yaml
        git add . && git commit -m "automatic upgrade of $C chart"
        git push -q

        echo "$C updated successfully"
     fi
 done
'
