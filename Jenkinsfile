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
                checkout scm
                sh "echo '${env.JOB_NAME}'"
                branch = getBranch()
                sh "echo '${branch}'"
            }
            stage('Build image') {
                if ( "${branch}" == "master" ) {
					imageName = "stmosher/colabot-prod"
				} else if ( "${branch}" == "dev" ) {
        			imageName = "stmosher/colabot-dev"
				}
                colabot = docker.build(imageName)
            }
//             stage('Test image') {
//                 colabot.inside {
//                     sh 'python --version'
//                 }
//             }
            stage('Push image') {
                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
                    colabot.push("${env.BUILD_NUMBER}")
                    colabot.push("latest")
                }
            }
        }
    }
}

def getBranch() {
    tokens = "${env.JOB_NAME}".tokenize('/')
    branch = tokens[tokens.size()-1]
    return "${branch}"
}
