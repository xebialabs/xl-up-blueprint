#!groovy
@Library('jenkins-pipeline-libs@master')
import com.xebialabs.pipeline.utils.Branches

import groovy.transform.Field

@Field def testCases = ["eks-xld-xlr-mon", "on-prem-xld-mon", "gke-xld-xlr-mon"]

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
        ON_PREM_CERT = "${env.ON_PREM_CERT}"
        ON_PREM_KEY = "${env.ON_PREM_KEY}"
        ON_PREM_K8S_API_URL = "${env.ON_PREM_K8S_API_URL}"
        NSF_SERVER_HOST = "${env.NSF_SERVER_HOST}"
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
                        sh "mkdir -p temp"
                        dir('temp') {
                            if (githubLabelsPresent(this, ['same-branch-on-cli'])){
                                sh "git clone -b ${CHANGE_BRANCH} git@github.com:xebialabs/xl-cli.git || true"
                            } else {
                                sh "git clone git@github.com:xebialabs/xl-cli.git || true"
                            }
                        }
                        dir('temp/xl-cli') {
                            sh "./gradlew goClean goBuild -x goTest -x updateLicenses"
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
                        nfsSharePath = "xebialabs-k8s"
                        runXlUpOnEks(awsAccessKeyId, awsSecretKeyId, eksEndpoint, efsFileId)
                        runXlUpOnPrem(nfsSharePath)
                    } catch (err) {
                        throw err
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

def runXlUpOnEks(String awsAccessKeyId, String awsSecretKeyId, String eksEndpoint, String efsFileId) {
    sh "sed -ie 's@https://aws-eks.com:6443@${eksEndpoint}@g' integration-tests/test-cases/jenkins/eks-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@SOMEKEY@${awsAccessKeyId}@g' integration-tests/test-cases/jenkins/eks-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@SOMEMOREKEY@${awsSecretKeyId}@g' integration-tests/test-cases/jenkins/eks-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@test1234561@${efsFileId}@g' integration-tests/test-cases/jenkins/eks-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@test-eks-master@xl-up-master@g' integration-tests/test-cases/jenkins/eks-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@XldLic: ../xl-up/__test__/files/test-file@XldLic: ./deployit-license.lic@g' integration-tests/test-cases/jenkins/eks-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@XlrLic: ../xl-up/__test__/files/test-file@XlrLic: ./xl-release.lic@g' integration-tests/test-cases/jenkins/eks-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@XlKeyStore: ../xl-up/__test__/files/test-file@XlKeyStore: ./xl-up/__test__/files/keystore.jceks@g' integration-tests/test-cases/jenkins/eks-xld-xlr-mon-full.yaml"
    sh "./temp/xl-cli/build/linux-amd64/xl up -a integration-tests/test-cases/jenkins/eks-xld-xlr-mon-full.yaml -b xl-infra -l . --undeploy --skip-prompts"
    sh "./temp/xl-cli/build/linux-amd64/xl up -a integration-tests/test-cases/jenkins/eks-xld-xlr-mon-full.yaml -b xl-infra -l ."
    sh "./temp/xl-cli/build/linux-amd64/xl up -a integration-tests/test-cases/jenkins/eks-xld-xlr-mon-full.yaml -b xl-infra -l . --undeploy --skip-prompts"

}


def runXlUpOnPrem(String nsfSharePath) {
    sh """ if [[ ! -f "k8sClientCert-onprem.crt" ]]; then 
        echo ${ON_PREM_CERT} >> k8sClientCert-onprem-tmp.crt
        tr ' ' '\\n' < k8sClientCert-onprem-tmp.crt > k8sClientCert-onprem-tmp2.crt
        tr '%' ' ' < k8sClientCert-onprem-tmp2.crt > k8sClientCert-onprem.crt
        rm -f k8sClientCert-onprem-tmp.crt | rm -f k8sClientCert-onprem-tmp2.crt
    fi"""

    sh """ if [[ ! -f "k8sClientCert-onprem.key" ]]; then
        echo ${ON_PREM_KEY} >> k8sClientCert-onprem-tmp.key
        tr ' ' '\\n' < k8sClientCert-onprem-tmp.key > k8sClientCert-onprem-tmp2.key
        tr '%' ' ' < k8sClientCert-onprem-tmp2.key > k8sClientCert-onprem.key
        rm -f k8sClientCert-onprem-tmp.key | rm -f k8sClientCert-onprem-tmp2.key
    fi"""

    sh "sed -ie 's@https://k8s.com:6443@${ON_PREM_K8S_API_URL}@g' integration-tests/test-cases/jenkins/on-prem-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@K8sClientCertFile: ../xl-up/__test__/files/test-file@K8sClientCertFile: ./k8sClientCert-onprem.crt@g' integration-tests/test-cases/jenkins/on-prem-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@K8sClientKeyFile: ../xl-up/__test__/files/test-file@K8sClientKeyFile: ./k8sClientCert-onprem.key@g' integration-tests/test-cases/jenkins/on-prem-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@nfs-test.com@${NSF_SERVER_HOST}@g' integration-tests/test-cases/jenkins/on-prem-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@/xebialabs@/${nfsSharePath}@g' integration-tests/test-cases/jenkins/on-prem-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@XldLic: ../xl-up/__test__/files/test-file@XldLic: ./deployit-license.lic@g' integration-tests/test-cases/jenkins/on-prem-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@XlrLic: ../xl-up/__test__/files/test-file@XlrLic: ./xl-release.lic@g' integration-tests/test-cases/jenkins/on-prem-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@XlKeyStore: ../xl-up/__test__/files/test-file@XlKeyStore: ./xl-up/__test__/files/keystore.jceks@g' integration-tests/test-cases/jenkins/on-prem-xld-xlr-mon-full.yaml"
    sh "./temp/xl-cli/build/linux-amd64/xl up -a integration-tests/test-cases/jenkins/on-prem-xld-xlr-mon-full.yaml -b xl-infra -l . --undeploy --skip-prompts"
    sh "./temp/xl-cli/build/linux-amd64/xl up -a integration-tests/test-cases/jenkins/on-prem-xld-xlr-mon-full.yaml -b xl-infra -l ."
    sh "./temp/xl-cli/build/linux-amd64/xl up -a integration-tests/test-cases/jenkins/on-prem-xld-xlr-mon-full.yaml -b xl-infra -l . --undeploy --skip-prompts"

}