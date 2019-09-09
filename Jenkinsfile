#!groovy
@Library('jenkins-pipeline-libs@master')
import com.xebialabs.pipeline.utils.Branches
import com.xebialabs.pipeline.globals.Globals
import com.xebialabs.pipeline.utils.Touch

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
        /*stage('Run XL UP Master') {
            agent {
                node {
                    label 'xld||xlr||xli'
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
                        sh "./gradlew goClean goBuild sonarqube -Dsonar.branch.name=${getBranch()} --info -x goTest -x updateLicenses -PincludeXlUp"
                    }
                    dir('${env.WORKSPACE}') {
                        def tests = [:]
                        testCases.each {
                            tests.put(runXlUpTest(${it}))
                        }
                        parallel tests
                        sh "./gradlew goClean goBuild sonarqube -Dsonar.branch.name=${getBranch()} --info -x updateLicenses"
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
                    githubLabelsPresent(this, ['run-xl-up-pr'])
                }
            }

            steps {
                script {
                    dir('${env.WORKSPACE}') {
                        sh "git clone git@github.com:xebialabs/xl-cli.git"
                    }
                    dir('${env.WORKSPACE}/xl-cli') {
                        sh "./gradlew goClean goBuild sonarqube -Dsonar.branch.name=${getBranch()} --info -x goTest -x updateLicenses -PincludeXlUp"
                    }
                    awsAccessKey = getAwsAccessKey()
                    eksEndpoint = getEksEndpoint()
                    efsFileSystem = getEfsFileSystem()
                    dir('${env.WORKSPACE}') {
                        def tests = [:]
                        testCases.each {
                            tests.put(runXlUpTest(${it}, awsAccessKey, eksEndpoint))
                        }
                        parallel tests
                        sh "./gradlew goClean goBuild sonarqube -Dsonar.branch.name=${getBranch()} --info -x updateLicenses"
                    }
                }
            }
        }*/
        stage('Clone deneme') {
            agent {
                node {
                    label 'xld||xlr||xli'
                }
            }
            steps {
                script{
                    sh "git clone git@github.com:xebialabs/xl-cli.git || true"
                    dir('${env.WORKSPACE}/xl-cli') {
                        sh "./gradlew goClean goBuild sonarqube -Dsonar.branch.name=${getBranch()} --info -x goTest -x updateLicenses -PincludeXlUp"
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

def getAwsAccessKey() {
    return awsAccessKey = sh (
            script: 'aws sts get-caller-identity --query \'UserId\' --output text',
            returnStdout: true
    ).trim()
}

def getEksEndpoint() {
    return eksEndpoint = sh (
            script: 'aws eks describe-cluster --name xld-perf-master --query \'cluster.endpoint\' --output text',
            returnStdout: true
    ).trim()
}

def getEfsFileSystem() {
    return efsFileSystem = sh (
            script: 'aws efs describe-file-systems --query \'FileSystems[0].FileSystemId\' --output text',
            returnStdout: true
    ).trim()
}

def runXlUpTest(String testCase, String awsAccessKey, String eksEndpoint) {
    sh "sed -e 's/https:\\/\\/aws-eks.com:6443/$eksEndpoint/g' xl-up-blueprint/xl-infra/__test__/test-cases/external-db/$testCase.yaml"
    sh "sed -e 's/SOMEKEY/$awsAccessKey/g' xl-up-blueprint/xl-infra/__test__/test-cases/external-db/$testCase.yaml"
    sh "./xl-cli/xl up -a xl-up-blueprint/xl-infra/__test__/test-cases/external-db/$testCase.yaml -b xl-infra -l xl-up-blueprint"
}
