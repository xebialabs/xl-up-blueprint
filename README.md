# xl-up-blueprint
This blueprint is usable only on `xl up` command . Cannot be used separately with `xl blueprint` command.

If you run `xl up` command on a machine where access to internet is not available. Copy this repository to your machine and run `xl up -lb /path/to/downloaded/git-repo/xl-up`

## Monitoring

### Introduction

By default, `xl up` will install the following components

- Elasticsearch 
- Kibana
- FluentD
- Prometheus
- Grafana

By using these components, issues in the XL DevOps platform can quickly be identified and remedied. The dashboards and visualizations provided should be enough to get you started, but feel free to modify them according to your needs. 

### Querying from Kibana

The simplest form of queries in Elasticsearch is called a "Lucene query". For example, to find XL Deploy logs for a failed deployment, you can execute the following query directly in Kibana:

```
log: "com.xebialabs.platform.script.jython.JythonException: Error while executing script"
```

Of course, Elasticsearch is much more powerful and you can tailor dashboards and searches by using the more advanced query/filter options available in the [Elasticsearch Query DSL](elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html). 

