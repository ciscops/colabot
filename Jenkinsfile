podTemplate(
  namespace: "default",
  serviceAccount: "colabot-build",
  yaml: '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: docker
    image: docker:19.03.8
    command:
    - sleep
    args:
    - 99d
    env:
      - name: DOCKER_HOST
        value: tcp://localhost:2375
  - name: docker-daemon
    image: docker:19.03.8-dind
    securityContext:
      privileged: true
    env:
      - name: DOCKER_TLS_CERTDIR
        value: ""
  - name: kubectl
    image: ciscops/kubectl
    command: ["sleep"]
    args: ["100000"]
''') {
    node(POD_LABEL) {
        container('docker') {
            stage('Clone repository') {
                checkout scm
                sh "echo '${env.JOB_NAME}'"
                branch = getBranch()
                sh "echo '${branch}'"
            }
            stage('Build container') {
                if ( "${branch}" == "master" ) {
					imageName = "ciscops/colabot-prod"
				} else if ( "${branch}" == "dev" ) {
        			imageName = "ciscops/colabot-dev"
				}
                colabot = docker.build(imageName)
            }
            stage('Push container to docker hub ') {
                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
                    colabot.push("${env.BUILD_NUMBER}")
                    colabot.push("latest")
                }
            }
        }
        container("kubectl") {
            stage('Clone k8s manifest') {
                sh "apk update"
                sh "apk upgrade"
                sh "apk add git"
                sh 'git config --global credential.helper cache'
                withCredentials([usernamePassword(credentialsId: 'github', passwordVariable: 'pass', usernameVariable: 'user')]) {
                    sh 'git clone https://"$user":"$pass"@github.com/ciscops/colabot-private.git'
                    }
		    }
            stage('Apply new COLABot-dev to K8s cluster') {
                if ( "${branch}" == "dev" ) {
                    sh "kubectl apply -f colabot-private/colabot_dev/colabot-dev.yaml"
                    sh "kubectl rollout restart deployment/colabot-dev-1"
                    sh 'echo Finished'
                } else if ( "${branch}" == "master" ) {
                    sh "kubectl apply -f colabot-private/colabot_prod/colabot-prod.yaml"
                    sh "kubectl rollout restart deployment/colabot-prod-1"
                    sh 'echo Finished'
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
