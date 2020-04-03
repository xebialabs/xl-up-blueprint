##Using Custom Ingress Controller in XL UP<br/>(Envoy based Gloo)

Tutorial Link: <a href="https://docs.solo.io/gloo/1.3.0/installation/gateway/kubernetes/">Installing Gloo on Kubernetes</a>

Ingress Rules:
- For every ingress rule, a route should be created in Gloo.<br/> 
`glooctl add route --path-prefix /{PREFIX}/ --dest-name {APP_UPSTREAM_NAME} --prefix-rewrite /`
1. XL Deploy <br/>
Service Name: xl-deploy-lb<br/>
Service Port: 4516<br/>
Health Probe Path: /deployit/ha/health
Session Cookie Name: None should be specified
2. XL Release <br/>
Service Name: xl-release<br/>
Service Port: 5516<br/>
Health Probe Path: /ha/health
Session Cookie Name: JSESSIONID<br/>
**XL-Release upstream's loadBalancerConfig should be set in order to use Session Affinity**
3. Kibana <br/>
Service Name: kibana-logging<br/>
Service Port: 5601<br/>
Authentication on Gloo requires Gloo Enterprise and is not available in Gloo community.<br/>
You can follow <a href='https://docs.solo.io/gloo/latest/security/auth/basic_auth/'>this tutorial</a> to provide a basic authentication for Kibana.
4. Grafana<br/>
Service Name: grafana<br/>
Service Port: 3000
5. RabbitMQ<br/>
Service Name: rabbitmq<br/>
Service Port: 15672
#
Ingress Rule Annotations:<br/>
- Gloo doesn't use any annotation for Ingress rules. Any configuration (session affinity and health probes) should be done in VirtualServices and Upstreams.
- Follow <a href="https://docs.solo.io/gloo/1.1.0/advanced_configuration/session_affinity/">this link</a> to add session affinity configuration
- `kubernetes.io/ingress.class: gloo` is required ONLY when `REQUIRE_INGRESS_CLASS` is specified in Gloo configuration and is set to true.
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
      kubernetes.io/ingress.class: gloo
  spec:
    rules:
      - http:
          paths:
            - path: /xl-deploy/
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
        kubernetes.io/ingress.class: gloo
    spec:
      rules:
        - http:
            paths:
              - path: /xl-release/
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
        kubernetes.io/ingress.class: gloo
    spec:
      rules:
        - http:
            paths:
              - path: /kibana/
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
        kubernetes.io/ingress.class: gloo
    spec:
      rules:
        - http:
            paths:
              - path: /grafana/
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
        kubernetes.io/ingress.class: gloo
    spec:
      rules:
        - http:
            paths:
              - path: /rabbitmq/
                backend:
                  serviceName: rabbitmq
                  servicePort: 15672
    ```