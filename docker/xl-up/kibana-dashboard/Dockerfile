FROM docker.elastic.co/beats/metricbeat:6.3.2
COPY dashboards /tmp
WORKDIR /usr/share/metricbeat/

ENV ELASTICSEARCH_URL=''
ENV ELASTICSEARCH_USERNAME=''
ENV ELASTICSEARCH_PASSWORD=''
ENV KIBANA_URL=''

CMD ./metricbeat setup \
  --dashboards \
  -E output.elasticsearch.hosts="[$ELASTICSEARCH_URL]" \
  -E output.elasticsearch.username="$ELASTICSEARCH_USERNAME" \
  -E output.elasticsearch.password="$ELASTICSEARCH_PASSWORD" \
  -E setup.kibana.host=$KIBANA_URL \
  -E setup.dashboards.directory=/tmp
