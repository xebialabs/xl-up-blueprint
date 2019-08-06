## Custom xebialabs docker images

`xl up` commands helps you to install the Xebialabs DevOps in Kubernetes. While by default you can install the default Xebialabs docker images it sis common 
that you may have customization (custom plugins, custom synthetic xml and scripts). The default Xebialabs docker images include only the bundled plugins.

### Adding custom plugins

If you want to add a custom plugin that you have been developing manually or you have saved somewhere it can can be reached by a url you may use this [Dockerfile](plugins/Dockerfile):

```dockerfile
FROM xebialabs/xl-deploy:8.6.1

# Add plugin from local path. user 10001 is the xebialabs user
COPY --chown=10001:0 files/xld-liquibase-plugin-5.0.1.xldp /opt/xebialabs/xl-deploy-server/default-plugins/

# Add plugin from url. user 10001 is the xebialabs user
ADD --chown=10001:0 https://dist.xebialabs.com/public/community/xl-deploy/command2-plugin/3.9.1-1/command2-plugin-3.9.1-1.jar /opt/xebialabs/xl-deploy-server/default-plugins/

``` 

In the example above we are extending the  official XL Deploy docker image and adding 2 plugins (one from local path and one from url). `Note` that the `--chown` flag is mandatory so we  use the correct user and group (10001 is the xebialabs user in the base container)
Next step is to build the docker image (`docker build Dockerfile -t YOUR_TAG`) and then push your docker image to your docker image registry(`docker push YOUR_TAG`)

### Use custom XL Deploy or XL Release images in `xl up` 

When `xl up` comand is launched in `Advanced` mode there will be a question if you want to use a custom docker registry:

```$xslt
? Do you want to use custom Docker Registry? (y/N)
```

If you select yes them more questions will follow about the docker registry, credentials and image:

```$xslt

```