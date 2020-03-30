##Using Custom Ingress Controller in XL UP<br/>(NGINX)

Tutorial Link: <a href="https://github.com/uswitch/ingress/tree/master/deploy">NGINX Installation Guide</a>

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
Session Cookie Name: Any other name than JSESSIONID as it is already associated with XLR.
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
* Required annotations:
   * `kubernetes.io/ingress.class: nginx`
   * `nginx.ingress.kubernetes.io/rewrite-target: /`
   * `nginx.ingress.kubernetes.io/ssl-redirect: "false"`
   * `nginx.ingress.kubernetes.io/auth-type: basic`
   * `nginx.ingress.kubernetes.io/auth-realm: "Kibana Authentication"`
   * `nginx.ingress.kubernetes.io/auth-secret: {KIBANA_SECRET_NAME}`
   * `nginx.ingress.kubernetes.io/server-snippets: |
            option httpchk GET {HELTH_PROBE_PATH} HTTP/1.0`