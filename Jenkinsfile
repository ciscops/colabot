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
        def colabot
        git 'https://github.com/ciscops/colabot.git'
        container('docker') {
            stage('Clone repository') {
                checkout scm
            }
            stage('Build image') {
                colabot = docker.build("jasonking/colabot")
            }
            stage('Test image') {
                colabot.inside {
                    sh 'node --version'
                }
            }
            stage('Push image') {
                docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-credentials') {
                    colabot.push("${env.BUILD_NUMBER}")
                    colabot.push("latest")
                }
            }             
        }
    }
}