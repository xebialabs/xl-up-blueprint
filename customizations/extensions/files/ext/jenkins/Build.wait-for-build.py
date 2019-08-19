import sys
import urllib
from com.xebialabs.xlrelease.plugin.webhook import JsonPathResult
from java.io import IOException


def finishPolling(buildStatus):
    print "\nFinished: %s" % buildStatus
    if buildStatus != 'SUCCESS':
        sys.exit(1)


request = HttpRequest(jenkinsServer, username, password)
jobContext = '/job/' + urllib.quote(jobName) + '/'

response = None
try:
    response = request.get(jobContext + str(buildNumber) + '/api/json', contentType='application/json')
except IOException as error:
    print "\nFailed to check the job status due to connection problems. Will retry in the next polling run. Error details: `%s`" % error
    task.schedule("jenkins/Build.wait-for-build.py")

buildStatus = None
if response and response.isSuccessful():
    buildStatus = JsonPathResult(response.response, 'result').get()
    duration = JsonPathResult(response.response, 'duration').get()
    if buildStatus and duration != 0:

        # Customization: get additional variables from the jenkins job
        if jobEnvVarName:
            envResponse = request.get(jobContext + '/' + str(buildNumber) + '/injectedEnvVars/api/json', contentType = 'application/json')
            jobEnvVarValue = JsonPathResult(envResponse.response, "envMap.%s" % jobEnvVarName).get()
        # end custom logic

        finishPolling(buildStatus)
    else:
        task.schedule("jenkins/Build.wait-for-build.py")

else:
    print "\nFailed to check the job status. Received an error from the Jenkins server: `%s`" % response.response
    finishPolling(buildStatus)