FROM xebialabs/xl-deploy:8.6.1

# Add plugin from local path
COPY --chown=10001:0 files/xld-liquibase-plugin-5.0.1.xldp /opt/xebialabs/xl-deploy-server/plugins/

# Add plugin from url
ADD --chown=10001:0 https://dist.xebialabs.com/public/community/xl-deploy/command2-plugin/3.9.1-1/command2-plugin-3.9.1-1.jar /opt/xebialabs/xl-deploy-server/plugins/

#USER root

ADD --chown=10001:0 https://dist.xebialabs.com/public/community/xl-deploy/command2-plugin/3.9.1-1/command2-plugin-3.9.1-1.jar /opt/xebialabs/xl-deploy-server/hotfix/plugins/

#RUN chown 10001 /opt/xebialabs/xl-deploy-server/hotfix/plugins/command2-plugin-3.9.1-1.jar

#USER 10001