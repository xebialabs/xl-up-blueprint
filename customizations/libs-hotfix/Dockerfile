FROM xebialabs/xl-deploy:9.0.3

# Add jdbc lib from local path. user 10001 is the xebialabs user
ADD --chown=10001:0 files/ojdbc6.jar /opt/xebialabs/xl-deploy-server/lib/

# Add hotfix for lib from local path. user 10001 is the xebialabs user
ADD --chown=10001:0 files/lib-hotfix.jar /opt/xebialabs/xl-deploy-server/hotfix/lib/

# Add hotfix for plugin from local path. user 10001 is the xebialabs user
ADD --chown=10001:0 files/plugin-hotfix.jar /opt/xebialabs/xl-deploy-server/hotfix/plugins/