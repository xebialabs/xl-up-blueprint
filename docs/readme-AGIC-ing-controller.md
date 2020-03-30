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
- Required Annotations:
    * `kubernetes.io/ingress.class: azure/application-gateway` REQUIRED
    * `appgw.ingress.kubernetes.io/backend-path-prefix: PATH_OVERWRITE` 
    * `appgw.ingress.kubernetes.io/ssl-redirect: "true" or "false"`
    * `appgw.ingress.kubernetes.io/cookie-based-affinity: "true" or "false"`
    * `appgw.ingress.kubernetes.io/backend-protocol: "http" or "https"`