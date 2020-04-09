podTemplate(yaml: '''
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
            stage('Build container') {
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
            stage('Push container to docker hub ') {
                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
                    colabot.push("${env.BUILD_NUMBER}")
                    colabot.push("latest")
                }
            }
            stage('Clone k8s manifest') {
                if ( "${branch}" == "dev" ) {
                    sh "apk add git"
                    sh 'git config --global credential.helper cache'
                    withCredentials([usernamePassword(credentialsId: 'github', passwordVariable: 'pass', usernameVariable: 'user')]) {
                        sh 'git clone https://"$user":"$pass"@github.com/ciscops/colabot-private.git'
                        }
				} else if ( "${branch}" == "master" ) {
        			sh 'echo skipping clone k8s manifest'
			    }
		    }
            stage('Install k8s client') {
                if ( "${branch}" == "dev" ) {
                    sh "apk add curl"
                    sh 'k8sversion=v1.14.6'
                    sh 'curl -LO https://storage.googleapis.com/kubernetes-release/release/$k8sversion/bin/linux/amd64/kubectl'
                    sh 'pwd'
                    sh 'ls /home/jenkins/agent/workspace/colabot_dev_and_prod_dev'
                    sh "chmod +x ./kubectl"
                    sh 'cp ./kubectl /usr/local/bin/kubectl'
                    sh 'export KUBECONFIG=kubeconfig.yaml'
                    sh 'pwd'
                    sh 'ls -alF /usr/local/bin/'
                    sh 'kubectl get pods'
                    sh "/home/jenkins/agent/workspace/colabot_dev_and_prod_dev/kubectl get pods"
				} else if ( "${branch}" == "master" ) {
        			sh 'echo skipping Install k8s client'
                }
            }
            stage('Apply new COLABot-dev to K8s cluster') {
                if ( "${branch}" == "dev" ) {
                    sh "/usr/local/bin/kubectl delete -f colabot-private/colabot_dev/colabot-dev.yaml"
                    sh "/usr/local/bin/kubectl create -f colabot-private/colabot_dev/colabot-dev.yaml"
                    sh 'echo Finished'
                } else if ( "${branch}" == "master" ) {
        			sh 'echo skipping Apply new COLABot-dev to K8s cluster'
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
