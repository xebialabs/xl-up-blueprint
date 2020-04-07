##Using Custom Ingress Controller in XL UP<br/>(Azure AGIC)

Tutorial Link: <a href="https://docs.microsoft.com/en-us/azure/application-gateway/ingress-controller-install-new">How to Install an Application Gateway Ingress Controller (AGIC) Using a New Application Gateway</a>

Ingress Rules:
* Setting health probes and session-cookie names should be done through Azure portal as there are no annotations to support that by now.

1. XL Deploy <br/>
Service Name: xl-deploy-lb<br/>
Service Port: 4516<br/>
Health Probe Path: /deployit/ha/health
Session Cookie Name: None should be specified
2. XL Release <br/>
Service Name: xl-release<br/>
Service Port: 5516<br/>
Health Probe Path: /ha/health<br/>
Session Cookie Name: JSESSIONID
3. Kibana <br/>
Service Name: kibana-logging<br/>
Service Port: 5601<br/>
4. Grafana<br/>
Service Name: grafana<br/>
Service Port: 3000
5. RabbitMQ<br/>
Service Name: rabbitmq<br>
Service Port: 15672
#
Ingress Rule Annotations:<br/>
- AGIC uses a set of annotations starting with `appgw.ingress.kubernetes.io`
- If you want applications to be accessible with `/{APP_NAME}/` pattern, you need to set path in ingress rules as `/{APP_NAME}/*` with path overwrite `/`
- Ingress Rules:
    * XL-DEPLOY
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
        kubernetes.io/ingress.class: azure/application-gateway
        appgw.ingress.kubernetes.io/backend-path-prefix: "/"
        appgw.ingress.kubernetes.io/ssl-redirect: "false"
        appgw.ingress.kubernetes.io/cookie-based-affinity: "true"
        appgw.ingress.kubernetes.io/backend-protocol: "http"
    spec:
      rules:
        - http:
            paths:
              - path: /xl-deploy/*
                backend:
                  serviceName: xl-deploy-lb
                  servicePort: 4516
    ```
    * XL-RELEASE
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
        kubernetes.io/ingress.class: azure/application-gateway
        appgw.ingress.kubernetes.io/backend-path-prefix: "/"
        appgw.ingress.kubernetes.io/ssl-redirect: "false"
        appgw.ingress.kubernetes.io/cookie-based-affinity: "true"
        appgw.ingress.kubernetes.io/backend-protocol: "http"
    spec:
      rules:
        - http:
            paths:
              - path: /xl-release/*
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
        kubernetes.io/ingress.class: azure/application-gateway
        appgw.ingress.kubernetes.io/backend-path-prefix: "/"
        appgw.ingress.kubernetes.io/ssl-redirect: "false"
    spec:
      rules:
        - http:
            paths:
              - path: /kibana/*
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
        kubernetes.io/ingress.class: azure/application-gateway
        appgw.ingress.kubernetes.io/backend-path-prefix: "/"
        appgw.ingress.kubernetes.io/ssl-redirect: "false"
    spec:
      rules:
        - http:
            paths:
              - path: /grafana/*
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
        kubernetes.io/ingress.class: azure/application-gateway
        appgw.ingress.kubernetes.io/backend-path-prefix: "/"
        appgw.ingress.kubernetes.io/ssl-redirect: "false"
    spec:
      rules:
        - http:
            paths:
              - path: /rabbitmq/
                backend:
                  serviceName: rabbitmq
                  servicePort: 15672
    ```