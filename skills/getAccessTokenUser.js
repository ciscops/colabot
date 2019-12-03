/**
 * This node js file obtains the Tokens Specific for a User through each of the Virl2 Servers
 * It requires the user's username and password  
 * It is for obtianing the list of labs for a user as well as obtianing the details of specific labs for the user
 * 
 */


userVirlServersToken = []
serversList = require("./variables/serverList.js")
servers = serversList.serverList
async function getUserAccessToken(userName,userPassword)
{
    var request = require("request");
    for(i=0;i<servers.length;i++)
    {
        userVirlServerURL = String(servers[i])
        var options = {
            method: 'POST',
            url: userVirlServerURL+'/api/v0/authenticate',
            rejectUnauthorized: false,
            headers: 
            { 
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'cache-control': "no-cache" 
            },
            body: { username: userName, password: userPassword },
            json: true 
        };
        userVirlServersToken.push(new Promise((resolve,reject)=>{
            request(options, function (error, body) 
            {
                if (error)
                {
                    console.log(error)
                    reject(error)
                } 
                else
                {
                    if(body.body == "Authentication failed!")
                    {
                        resolve("Failed")
                    }
                    else
                    {
                        resolve({"url":userVirlServerURL,"token":body.body})
                    }                    
                }
            });
        }))
        
    }
    return Promise.all(userVirlServersToken)
}


module.exports.getUserAccessToken = getUserAccessToken
module.exports.userVirlServersToken = userVirlServersToken
