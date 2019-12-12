# colabot
WebEx Teams user self-service bot for CIDR

## Deploying locally with docker-compose

Create a file called `botkit-vars.env` in the local directory with the folling environment variables set for your environment:
```
# Environment Config

# store your secrets and config variables in here
# only invited collaborators will be able to see your .env values
# reference these in your code with process.env.SECRET

ACCESS_TOKEN=[YOUR ACCESS TOKEN]
PUBLIC_URL=https://colabot.example.com
SERVER_LIST=https://server1.example.com,https://server2.example.com
VIRL_USERNAME=virl
VIRL_PASSWORD=foo
DEBUG=*
# note .env is a shell file so there can't be spaces around =
```
> Note: replace 
Then build and run the bot.
```
docker-compose up
```
