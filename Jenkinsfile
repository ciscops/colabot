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
//         git 'https://github.com/ciscops/colabot.git'
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
            stage('Install k8s client') {
                sh "apk add curl"
                sh 'k8sversion=v1.14.6'
                sh 'curl -LO https://storage.googleapis.com/kubernetes-release/release/$k8sversion/bin/linux/amd64/kubectl'
                sh "chmod +x ./kubectl"
                sh 'mv ./kubectl /usr/local/bin/kubectl'
                }

            stage('Clone repository') {
                sh "apk add git"
                sh 'git config --global credential.helper cache'
                withCredentials([usernamePassword(credentialsId: 'hello-kb', passwordVariable: 'pass', usernameVariable: 'user')]) {
                    // the code in here can access $pass and $user
                    sh 'git clone https://"$user":"$pass"@github.com/ciscops/colabot-private.git'
                }
                sh "ls"
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
