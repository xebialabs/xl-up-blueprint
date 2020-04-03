##Using Custom Ingress Controller in XL UP<br/>(NGINX 0.30.0)

Tutorial Link: <a href="https://github.com/kubernetes/ingress-nginx/blob/master/docs/deploy/index.md">NGINX Installation Guide</a>

Ingress Rules:
1. XL Deploy <br/>
Service Name: xl-deploy-lb<br/>
Service Port: 4516<br/>
Health Probe Path: /deployit/ha/health<br/>
Session Cookie Name: None should be specified
2. XL Release <br/>
Service Name: xl-release<br/>
Service Port: 5516<br/>
Health Probe Path: /ha/health<br/>
Session Cookie Name: JSESSIONID
3. Kibana <br/>
Service Name: kibana-logging<br/>
Service Port: 5601<br/>
To setup a basic authentication for Kibana, follow these steps:<br/>
    * Generate authentication file named exactly "auth". Otherwise NGINX returns 503 Error. <br/>
    `htpasswd -c auth username`<br/>
     Enter the username and password to generate the key
    * `kubectl create secret generic {KIBANA_SECRET_NAME} --from-file=auth` <br/>
    * Add the required annotation from below to the ingress rule.<br/>
    **The secret has to be in the same namespace as the ingress rules**
4. Grafana<br/>
Service Name: grafana<br/>
Service Port: 3000
5. RabbitMQ<br/>
Service Name: rabbitmq<br/>
Service Port: 15672
#
Ingress Rule Annotations:
* NGINX uses a set of annotations starting with `nginx.ingress.kubernetes.io`. This can be changed in ingress controller definition file as an environment variable to the docker container.
* Ingress Rules:
    * XL-DEPLOY <br/>
    ``` 
  apiVersion: extensions/v1beta1
  kind: Ingress
  metadata:
    name: xl-deploy
    namespace: xebialabs
    labels:
      app: xl-deploy
      organization: xebialabs
    annotations:
      kubernetes.io/ingress.class: nginx
      nginx.ingress.kubernetes.io/rewrite-target: /$2
      nginx.ingress.kubernetes.io/ssl-redirect: "false"
      nginx.ingress.kubernetes.io/server-snippets: |
        option httpchk GET /deployit/ha/health HTTP/1.0
  spec:
    rules:
      - http:
          paths:
            - path: /xl-deploy(/|$)(.*)
              backend:
                serviceName: xl-deploy-lb
                servicePort: 4516
   ```
  * XL-RELEASE<br/>
  ```
  apiVersion: extensions/v1beta1
  kind: Ingress
  metadata:
    name: xl-release
    namespace: xebialabs
    labels:
      app: xl-release
      organization: xebialabs
    annotations:
      kubernetes.io/ingress.class: nginx
      nginx.ingress.kubernetes.io/rewrite-target: /$2
      nginx.ingress.kubernetes.io/ssl-redirect: "false"
      nginx.ingress.kubernetes.io/affinity: cookie
      nginx.ingress.kubernetes.io/session-cookie-name: JSESSIONID
      nginx.ingress.kubernetes.io/server-snippets: |
        option httpchk GET /ha/health HTTP/1.0
  spec:
    rules:
      - http:
          paths:
            - path: /xl-release(/|$)(.*)
              backend:
                serviceName: xl-release
                servicePort: 5516
  ```
  * Kibana
  ```
  apiVersion: extensions/v1beta1
  kind: Ingress
  metadata:
    name: kibana
    namespace: xebialabs
    labels:
      app: kibana
      organization: xebialabs
    annotations:
      kubernetes.io/ingress.class: nginx
      nginx.ingress.kubernetes.io/rewrite-target: /$2
      nginx.ingress.kubernetes.io/ssl-redirect: "false"
      nginx.ingress.kubernetes.io/auth-type: basic
      nginx.ingress.kubernetes.io/auth-realm: "Kibana Authentication"
      nginx.ingress.kubernetes.io/auth-secret: kibana-secret
  spec:
    rules:
      - http:
          paths:
            - path: /kibana(/|$)(.*)
              backend:
                serviceName: kibana-logging
                servicePort: 5601
  ```
  * Grafana
  ```
  apiVersion: extensions/v1beta1
  kind: Ingress
  metadata:
    name: grafana
    namespace: xebialabs
    labels:
      app: grafana
      organization: xebialabs
    annotations:
      kubernetes.io/ingress.class: nginx
      nginx.ingress.kubernetes.io/rewrite-target: /$2
      nginx.ingress.kubernetes.io/ssl-redirect: "false"
  spec:
    rules:
      - http:
          paths:
            - path: /grafana(/|$)(.*)
              backend:
                serviceName: grafana
                servicePort: 3000
  ```
  * Rabbit MQ
  ```
  apiVersion: extensions/v1beta1
  kind: Ingress
  metadata:
    name: rabbitmq
    namespace: xebialabs
    labels:
      app: rabbitmq
      organization: xebialabs
    annotations:
      kubernetes.io/ingress.class: nginx
      nginx.ingress.kubernetes.io/rewrite-target: /$2
      nginx.ingress.kubernetes.io/ssl-redirect: "false"
  spec:
    rules:
      - http:
          paths:
            - path: /rabbitmq(/|$)(.*)
              backend:
                serviceName: rabbitmq
                servicePort: 15672
  ```