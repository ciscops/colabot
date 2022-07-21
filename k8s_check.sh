#!/bin/sh

kubectl get secret colabot-dev-1-secret
status=$?
if [ $status -eq 0] ; then
  kubectl delete -f output-secrets-dev.yaml
fi
kubectl create -f output-secrets-dev.yaml

kubectl get deployment colabot-dev-1
status=$?
if [ $status -eq 0] ; then
  kubectl delete -f output-manifest-dev.yaml
fi
kubectl create -f output-manifest-dev.yaml
