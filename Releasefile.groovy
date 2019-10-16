// Exported from:        https://xl-release.xebialabs.com/#/templates/Folderadafda8557864c048c211cb50cf64fd4-Release1ba0c6e08e0b4c1484fe789c8d41acd0/releasefile
// XL Release version:   9.0.6
// Date created:         Wed Oct 16 15:06:00 CEST 2019
// Needs to be zipped in order to import back into XLR

xlr {
  template('XL UP Blueprints release template') {
    folder('xl-up')
    variables {
      stringVariable('BLUEPRINTS_VERSION') {
        label 'Blueprints Version'
        description 'The release version to use, should be x.x.x notation'
      }
      stringVariable('GIT_BRANCH') {
        label 'Git branch'
        description 'Git branch to build'
        value 'master'
      }
    }
    description 'XLR pipeline to release XL UP blueprints every milestone'
    scheduledStartDate Date.parse("yyyy-MM-dd'T'HH:mm:ssZ", '2019-04-08T09:00:00+0200')
    phases {
      phase('Prepare') {
        color '#0099CC'
        tasks {
          custom('Create Branch for release') {
            script {
              type 'github.CreateBranch'
              server 'XebiaLabs GitHub (from community GitHub plugin)'
              organization 'xebialabs'
              repositoryName 'xl-up-blueprint'
              oldBranch '${GIT_BRANCH}'
              newBranch '${BLUEPRINTS_VERSION}-maintenance'
            }
          }
        }
      }
      phase('Release') {
        color '#0099CC'
        tasks {
          custom('Release new version of UP Blueprints') {
            script {
              type 'jenkins.Build'
              jenkinsServer 'Jenkins NG'
              jobName 'XL Up/job/XL UP Blueprints Release'
              jobParameters 'RELEASE_BRANCH_NAME=${BLUEPRINTS_VERSION}-maintenance\n' +
                            'RELEASE_FOLDER=${BLUEPRINTS_VERSION}'
            }
          }
          custom('Notify team') {
            script {
              type 'slack.Notification'
              server 'Kube-Love'
              title 'UP Blueprints version  ${BLUEPRINTS_VERSION} released'
              message 'UP Blueprints version ${BLUEPRINTS_VERSION} was released to https://dist.xebialabs.com/public/xl-up-blueprints/${BLUEPRINTS_VERSION} and a new branch ${BLUEPRINTS_VERSION}-maintenance has been created in GitHub.'
              titleLink 'https://dist.xebialabs.com/public/xl-up-blueprints/${BLUEPRINTS_VERSION}'
              color 'good'
            }
          }
        }
      }
    }
    
  }
}