/**
 * This JS File creates a user on each of the VIRL2 Servers
 * It utilizes the ADMIN Tokens of the Virl2 Servers
 */

/**
 * Function to Add a new User to the Virl Servers
 * It creates a random password for the user
 * @param {*} message  Message sent by the User
 * @param {*} newPassword New Password For the User
 */
userAdded = []
async function addNewUser(message,newPassword)
{
    
    serverList = require('./getAccessTokens.js')
    virlServers = serverList.virlServersTokens
    userEmail = message.user
    username = message.user.substring(0, message.user.lastIndexOf("@"))
    request = require("request");
    userInfo ={
        "password": newPassword,
        "fullname": userEmail,
        "description": "",
        "roles": [
          "User"
        ],
        "context": {}
    }
    for(i=0;i<virlServers.length;i++)
    {
        virlUrl = virlServers[i]["url"]
        virlToken = virlServers[i]["token"]
        var options = {
            method: 'POST',
            url: virlUrl+'/api/v0/users/'+username,
            rejectUnauthorized: false,
            headers: 
            { 
                'Accept': 'application/json',
                'cache-control': "no-cache" ,
                "Authorization":"Bearer "+virlToken
            },
            body: userInfo,
            json: true 
        };
        userAdded.push(new Promise((resolve,reject)=>{
            request(options, function (error, body) 
            {
                if (error)
                {
                    console.log(error)
                    reject(error)
                } 
                else
                {
                    if(body.body == "OK")
                    {
                        resolve("added")
                    }
                    if(body.body["description"] == "User already exists: " + username + ".")
                    {
                        resolve("exists")
                    }
                    else
                    {
                        resolve("error")
                    }
                                        
                }
            });
        }))
        
    }
    return Promise.all(userAdded)

}

module.exports.addNewUser = addNewUser