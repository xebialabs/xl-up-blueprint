#!/bin/bash

sa_name=xebialabs-admin

getClientCrt () {
    gcloud container clusters describe TEST_CLUSTER --format="json" --zone europe-west4-a | jq -r .masterAuth.clientCertificate | base64 -d
}

getClientKey () {
    gcloud container clusters describe TEST_CLUSTER --format="json" --zone europe-west4-a | jq -r .masterAuth.clientKey | base64 -d
}

getToken () {
    local secret_name=${1}
    kubectl get secrets --field-selector metadata.name=${secret_name} -n kube-system -o=jsonpath='{.items[].data.token}' | base64 -d
}

### TOKEN AUTH ###

secret_name=$(kubectl get secrets -o custom-columns=:metadata.name -n kube-system | grep ${sa_name})
if [[ -n ${secret_name} ]] ; then
	getToken ${secret_name} > token.txt
	echo "Auth token was found and saved to token.txt."
else
	echo "ServiceAccount ${sa_name} was not found. Trying to obtain certificate and key..."
fi

### CERTIFICATE AUTH ###


client_key=$()
client_crt=$()
if [[ ( -n getClientCrt ) && ( -n getClientKey  ) ]] ; then
	getClientCrt > client.crt
	getClientKey > client.key
	echo "Client certificate and key were saved in client.crt and client.key accordingly."
else
	echo "Client certificate and key were not found."
fi