##Using Custom Ingress Controller in XL UP<br/>(Envoy based Gloo)

Tutorial Link: <a href="https://docs.solo.io/gloo/1.3.0/installation/gateway/kubernetes/">Installing Gloo on Kubernetes</a>

Ingress Rules:
- For every ingress rule, a route should be created in Gloo.<br/> 
`glooctl add route --path-prefix /{PREFIX}/ --dest-name {APP_UPSTREAM_NAME} --prefix-rewrite /`
- Example on configuring routes can be found <a href='https://docs.solo.io/gloo/1.3.0/gloo_routing/hello_world/#verify-the-upstream-for-the-pet-store-application'>here</a>
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
You can follow <a href='https://docs.solo.io/gloo/latest/guides/security/auth/basic_auth/'>this tutorial</a> to provide a basic authentication for Kibana.
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