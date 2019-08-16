#!groovy
@Library('jenkins-pipeline-libs@master')
import com.xebialabs.pipeline.utils.Branches

import groovy.transform.Field

@Field def testCases = ["eks-xld-xlr-mon"]

pipeline {
    agent none

    options {
        buildDiscarder(logRotator(numToKeepStr: '20', artifactDaysToKeepStr: '7', artifactNumToKeepStr: '5'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
        ansiColor('xterm')
    }

    environment {
        REPOSITORY_NAME = 'xl-up-blueprint'
        DIST_SERVER_CRED = credentials('distserver')
    }

    stages {
        /*stage('Test xl-up Blueprint') {
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
                        //notifySlack("Testing blueprint succeeded", "good")
                    } catch (err) {
                        githubNotify context: "Testing blueprint", status: "FAILURE"
                        //notifySlack("Testing blueprint failed", "danger")
                        throw err
                    }
                }

            }
        }*/
        stage('Run XL UP Master') {
            agent {
                node {
                    label 'xld||xlr||xli'
                }
            }

            when {
                expression {
                    Branches.onMasterBranch(env.BRANCH_NAME) &&
                            githubLabelsPresent(this, ['run-xl-up-master'])
                }
            }

            steps {
                script {
                    try {
                        sh "mkdir -p xld"
                        dir('xld') {
                            sh "git clone git@github.com:xebialabs/xl-cli.git || true"
                        }
                        dir('xld/xl-cli') {
                            sh "./gradlew goClean goBuild -x goTest -x updateLicenses -PincludeXlUp"
                            stash name: "xl-up", inludes: "build/darwin-amd64/xl"
                        }
                        unstash name: "xl-up"
                        awsAccessKey = sh (script: 'aws sts get-caller-identity --query \'UserId\' --output text', returnStdout: true).trim()
                        eksEndpoint = sh (script: 'aws eks describe-cluster --region eu-west-1 --name xl-up-master --query \'cluster.endpoint\' --output text', returnStdout: true).trim()
                        efsFileSystem = sh (script: 'aws efs describe-file-systems --region eu-west-1 --query \'FileSystems[0].FileSystemId\' --output text', returnStdout: true).trim()
                        runXlUp(awsAccessKey, eksEndpoint)
                    } catch (err) {
                        throw err
                    }
                }

            }
        }
        stage('Run XL UP Branch') {
            agent {
                node {
                    label 'xld||xlr||xli'
                }
            }

            when {
                expression {
                    !Branches.onMasterBranch(env.BRANCH_NAME) &&
                            githubLabelsPresent(this, ['run-xl-up-pr'])
                }
            }

            steps {
                script {
                    try {
                        sh "mkdir -p xld"
                        dir('xld') {
                            sh "git clone git@github.com:xebialabs/xl-cli.git || true"
                        }
                        dir('xld/xl-cli') {
                            sh "./gradlew goClean goBuild --info -x goTest -x updateLicenses -PincludeXlUp"
                        }
                        awsConfigure = readFile "/var/lib/jenkins/.aws/credentials"
                        awsAccessKeyIdLine = awsConfigure.split("\n")[1]
                        awsSecretKeyIdLine = awsConfigure.split("\n")[2]
                        awsAccessKeyId = awsAccessKeyIdLine.split(" ")[2]
                        awsSecretKeyId = awsSecretKeyIdLine.split(" ")[2]
                        sh "curl https://dist.xebialabs.com/customer/licenses/download/v3/deployit-license.lic -u ${DIST_SERVER_CRED} -o ./deployit-license.lic"
                        sh "curl https://dist.xebialabs.com/customer/licenses/download/v3/xl-release-license.lic -u ${DIST_SERVER_CRED} -o ./xl-release.lic"
                        eksEndpoint = sh (script: 'aws eks describe-cluster --region eu-west-1 --name xl-up-master --query \'cluster.endpoint\' --output text', returnStdout: true).trim()
                        efsFileId = sh (script: 'aws efs describe-file-systems --region eu-west-1 --query \'FileSystems[0].FileSystemId\' --output text', returnStdout: true).trim()
                        runXlUp(awsAccessKeyId, awsSecretKeyId, eksEndpoint, efsFileId)
                    } catch (err) {
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

def runXlUp(String awsAccessKeyId, String awsSecretKeyId, String eksEndpoint, String efsFileId) {
    sh "sed -ie 's%https://aws-eks.com:6443%${eksEndpoint}%g' xl-up/__test__/test-cases/provisioned-db/eks-xld-xlr-mon.yaml"
    sh "sed -ie 's@SOMEKEY@${awsAccessKeyId}@g' xl-up/__test__/test-cases/provisioned-db/eks-xld-xlr-mon.yaml"
    sh "sed -ie 's@SOMEMOREKEY@${awsSecretKeyId}@g' xl-up/__test__/test-cases/provisioned-db/eks-xld-xlr-mon.yaml"
    sh "sed -ie 's@test1234561@${efsFileId}@g' xl-up/__test__/test-cases/provisioned-db/eks-xld-xlr-mon.yaml"
    sh "sed -ie 's@test-eks-master@xl-up-master@g' xl-up/__test__/test-cases/provisioned-db/eks-xld-xlr-mon.yaml"
    sh "sed -ie 's@XldLic: ../xl-up/__test__/files/test-file@xldLic: ./deployit-license.lic@g' xl-up/__test__/test-cases/provisioned-db/eks-xld-xlr-mon.yaml"
    sh "sed -ie 's@XlrLic: ../xl-up/__test__/files/test-file@xlrLic: ./xl-release.lic@g' xl-up/__test__/test-cases/provisioned-db/eks-xld-xlr-mon.yaml"
    sh "sed -ie 's@XlKeyStore: ../xl-up/__test__/files/test-file@XlKeyStore: ./xl-up/__test__/files/keystore.jceks@g' xl-up/__test__/test-cases/provisioned-db/eks-xld-xlr-mon.yaml"
    sh "sed -ie 's@8.6.1@9.0.2@g' xl-up/__test__/test-cases/provisioned-db/eks-xld-xlr-mon.yaml"
    sh "echo 'UseCustomRegistry: false' >> xl-up/__test__/test-cases/provisioned-db/eks-xld-xlr-mon.yaml"
    sh "echo 'ExternalDatabase: false' >> xl-up/__test__/test-cases/provisioned-db/eks-xld-xlr-mon.yaml"
    sh "./xld/xl-cli/build/linux-amd64/xl up -a xl-up/__test__/test-cases/provisioned-db/eks-xld-xlr-mon.yaml -b xl-infra -l ."
}
