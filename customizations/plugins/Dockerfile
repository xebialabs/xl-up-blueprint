FROM xebialabs/xl-deploy:8.6.1

# Add plugin from local path. user 10001 is the xebialabs user
COPY --chown=10001:0 files/xld-liquibase-plugin-5.0.1.xldp /opt/xebialabs/xl-deploy-server/default-plugins/

# Add plugin from url. user 10001 is the xebialabs user
ADD --chown=10001:0 https://dist.xebialabs.com/public/community/xl-deploy/command2-plugin/3.9.1-1/command2-plugin-3.9.1-1.jar /opt/xebialabs/xl-deploy-server/default-plugins/


