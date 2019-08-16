#!groovy

pipeline {
    agent none

    options {
        buildDiscarder(logRotator(numToKeepStr: '20', artifactDaysToKeepStr: '7', artifactNumToKeepStr: '5'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
        ansiColor('xterm')
    }

    stages {
        stage('Test xl-up Blueprint') {
            agent {
                node {
                    label 'xld||xlr||xli'
                }
            }

            steps {
                script {
                    try {
                        githubNotify context: "Testing blueprint", status: "PENDING"
                        checkout scm
                        sh "python3.7 integration_tests.py"
                        githubNotify context: "Testing blueprint", status: "SUCCESS"
                        notifySlack("Testing blueprint succeeded", "good")
                    } catch (err) {
                        githubNotify context: "Testing blueprint", status: "FAILURE"
                        notifySlack("Testing blueprint failed", "danger")
                        throw err
                    }
                }

            }
        }
        stage('Run XL UP Master') {
            agent {
                node {
                    label 'xld|xlr|xli'
                }
            }

            when {
                expression {
                    githubLabelsPresent(this, ['run-xl-up-master'])
                }
            }

            steps {
                script {
                    dir('${env.WORKSPACE}') {
                        sh "git clone git@github.com:xebialabs/xl-cli.git"
                    }
                    dir('${env.WORKSPACE}/xl-cli') {
                        sh "./gradlew goClean goBuild sonarqube -Dsonar.branch.name=${getBranch()} --info -x updateLicenses"
                    }
                    dir('${env.WORKSPACE}') {
                        sh "./xl-cli/xl up -a xl-up-blueprint/xl-infra/__test__/local-kube.yaml -b xl-infra -l xl-up-blueprint"
                    }
                }
            }
        }
        stage('Run XL UP Branch') {
            agent {
                node {
                    label 'xld|xlr|xli'
                }
            }

            when {
                expression {
                    githubLabelsPresent(this, ['run-xl-up-pr'])
                }
            }

            steps {
                script {
                    dir('${env.WORKSPACE}') {
                        sh "git clone git@github.com:xebialabs/xl-cli.git"
                    }
                    dir('${env.WORKSPACE}/xl-cli') {
                        sh "./gradlew goClean goBuild sonarqube -Dsonar.branch.name=${getBranch()} --info -x updateLicenses"
                    }
                    dir('${env.WORKSPACE}') {
                        sh "./xl-cli/xl up -a xl-up-blueprint/xl-infra/__test__/local-kube.yaml -b xl-infra -l xl-up-blueprint"
                    }
                }
            }
        }
    }
}

def notifySlack(String message, String notificationColor) {
    slackSend(color: "${notificationColor}", message: "$message (<${env.BUILD_URL}|${env.JOB_NAME} [${env.BUILD_NUMBER}]>)",
            channel: "#kubicorns", tokenCredentialId: "slack-token")
}