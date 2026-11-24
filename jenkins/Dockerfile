# Jenkins with the Docker CLI, so pipelines can run docker build/run
# against the host's Docker engine (socket mounted in docker-compose.yml)
FROM jenkins/jenkins:lts-jdk17
USER root
COPY --from=docker:cli /usr/local/bin/docker /usr/local/bin/docker
RUN jenkins-plugin-cli --plugins git workflow-aggregator junit github pipeline-stage-view
