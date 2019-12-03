/**
 * Botkit Controller to list a User's Labs on the Virl2 Servers
 * 
 * Command : list
 * 
 * Order=>
 * Check if User has An Account
 *      Yes-> Ask to Enter Password (for User Tokens)
 *              Auth Failed-> Alert User their Auth has Failed
 *              Auth Passed-> Try to Show labs
 *                  No Labs-> Tell User there are no Labs to Show
 *                  Labs-> Display Labs 
 *      No-> Ask if they want to Create Account
 *              Yes-> Create Account, return new Password
 *              No-> Inform User they need account to utilize Virl2 Commands
 */
userServers = require("./getAccessTokenUser.js")
module.exports = function (controller) {

    controller.hears(["^list"], 'direct_message,direct_mention', function (bot, message) {
        bot.startConversation(message,function(err,convo)
        {
            serverList = require('./getAccessTokens.js')
            virlServers = serverList.virlServersTokens
            username = message.user.substring(0, message.user.lastIndexOf("@"))
            checkUser = require('./checkuser.js')
            checkTheUser = checkUser.checkTheUser(username)
            checkTheUser.then(body =>{
                userResult = body.slice(-virlServers.length)
                console.log(body)
                personID = message.data["personId"]
                if(userResult.lastIndexOf("false")>-1)
                {
                    convo.stop()
                    generateNewPassword = require('./generateRandomPassword.js')
                    newPassword = generateNewPassword.randomPasswordGenerator()
                    bot.startPrivateConversationWithPersonId(personID, function (err, convo) {
                        convo.ask("@"+ username+ ", You Do Not have an account<br>Would you like to create an account?</br>(<strong>YES | NO</strong>)" ,[
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
                                    convo.next()
                                    convo.gotoThread("noNewUser");
                                    convo.next()
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
                    convo.say("")
                    convo.stop()
                    bot.startPrivateConversationWithPersonId(personID, function (err, convo) {
                        convo.ask("@" + username + ", Please Enter Your Password</br>" ,[
                            {

                                default: true,
                                callback: function(response,convo){
                                    convo.next()
                                    getListLabs(convo,username,response.text)
                                }
                            }
                            ],{key: "password"});
                    })
                    //
                }
            })
        })
    });
}


/**
 * Function to get the User's Labs
 * 
 * @param {*} convo Conversation with User
 * @param {*} username Username for User
 * @param {*} userpassword User Password
 */
function getListLabs(convo,username,userpassword)
{
    convo.next()
    serverList = require('./getAccessTokens.js')
    virlServers = serverList.virlServersTokens
    userServers = require("./getAccessTokenUser.js")
    userserverList = userServers.getUserAccessToken(username,userpassword)
    request = require("request");
    userserverList.then(body=>{
        userTokenList = body.slice(-virlServers.length)
        if(userTokenList.lastIndexOf("Failed")>-1)
        {
            console.log("Failed Authentication")
            convo.say('Sorry @' + username + ', Authentication Failed </br>Please Try Again')
            convo.next()

        }
        else
        {
            var labString = ""
            for(i=0;i<userTokenList.length;i++)
            {
                virlUrl = userTokenList[i]["url"]
                virlToken = userTokenList[i]["token"]
                var options = {
                    method: 'GET',
                    url: virlUrl+'/api/v0/labs',
                    rejectUnauthorized: false,
                    headers: 
                    { 
                        'Accept': 'application/json',
                        'cache-control': "no-cache" ,
                        "Authorization":"Bearer "+virlToken
                    }
                };
                
                request(options, function (error, response, body) 
                {
                    if (error)
                    {
                        convo.say('Sorry @' + username + ', I cannot obtain your list of labs')
                    } 
                    else
                    {
                        console.log(body)
                        var labList = JSON.parse(body)
                        if(labList["code"] == null)
                        {
                            for(i=0;i<labList.length;i++)
                            {
                                if(labList.length == 1)
                                {
                                    labString = "Lab ID: " + labList[i]
                                }
                                else
                                {
                                    labString += "Lab ID: " + labList[i] + "<br>"
                                }
                            }
                            if(labString == "")
                            {
                                console.log("EMPTY LABS")
                                convo.say("Sorry @" + username + ", You have no labs to show")
                                convo.next()                                
                            }
                            else
                            {
                                convo.say("<strong>" + labString + "</strong>")
                                convo.next()                                
                            }
                            
                        }
                        else
                        {
                            convo.say('Sorry @' + username + ', I cannot obtain your list of labs')
                            convo.next()
                        }
                    }
                    
                });
            }
        }
    }).catch(err=>{
        console.log("This the err " + err)
        convo.say('Sorry @' + username + ', I cannot obtain your list of labs')
        convo.next()
    })

}


