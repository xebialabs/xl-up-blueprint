#!/bin/bash
#set -x
# ############# ############# ###############
# ##       GKE AUTHENTICATION HELPER     ## #
# ##             by XebiaLabs            ## #
# ############# ############# ###############

svc_account_name="xebialabs-admin"
cluster_name="TEST_CLUSTER"
zone="europe-west4-a"
auth_type="none"

while getopts n:z:a:h option
do
    case "${option}"
    in
        h) echo -e "Example command: \n./get-sa-token.sh -n test-cluster -z us-central1-a -a token \n------------------\nAvailable options:\n------------------\n-n: GKE Cluster name\n-z: GKE Zone\n-a: Authentication type. Only 'token' or 'cert' options are valid!"; exit 0;;
        n) cluster_name=${OPTARG};;
        z) zone=${OPTARG};;
        a) auth_type=${OPTARG};;
        *) echo -e "\nExample command: \n./get-sa-token.sh -n test-cluster -z us-central1-a -a token \n------------------\nAvailable options:\n------------------\n-n: GKE Cluster name\n-z: GKE Zone\n-a: Authentication type. Only 'token' or 'cert' options are valid!"; exit 1;;
    esac
done

applyCertificateRBAC () {
    kubectl apply -f xebialabs-rbac-certificate.yaml
}

base64decode () {
    case "$OSTYPE" in
      darwin*)  base64 -D ;;
      linux*)   base64 -d ;;
      *)        echo "unknown: $OSTYPE" ;;
    esac
}

createToken () {
    kubectl apply -f xebialabs-rbac-token.yaml
}

main () {
    # Get Auth type
    case ${auth_type}
    in
       token) echo "Authentication type is token. Creating token..."; generateKubeconf; createToken; saveTokenToFile;;
        cert) echo "Authentication type is client certificate. Applying RBAC..."; generateKubeconf; applyCertificateRBAC; saveCertKeyToFiles;;
        none) echo "No Authentication type provided. Quitting..."; exit 0;;
           *) echo "Provided Authentication type is not valid!"; exit 1;;
    esac
}

generateKubeconf () {
    gcloud container clusters get-credentials ${cluster_name} --zone ${zone}
}

getClientCrt () {
    gcloud container clusters describe ${cluster_name} --format="json" --zone ${zone} | jq -r .masterAuth.clientCertificate | base64decode
}

getClientKey () {
    gcloud container clusters describe ${cluster_name} --format="json" --zone ${zone} | jq -r .masterAuth.clientKey | base64decode
}

getToken () {
    local secret_name=${1}
    kubectl get secrets --field-selector metadata.name=${secret_name} -n kube-system -o=jsonpath='{.items[].data.token}' | base64decode
}

saveTokenToFile () {
    secret_name=$(kubectl get secrets -o custom-columns=:metadata.name -n kube-system | grep ${svc_account_name})
    if [[ -n ${secret_name} ]] ; then
        getToken ${secret_name} > token.txt
        echo "Auth token was found and saved to token.txt."
    else
        echo "ServiceAccount ${svc_account_name} was not found. Trying to obtain certificate and key..."
    fi
}

saveCertKeyToFiles () {
    if [[ ( -n getClientCrt ) && ( -n getClientKey  ) ]] ; then
        getClientCrt > client.crt
        getClientKey > client.key
        echo "Client certificate and key were saved in client.crt and client.key accordingly."
    else
        echo "Client certificate and key were not found."
    fi
}

main

