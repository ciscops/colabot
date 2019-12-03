/**
 * Botkit Controller to Show the Details of a Specifc Lab on Virl2 Servers
 * 
 * Command : show
 * 
 * Order=>
 * Check if User has An Account
 *      Yes-> Ask to Enter Password (for User Tokens)
 *              Auth Failed-> Alert User their Auth has Failed
 *              Auth Passed-> Ask User for Lab ID
 *                  No Information-> Tell User Cannot obtain Labs Details
 *                  Information-> Display Lab information (ID,Title,Description,Node Count,Link Count,State,Created Date)
 *      No-> Ask if they want to Create Account
 *              Yes-> Create Account, return new Password
 *              No-> Inform User they need account to utilize Virl2 Commands
 */
module.exports =   function (controller) {
    controller.hears(["^show"], 'direct_message,direct_mention', function (bot, message) {
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
                        convo.ask("@"+ username+ " Please Enter Your Password</br>" ,[
                            {
                                default: true,
                                callback: function(response,convo){
                                    
                                    return getLabDetails(convo,username,response.text)
                                    
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
 * Function to Obtain the Lab Details of a Specific Lab on the Virl2 Servers
 * 
 * @param {*} convo User Conversation
 * @param {*} username Username of User
 * @param {*} userpassword User Password
 */
function getLabDetails(convo,username,userpassword)
{
    convo.next()
    userServers = require("./getAccessTokenUser.js")
    userserverList = userServers.getUserAccessToken(username,userpassword)
    request = require("request");
    userserverList.then(body=>{
        userTokenList = body.slice(-virlServers.length)
        if(userTokenList.lastIndexOf("Failed")>-1)
        {
            console.log("FAILED Authentication")
            convo.say('Sorry @' + username + ', Authentication Failed </br>Please Try Again')
            convo.next()

        }
        else
        {
            convo.next()
            convo.ask("Please Enter <strong>LAB ID</strong>",function(response,convo)
            {
                convo.setVar('labID',response.text)
                for(i=0;i<userTokenList.length;i++)
                {
                    virlUrl = userTokenList[i]["url"]
                    virlToken = userTokenList[i]["token"]
                    var options = {
                        method: 'GET',
                        url: virlUrl+'/api/v0/labs/'+response.text,
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
                            console.log(error)
                            convo.say("Sorry I cannot obtain your lab: <strong>" + response.text + "</strong>" )
                            convo.next()
                        } 
                        else
                        {
                            getResponse(body,convo)
                            
                        }
                    
                    });
                }

            })

        }
    }).catch(err=>{
        console.log("This the err " + err)
        convo.say('Sorry @' + username + ', I cannot obtain your list of labs')
        convo.next()
    })    
}

/**
 * Function to Return a Formatted Version of the Lab Details
 * 
 * @param {*} body Return Body of HTTP Request to Obtain Lab Information
 * @param {*} convo User Conversation
 */
function getResponse(body,convo)
{
    convo.next()
    returnData = JSON.parse(body)
    labID = convo.vars.labID
    if(returnData['id'] != null)
    {
        returnDataString = "</br><strong>ID</strong>: " + returnData['id'] +
        "</br><strong>Title</strong>: " + returnData['lab_title'] +
        "</br><strong>Description</strong>: " + returnData['lab_description'] +
        "</br><strong>Node Count</strong>: " + returnData['node_count'] +
        "</br><strong>Link Count</strong>: " + returnData['link_count'] +
        "</br><strong>State</strong>: " + returnData['state'] +
        "</br><strong>Created</strong>: " + new Date(returnData['created']).toLocaleDateString()
        
        convo.say("Lab Information =></br>" + returnDataString )
    }
    else
    {
        convo.say("Cannot Obtain Data for Lab: " + labID)
    }
    convo.next()
}