# COLABot
WebEx Teams user self-service bot for CIDR Group

## Installation
#### Local
Build a COLABot image using the Dockerfile.

Ensure you pass in the appropriate environment vars2 required in the config.py file.


### Pipeline
The GitHub [COLABot](https://github.com/ciscops/colabot) repository is configured to initiate a Jenkins build 
(send webhook to build server) upon receipt of a "push". The Jenkins server is configured to execute the build according
 to the Jenkinsfile located at the root of this repository. 


A push to the dev branch will build a new image, push to docker hub, and deploy in CPN Kubernetes.


A push to the master branch will build a new image and push to docker hub. 

## Details
The COLABot app is a web server that receives WebHooks from WebEx Teams for direct messages or mentions to the WebEx Teams
bot COLABot. 

Program configuration including needed environment variable import statements are found in config.py.

The app.py file starts the web server.

Upon reception of a web hook, the app.py passes the web message to bot.py.

bot.py:
  - Authenticates the web hook msg
  - Creates an "activity" dictionary from the web hook
  - Updates the activity with previous dialogue information from MongoDB if appropriate
  - Passes the activity to a matching feature for further processing
  - If not a feature match, passes the activity to the catch-all

## To add new Features
1. Add new feature python file(s) in ./features
2. In bot.py
    - import new feature
    - Add help description to list $help_menu_list 
    - add elif to match new feature(s) between
        - '# Start Add elif for new Feature' ----> and '# End Add elif for new Feature ---->'
