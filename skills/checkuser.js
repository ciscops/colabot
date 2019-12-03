/**
 * This File Checks to see if a User is Part of the Virl2 Servers List
 * 
 * To Obtain the return value of the Promise
 * EX:
 * checkuser = checkTheUser(username)
 * checkuser.then(body=>{//Do Something With Body}).catch(err=>{//Do Something With Error})
 * 
 * @param {*} username  //UserName of User who sent request
 */

arrayList = []
async function checkTheUser(userName)
{
    serverList = require('./getAccessTokens.js')
    virlServers = serverList.virlServersTokens
    var request = require("request");
    for(i=0;i<virlServers.length;i++)
    {
        virlUrl = virlServers[i]["url"]
        virlToken = virlServers[i]["token"]
        var options = {
            method: 'GET',
            url: virlUrl+'/api/v0/users/'+userName,
            rejectUnauthorized: false,
            headers: 
            { 
                'Accept': 'application/json',
                'cache-control': "no-cache" ,
                "Authorization":"Bearer "+virlToken
            }
        };
        arrayList.push(new Promise((resolve,reject)=>{
            request(options, function (error, body) 
            {
                if (error)
                {
                    console.log(error)
                    reject(error)
                } 
                else
                {
                    info = JSON.parse(body.body)
                    if(info["username"]!= null)
                    {
                        resolve("true")
                    }
                    else
                    {
                        resolve("false")
                    }
                                        
                }
            });
        }))
        
    }
    return Promise.all(arrayList)

}

module.exports.checkTheUser = checkTheUser



