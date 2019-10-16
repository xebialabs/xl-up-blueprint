# Steps to setup ES cluster on a kubernetes cluster

1. Create namespace xebialabs-dev if it doesn't exist `kubectl create namespace xebialabs-dev`
3. Run `kubectl apply -f elasticsearch.yaml`
4. Set the passwords for all built-in users on the pod
   1. Run `kubectl exec -it <podname> -n xebialabs-dev -- /bin/bash` 
   2. Run `bin/elasticsearch-setup-passwords interactive` and set password for default users
5. Check by creating a tunnel 
   1. Run `kubectl port-forward <podname> 9200:9200 --namespace=xebialabs-dev`
   2. Run `curl --user elastic:<set during setup> http://localhost:9200/_cluster/state?pretty` and should produce a valid output