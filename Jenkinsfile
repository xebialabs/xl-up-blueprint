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
        XL_UP_GCP_PROJECT_ID = "${env.XL_UP_GCP_PROJECT_ID}"
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

        //stage('Run XL UP Branch Linux') {
        //    agent {
        //        node {
        //            label 'xld||xlr||xli'
        //        }
        //    }
//
        //    when {
        //        expression {
        //            !Branches.onMasterBranch(env.BRANCH_NAME) &&
        //                    githubLabelsPresent(this, ['run-xl-up-pr'])
        //        }
        //    }
//
        //    steps {
        //        script {
        //            try {
        //                sh "mkdir -p temp"
        //                dir('temp') {
        //                    if (githubLabelsPresent(this, ['same-branch-on-cli'])){
        //                        sh "git clone -b ${CHANGE_BRANCH} git@github.com:xebialabs/xl-cli.git || true"
        //                    } else {
        //                        sh "git clone git@github.com:xebialabs/xl-cli.git || true"
        //                    }
        //                }
        //                dir('temp/xl-cli') {
        //                    sh "./gradlew goClean goBuild -x goTest -x updateLicenses -x buildDarwinAmd64 -x buildWindowsAmd64"
        //                }
        //                awsConfigure = readFile "/var/lib/jenkins/.aws/credentials"
        //                awsAccessKeyIdLine = awsConfigure.split("\n")[1]
        //                awsSecretKeyIdLine = awsConfigure.split("\n")[2]
        //                awsAccessKeyId = awsAccessKeyIdLine.split(" ")[2]
        //                awsSecretKeyId = awsSecretKeyIdLine.split(" ")[2]
        //                sh "curl https://dist.xebialabs.com/customer/licenses/download/v3/deployit-license.lic -u ${DIST_SERVER_CRED} -o ./deployit-license.lic"
        //                sh "curl https://dist.xebialabs.com/customer/licenses/download/v3/xl-release-license.lic -u ${DIST_SERVER_CRED} -o ./xl-release.lic"
        //                eksEndpoint = sh (script: 'aws eks describe-cluster --region eu-west-1 --name xl-up-master --query \'cluster.endpoint\' --output text', returnStdout: true).trim()
        //                efsFileId = sh (script: 'aws efs describe-file-systems --region eu-west-1 --query \'FileSystems[0].FileSystemId\' --output text', returnStdout: true).trim()
        //                nfsSharePath = "xebialabs-k8s"
        //                runXlUpOnEks(awsAccessKeyId, awsSecretKeyId, eksEndpoint, efsFileId)
        //                runXlUpOnPrem(nfsSharePath)
        //                runXlUpOnGke()
        //                sh "rm -rf temp"
        //            } catch (err) {
        //                sh "rm -rf temp"
        //                throw err
        //            }
        //        }
