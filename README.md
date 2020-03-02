# colabot
WebEx Teams user self-service bot for CIDR Group

## Deploying locally with docker-compose

Create a file called `.env` in the local directory with the following environment variables set for your environment:
```
# Environment Config

# store your secrets and config variables in here
# only invited collaborators will be able to see your .env values
# reference these in your code with process.env.SECRET

ACCESS_TOKEN=[YOUR ACCESS TOKEN]
PUBLIC_ADDRESS=https://colabot.example.com
SERVER_LIST=server1.example.com,server2.example.com,server3.example.com
VIRL_USERNAME=virl
VIRL_PASSWORD=foo
SECRET=foo
MONGO_INITDB_ROOT_USERNAME=cisco
MONGO_INITDB_ROOT_PASSWORD=password
MONGO_SERVER=mongodb.example.com
MONGO_PORT=27017
MONGO_DB=myproject
MONGO_COLLECTIONS=documents
APPROVED_ORG_DOMAINS=example1.com,example2.com,example3.com
// Add the below 2 lines if you are logging to the DB; Also uncomment the appropriate lines in ./bot.js
MONGO_DB_ACTIVITY=default
MONGO_COLLECTIONS_ACTIVITY=default
DEBUG=*
# note .env is a shell file so there can't be spaces around =
```

To locally build and run the bot:
```
docker-compose up
```
