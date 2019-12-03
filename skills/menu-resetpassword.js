/**
 * Botkit Controller to Rest a User's Password on the Virl2 Servers
 * 
 * Command : reset
 * 
 * Order=>
 * Check if User has An Account
 *      Yes-> Ask if they want to Reset Password
 *              Yes-> Reset Password
 *              No-> Old Password Kept 
 *      No-> Ask if they want to Create Account
 *              Yes-> Create Account, return new Password
 *              No-> Inform User they need account to utilize Virl2 Commands
 */
module.exports = function (controller) {

    controller.hears(["reset"], 'direct_message,direct_mention', function (bot, message) {
        bot.startConversation(message,function(err,convo)
        {
                serverList = require('./getAccessTokens.js')
                virlServers = serverList.virlServersTokens
                username = message.user.substring(0, message.user.lastIndexOf("@"))
                checkUser = require('./checkuser.js')
                checkTheUser = checkUser.checkTheUser(username)
                checkTheUser.then(body =>{
                    userResult = body.slice(-virlServers.length)
                    personID = message.data["personId"]
                    if(userResult.lastIndexOf("false")>-1)
                    {
                        convo.stop()
                        generateNewPassword = require('./generateRandomPassword.js')
                        newPassword = generateNewPassword.randomPasswordGenerator()
                        bot.startPrivateConversationWithPersonId(personID, function (err, convo) {
                            convo.ask("@"+ username+ " You Do Not have an account, Would you like to create an account?</br>(<strong>YES | NO</strong>)" ,[
                                    {
                                        pattern:"yes",
                                        callback: function(response,convo){
                                        newUser = require('./adduser.js')
                                        newUser.addNewUser(message,newPassword).then(body=>{
                                            createdUser = body
                                            convo.next()
                                            if(createdUser.lastIndexOf("error")>-1)
                                            {
                                                console.log("FAILED to Add User")
                                                convo.gotoThread("error");
                                    
                                            }
                                            if(createdUser.lastIndexOf("exists")>-1)
                                            {
                                                console.log("User Exists")
                                                convo.gotoThread("exists");
                                    
                                            }
                                            else
                                            {
                                                convo.gotoThread("added");
                                                convo.next()
                                            }
                                        })
                                        }
                                    }, 
                                    {
                                        pattern:"no",
                                        callback: function(response,convo){
                                            convo.gotoThread("noNewUser");
                                        }
                                    },
                                    {
                                        default: true,
                                        callback: function(response,convo){
                                            convo.gotoThread("unknownAnswer");
                                        }
                                    }
                                    ],{key: "answer"});
                                    convo.addMessage({
                                    text: "Understood<br>You'll need to create an account before you can access the Virl2 Commands"
                                },
                                "noNewUser"
                                )
                                convo.addMessage({
                                    text: "I'm sorry, I did not understand your reply. <br>",
                                    action: "default",
                                },
                                "unknownAnswer"
                                ),
                                convo.addMessage({
                                    text: "Great<br>Your Account Has been Created.<br>Your password is <strong>" + newPassword + "</strong>",
                                },
                                "added"
                                )
                                convo.addMessage({
                                    text: "Sorry @" + username + ", Your Account has already been created<br>Please try the command <strong>Reset</strong> to reset your password<br>Or <strong>Help</strong> to reload the Main Menu",
                                },
                                "exists"
                                )
                                convo.addMessage({
                                    text: "Sorry @" + username + ", Authentication Failed </br>Please Try Again",
                                },
                                "error"
                                )
                    
                                })
                    }
                    if(userResult.length == 0)
                    {
                        convo.say("")
                        convo.next()
                        bot.startPrivateConversationWithPersonId(personID, function (err, convo) {
                            convo.say("I'm sorry I am having some trouble obtaining your information<br>Please try again.")
                            convo.next()
                        })
                        
                    }
                    else
                    {
                        convo.ask("@"+ username+ ", Are you sure you want to change your password?</br>(<strong>YES | NO</strong>)",[
                            {
                                pattern:"^yes",
                                callback: function(response,convo){
                                    convo.next()
                                    bot.startPrivateConversationWithPersonId(personID, function (err, convo) {
                                        convo.next()
                                        generateNewPassword = require('./generateRandomPassword.js')
                                        newPassword = generateNewPassword.randomPasswordGenerator()
                                        resetPassword(convo,username,newPassword)
                                    })
                                    
                                }
                            },
                            {
                                pattern:"^no",
                                callback: function(response,convo){
                                    convo.gotoThread("keepPassword")
                                    convo.next()
                                }
                            },
                            {
                                default: true,
                                callback: function(response,convo){
                                    convo.gotoThread("unknownAnswer");
                                    convo.next();
                                }
                            }
                
                            ],{key: "answer"});
                
                            convo.addMessage({
                                text: "@"+ username+ ", Understood<br>Your Password will not change"
                            },
                            "keepPassword"
                            )
                            convo.addMessage({
                                text: "@"+ username+ " I'm sorry, I did not understand your reply. <br>",
                                action: "default",
                            },
                            "unknownAnswer"
                            )
                }
            })
        })
    });

    }

/**
 * Function to Reset the User's Password through each Virl2 Server
 * @param {*} convo Botkit Conversation with the User
 * @param {*} userName UserName of User
 * @param {*} newPassword New Password of User
 */
function resetPassword(convo,userName,newPassword)
{
    serverList = require('./getAccessTokens.js')
    virlServers = serverList.virlServersTokens
    resetAllPasswords(userName,newPassword).then(function(results){
        resetPasswords = results.splice(-virlServers.length)
        convo.next()
        if(resetPasswords.lastIndexOf("error")>-1)
        {
            console.log("Error New Password")
            convo.say("Sorry @" + username + ", I could not reset your password")
            convo.next()

        }
        if(resetPasswords.lastIndexOf("false")>-1)
        {
            console.log("Failed New Password")
            convo.say("Sorry @" + username + ", I could not reset your password")
            convo.next()

        }
        else
        {
            convo.say("Password Changed!<br>@" + username + ", here is your new password <br><strong>" + newPassword + "</strong>")
            convo.next()

        }
        
    })
    
}

/**
 * Function that resets the Password for each Virl2 Server
 * Returns an Array to see if User has been added to all Servers
 * 
 * @param {*} userName Username of User
 * @param {*} newPassword New Password of User
 */
async function resetAllPasswords(userName,newPassword)
{
    var request = require("request");
    serverList = require('./getAccessTokens.js')
    virlServers = serverList.virlServersTokens
    requestResults = [];
    for(i=0;i<virlServers.length;i++)
    {
        virlUrl = virlServers[i]["url"]
        virlToken = virlServers[i]["token"]

        var options = {
            method: 'PUT',
            url: virlServerURL+'/api/v0/users/'+userName+'/change_password',
            rejectUnauthorized: false,
            headers: 
            { 
                'Accept': 'application/json',
                'cache-control': "no-cache" ,
                "Authorization":"Bearer "+virlToken
            },
            body: { "old_password": '', "new_password": newPassword },
            json: true
        };
        requestResults.push(new Promise((resolve,reject)=>{
            request(options, function (error, body) 
            {
                if(error)
                {
                    resolve("error")
                }
                else{
                    resolve("true")
                }
            });
        }))
        
    }
    return Promise.all(requestResults)
}