/**
 * This node js file obtains all the "Admin" tokens for the Virl2 Serves
 * It is for resetting a user password, checking if a user is part of the Virl2 Servers, and Creating a new user account
 * 
 */
// virlServersList = require("./variables/serverList.js")
// virlServers = virlServersList.serverList
// virlServers = ['https://cpn-sjc-virl1.ciscops.net']
virlServers = []
virlServers = process.env.SERVER_LIST.split(',');
virlServersToken = []
var request = require("request");
// var adminInfo = require("./variables/adminInformation.json")
var adminInfo = {
    adminUsername: process.env.VIRL_USERNAME,
    adminPassword: process.env.VIRL_PASSWORD
}

for(i=0;i<virlServers.length;i++)
{
    virlServerURL = virlServers[i]
    var options = {
        method: 'POST',
        url: virlServerURL+'/api/v0/authenticate',
        rejectUnauthorized: false,
        headers: 
        { 
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': "no-cache" 
        },
        body: { username: adminInfo["adminUsername"], password: adminInfo["adminPassword"]},
        json: true 
    };

    request(options, function (error, response, body) 
    {
        if (!error && body["code"]==null)
        {
            virlServersToken.push({"url":virlServerURL,"token":body})
        }
    });
}

module.exports.virlServersTokens = virlServersToken
