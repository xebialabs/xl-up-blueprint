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
                        sh "python3.6 integration_tests.py"
                        githubNotify context: "Testing blueprint", status: "SUCCESS"
                    } catch (err) {
                        githubNotify context: "Testing blueprint", status: "FAILURE"
                        throw err
                    }
                }

            }
        }
    }
}