//
        //    }
        //}

        stage('Run XL UP Branch Windows') {
            agent {
                node {
                    label 'windows-jdk8'
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
                        bat "if not exist temp mkdir temp"
                        dir('temp') {
                            if (githubLabelsPresent(this, ['same-branch-on-cli'])){
                                bat "git clone -b ${CHANGE_BRANCH} git@github.com:xebialabs/xl-cli.git || true"
                            } else {
                                bat "git clone git@github.com:xebialabs/xl-cli.git || true"
                            }
                        }
                        dir('temp\\xl-cli') {
                            bat "./gradlew goClean goBuild -x goTest -x updateLicenses -x buildDarwinAmd64 -x buildLinuxAmd64"
                        }

                        bat "curl https://dist.xebialabs.com/customer/licenses/download/v3/deployit-license.lic -u ${DIST_SERVER_CRED} -o ./deployit-license.lic"
                        bat "curl https://dist.xebialabs.com/customer/licenses/download/v3/xl-release-license.lic -u ${DIST_SERVER_CRED} -o ./xl-release.lic"
                        nfsSharePath = "xebialabs-k8s"
                        runXlUpOnPremWindows(nfsSharePath)

                        bat "rmdir /q /s temp"
                    } catch (err) {
                        bat "rmdir /q /s temp"
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
    sh "./temp/xl-cli/build/linux-amd64/xl up -a integration-tests/test-cases/jenkins/on-prem-xld-xlr-mon-full.yaml -b xl-infra -l . --undeploy --skip-prompts"
    sh "./temp/xl-cli/build/linux-amd64/xl up -a integration-tests/test-cases/jenkins/on-prem-xld-xlr-mon-full.yaml -b xl-infra -l ."
    sh "./temp/xl-cli/build/linux-amd64/xl up -a integration-tests/test-cases/jenkins/on-prem-xld-xlr-mon-full.yaml -b xl-infra -l . --undeploy --skip-prompts"

}

def runXlUpOnPremWindows(String nsfSharePath) {
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

    sh "sed -ie 's@https://k8s.com:6443@${ON_PREM_K8S_API_URL}@g' integration-tests\\test-cases\\jenkins\\on-prem-xld-xlr-mon-full-windows.yaml"
    sh "sed -ie 's@K8sClientCertFile: ../xl-up/__test__/files/test-file@K8sClientCertFile: k8sClientCert-onprem.crt@g' integration-tests\\test-cases\\jenkins\\on-prem-xld-xlr-mon-full-windows.yaml"
    sh "sed -ie 's@K8sClientKeyFile: ../xl-up/__test__/files/test-file@K8sClientKeyFile: k8sClientCert-onprem.key@g' integration-tests\\test-cases\\jenkins\\on-prem-xld-xlr-mon-full-windows.yaml"
    sh "sed -ie 's@nfs-test.com@${NSF_SERVER_HOST}@g' integration-tests\\test-cases\\jenkins\\on-prem-xld-xlr-mon-full-windows.yaml"
    sh "sed -ie 's@/xebialabs@/${nfsSharePath}@g' integration-tests\\test-cases\\jenkins\\on-prem-xld-xlr-mon-full-windows.yaml"
    sh "./temp/xl-cli/build/windows-amd64/xl.exe up -a integration-tests\\test-cases\\jenkins\\on-prem-xld-xlr-mon-full-windows.yaml -b xl-infra -l . --undeploy --skip-prompts"
    sh "./temp/xl-cli/build/windows-amd64/xl.exe up -a integration-tests\\test-cases\\jenkins\\on-prem-xld-xlr-mon-full-windows.yaml -b xl-infra -l ."
    sh "./temp/xl-cli/build/windows-amd64/xl.exe up -a integration-tests\\test-cases\\jenkins\\on-prem-xld-xlr-mon-full-windows.yaml -b xl-infra -l . --undeploy --skip-prompts"

}

def runXlUpOnGke() {
    GKE_ACCOUNT_EMAIL = sh(script: 'cat /var/lib/jenkins/.gcloud/account.json | python -c \'import json, sys; obj = json.load(sys.stdin); print obj["client_email"];\'', returnStdout: true).trim()

    sh "gcloud auth activate-service-account ${GKE_ACCOUNT_EMAIL} --key-file=/var/lib/jenkins/.gcloud/account.json"
    sh "gcloud container clusters get-credentials  gke-xl-up-cluster --zone europe-west3-b --project ${XL_UP_GCP_PROJECT_ID}"

    GKE_ENDPOINT = sh(script: 'kubectl config view --minify -o jsonpath=\'{.clusters[0].cluster.server}\'', returnStdout: true).trim()
    SECRET_NAME = sh(script: "kubectl get secrets -o custom-columns=:metadata.name -n kube-system | grep xebialabs-admin", returnStdout: true).trim()
    GKE_TOKEN = sh(script: "kubectl get secrets --field-selector metadata.name=${SECRET_NAME} -n kube-system -o=jsonpath='{.items[].data.token}' | base64 -d", returnStdout: true).trim()
    NFS_PATH = sh(script: "gcloud filestore instances list --project ${XL_UP_GCP_PROJECT_ID} --format='csv(fileShares.name,networks.ipAddresses[0])' | sed -n 2p | tr ',' '\n' | sed -n 1p", returnStdout: true).trim()
    NFS_HOST = sh(script: "gcloud filestore instances list --project ${XL_UP_GCP_PROJECT_ID} --format='csv(fileShares.name,networks.ipAddresses[0])' | sed -n 2p | tr ',' '\n' | sed -n 2p", returnStdout: true).trim()

    sh "sed -ie 's@{{GKE_ENDPOINT}}@${GKE_ENDPOINT}@g' integration-tests/test-cases/jenkins/gke-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@{{K8S_TOKEN}}@${GKE_TOKEN}@g' integration-tests/test-cases/jenkins/gke-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@{{NFS_HOST}}@${NFS_HOST}@g' integration-tests/test-cases/jenkins/gke-xld-xlr-mon-full.yaml"
    sh "sed -ie 's@{{NFS_PATH}}@/${NFS_PATH}@g' integration-tests/test-cases/jenkins/gke-xld-xlr-mon-full.yaml"

    sh "./temp/xl-cli/build/linux-amd64/xl up -d -a integration-tests/test-cases/jenkins/gke-xld-xlr-mon-full.yaml -b xl-infra -l . --undeploy --skip-prompts"
    sh "./temp/xl-cli/build/linux-amd64/xl up -d -a integration-tests/test-cases/jenkins/gke-xld-xlr-mon-full.yaml -b xl-infra -l ."
    sh "./temp/xl-cli/build/linux-amd64/xl up -d -a integration-tests/test-cases/jenkins/gke-xld-xlr-mon-full.yaml -b xl-infra -l . --undeploy --skip-prompts"
}