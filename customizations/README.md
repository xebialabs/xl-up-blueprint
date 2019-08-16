## Custom xebialabs docker images

`xl up` commands helps you to install the Xebialabs DevOps in Kubernetes. While by default you can install the default Xebialabs docker images it is common 
that you may have customizations (custom plugins, custom synthetic xml and scripts). The default Xebialabs docker images include only the bundled plugins.

### Adding custom plugins

If you want to add a custom plugin that you have been developing manually or you have saved somewhere it can can be reached by a URL you may use this [Dockerfile](plugins/Dockerfile):

```dockerfile
FROM xebialabs/xl-deploy:8.6.1

# Add plugin from local path. user 10001 is the xebialabs user
COPY --chown=10001:0 files/xld-liquibase-plugin-5.0.1.xldp /opt/xebialabs/xl-deploy-server/default-plugins/

# Add plugin from url. user 10001 is the xebialabs user
ADD --chown=10001:0 https://dist.xebialabs.com/public/community/xl-deploy/command2-plugin/3.9.1-1/command2-plugin-3.9.1-1.jar /opt/xebialabs/xl-deploy-server/default-plugins/

``` 

In the example above we are extending the  official XL Deploy docker image and adding 2 plugins (one from local path and one from url). `Note` that the `--chown` flag is mandatory so we  use the correct user and group (10001 is the xebialabs user in the base container)
Next step is to build the docker image (`docker build Dockerfile -t YOUR_TAG`) and then push your docker image to your docker image registry(`docker push YOUR_TAG`)

### Adding extensions

If you want to add files into the *XLD_HOME/ext* or *XLR_HOME/ext* folder as part of your extensions or modifications you can use this  [Dockerfile](extensions/Dockerfile):

```dockerfile
FROM xebialabs/xl-release:9.0.2

# Add plugin from local path. user 10001 is the xebialabs user
ADD --chown=10001:0 files/ext /opt/xebialabs/xl-release-server/ext/
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
? Do you want to use custom Docker Registry? Yes
? Enter your Docker registry URL and organization: xl-docker.xebialabs.com
? Enter your Docker Registry username: userx
? Enter your Docker Registry password: ******
? Would you like to install XL Deploy? Yes
? Enter your custom XL Deploy image and tag: (xl-deploy:8.5.3) xl-deploy:9.0.1
```

The docker registry URL depends on your docker registry setup. In case of Dockerhub the you need domain and organization, for example `docker.io/xebialabs`. In case of an internal docker registry where organization is not required it  will be `xl-docker.xebialabs.com`
Docker credentials are needed if you need to authenticate to the docker registry in order to pull an image
The custom docker image that you want to use should use a tag that follows [semver](https://semver.org/). An image with a random tag like `xl-deploy:test123` will not work