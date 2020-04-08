import groovy.json.JsonOutput;
podTemplate(yaml: '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: docker
    image: docker:19.03.1
    command:
    - sleep
    args:
    - 99d
    env:
      - name: DOCKER_HOST
        value: tcp://localhost:2375
  - name: docker-daemon
    image: docker:19.03.1-dind
    securityContext:
      privileged: true
    env:
      - name: DOCKER_TLS_CERTDIR
        value: ""
''') {
    node(POD_LABEL) {
        git 'https://github.com/ciscops/colabot.git'
        container('docker') {
            stage('Clone repository') {
                scmVars = checkout scm
                sh "echo '${env}'"
                sh "echo '${env.JOB_NAME}'"
                branch = getBranch()
                sh "echo '${branch}'"
                sh "echo '${scmVars.GIT_BRANCH}'"
                sh "echo '${scmVars}'"
// + echo '[GIT_BRANCH:origin/master, GIT_COMMIT:aa6f29de1a5f3c5f33c6631cab409b5d7f0f2ab2, GIT_PREVIOUS_COMMIT:aa6f29de1a5f3c5f33c6631cab409b5d7f0f2ab2, GIT_PREVIOUS_SUCCESSFUL_COMMIT:aa6f29de1a5f3c5f33c6631cab409b5d7f0f2ab2, GIT_URL:https://github.com/ciscops/colabot.git]'
// [GIT_BRANCH:origin/master, GIT_COMMIT:aa6f29de1a5f3c5f33c6631cab409b5d7f0f2ab2, GIT_PREVIOUS_COMMIT:aa6f29de1a5f3c5f33c6631cab409b5d7f0f2ab2, GIT_PREVIOUS_SUCCESSFUL_COMMIT:aa6f29de1a5f3c5f33c6631cab409b5d7f0f2ab2, GIT_URL:https://github.com/ciscops/colabot.git]
                sh 'echo this step works7'
            }
//             stage('Test dev') {
//                 when {
//                     branch 'dev'
//                     }
//                 sh 'echo this the dev branch'
//             }
//             stage('Test master') {
//                 when {
//                     branch 'master'
//                     }
//                 sh 'echo this the master branch'
//             }
            stage('Build image') {
                if ( "${branch}" == "master" ) {
                    sh 'echo this is the master branch'
// 					imageName = "stmosher/colabot-prod"
				} else if ( "${branch}" == "dev" ) {
				    sh 'echo this is the dev branch'
//         			imageName = "stmosher/colabot-dev"
				}
                colabot = docker.build(imageName)
                sh "echo '${env.BUILD_NUMBER}'"
            }
//             stage('Test image') {
//                 colabot.inside {
//                     sh 'python --version'
//                 }
//             }
//             stage('Push image') {
//                 docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
//                     colabot.push("${env.BUILD_NUMBER}")
//                     colabot.push("latest")
//                 }
//             }
        }
    }
}

def getBranch() {
    tokens = "${env.JOB_NAME}".tokenize('/')
    branch = tokens[tokens.size()-1]
    return "${branch}"
}
// #!groovy
// // Parameters to define in the CloudBees UI in order for this job to work:
// // * CODE_BRANCH
//
// def Credentials = 'Abhay@1988'
// def dockerImageName = 'docker-datadog'
// def repoUrl = 'https://github.com/AbhayBhovi/test-jenkinsfile.git'
// def customImage = ""
//
// node('master') {
// 	timestamps {
// 		wrap([$class: 'AnsiColorBuildWrapper', 'colorMapName': 'xterm']) {
// 			stage ('build') {
// 				dir('my-code-checkout') {
// 					scmVars = checkout scm
// 					if ( "${scmVars.GIT_BRANCH}" == "master" ) {
// 							customImage = docker.build(dockerImageName + ":1.0-${env.BUILD_NUMBER}", "docker")
// 						} else {
//         						customImage = docker.build(dockerImageName + ":1.0-${scmVars.GIT_BRANCH.replace("/", "-")}-${env.BUILD_NUMBER}", "docker")
// 						}
//
// 						/* Push the container to the custom Registry */
// 						customImage.push()
// 				}
// 			}
// 		}
// 	}
// }