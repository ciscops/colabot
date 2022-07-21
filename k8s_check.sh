#!/bin/bash -xv
kubectl get secret colabot-dev-1-secret
echo $?
if [ $? -eq 0] ; then
  kubectl delete -f output-secrets-dev.yaml
fi
kubectl create -f output-secrets-dev.yaml

# kubectl get deployment colabot-dev-1
# echo $?
#
# if [ $(kubectl get secret colabot-dev-1-secret;echo $?) ]; then
#   kubectl delete -f output-secrets-dev.yaml
# fi
# kubectl create -f output-secrets-dev.yaml
#
# if [ $(kubectl get deployment colabot-dev-1;echo $?) ]; then
#   kubectl delete -f output-manifest-dev.yaml
# fi
# kubectl create -f output-manifest-dev.yaml
