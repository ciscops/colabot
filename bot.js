//  __   __  ___        ___
// |__) /  \  |  |__/ |  |  
// |__) \__/  |  |  \ |  |  

// This is the main file for the colabot bot.

// Import Botkit's core features
const {Botkit} = require('botkit');
const {BotkitCMSHelper} = require('botkit-plugin-cms');

// Import a platform-specific adapter for webex.

const {WebexAdapter} = require('botbuilder-adapter-webex');

const {MongoDbStorage} = require('botbuilder-storage-mongodb');

// Load process.env values from .env file
require('dotenv').config();

let storage = null;
if (process.env.MONGO_URI) {
    storage = mongoStorage = new MongoDbStorage({
        url: process.env.MONGO_URI,
    });
}

const adapter = new WebexAdapter({
    // REMOVE THIS OPTION AFTER YOU HAVE CONFIGURED YOUR APP!
    enable_incomplete: false,
    secret: process.env.SECRET,
    webhook_name: 'CoLabBot Webhook',
    access_token: process.env.ACCESS_TOKEN,
    public_address: process.env.PUBLIC_ADDRESS,
    // BELOW LINE ADDED BY CIDR
    limit_to_domain: process.env.APPROVED_ORG_DOMAINS.split(',')
})

const controller = new Botkit({
    webhook_uri: '/api/messages',

    adapter: adapter,

    storage
});

controller.commandHelp = [];
controller.checkAddMention = function (roomType, command) {

    var botName = adapter.identity.displayName;

    if (roomType === 'group') {

        return `\`@${botName} ${command}\``
    }

    return `\`${command}\``
};

if (process.env.CMS_URI) {
    controller.usePlugin(new BotkitCMSHelper({
        uri: process.env.CMS_URI,
        token: process.env.CMS_TOKEN,
    }));
}

// Once the bot has booted up its internal services, you can use them to do stuff.
controller.ready(() => {

    // load traditional developer-created local custom feature modules
    controller.loadModules(__dirname + '/features');

    /* catch-all that uses the CMS to trigger dialogs */
    if (controller.plugins.cms) {
        controller.on('message,direct_message', async (bot, message) => {
            let results = false;
            results = await controller.plugins.cms.testTrigger(bot, message);

            if (results !== false) {
                // do not continue middleware!
                return false;
            }
        });
    }

});


controller.webserver.get('/', (req, res) => {

    res.send(`This app is running Botkit ${controller.version}.`);

});

adapter.use(CheckDomainMiddleware);
async function CheckDomainMiddleware(turnContext, next) {
    if (turnContext._adapter.options.limit_to_domain) {
        var domains = [];
        if (typeof (turnContext._adapter.options.limit_to_domain) == 'string') {
            domains = [turnContext._adapter.options.limit_to_domain];
        } else {
            domains = turnContext._adapter.options.limit_to_domain;
        }

        let allowed = false;
        if (controller.adapter._identity.id === turnContext._activity.from.id) {
            allowed = true;
        } else {
            let d;
            for (d = 0; d < domains.length; d++) {
                let a = turnContext._activity.from.name.split('@');
                if (a[1].toLowerCase() == domains[d]) {
                    allowed = true;
                }
            }
        }

        if (!allowed) {
            console.warn('WARNING: Message received from ' + turnContext._activity.from.name);
            console.warn('WARNING - Allowed domains are: ', turnContext._adapter.options.limit_to_domain);
            return false;
        }
    }
    await next();
}

// adapter.use(LogToMongoDBMiddleware);
// async function LogToMongoDBMiddleware(turnContext, next) {
//     // console.log(turnContext._activity)
//     // or
//     // Below to log to a MongoDB
//     const MongoClient = require('mongodb').MongoClient;
//     const assert = require('assert');
//     const MONGO_INITDB_ROOT_USERNAME = process.env.MONGO_INITDB_ROOT_USERNAME;
//     const MONGO_INITDB_ROOT_PASSWORD = process.env.MONGO_INITDB_ROOT_PASSWORD;
//     const MONGO_SERVER = process.env.MONGO_SERVER;
//     const MONGO_PORT = process.env.MONGO_PORT;
//     const MONGO_DB_ACTIVITY = process.env.MONGO_DB_ACTIVITY;
//     const MONGO_COLLECTIONS_ACTIVITY = process.env.MONGO_COLLECTIONS_ACTIVITY;
//     if (MONGO_DB_ACTIVITY != 'default') {
//         const url = 'mongodb://' + MONGO_INITDB_ROOT_USERNAME + ':' + MONGO_INITDB_ROOT_PASSWORD + '@' + MONGO_SERVER + ':' + MONGO_PORT;
//         const client = new MongoClient(url, {useNewUrlParser: true});
//         let result = await client.connect();
//         if (result.s.url === undefined) {
//             console.log('Error connecting to database')
//         } else {
//             const db = await client.db(MONGO_DB_ACTIVITY);
//             const collection = await db.collection(MONGO_COLLECTIONS_ACTIVITY);
//             const record = await collection.insertOne(turnContext._activity);
//             console.log(record)
//         }
//     }
//         await next();
//     }