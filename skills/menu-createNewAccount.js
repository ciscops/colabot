/**
 * Botkit Controller to Create a New User on the VIRL2 Servers
 * 
 * Command : create
 * 
 * Order=>
 * Ask if they want Account
 *      Yes->Try to Create Account 
 *          Error=>Request Error
 *          Exists=>User Already Exists (Informs User to Reset Password or Help Menu)
 *          Added=>User Added (New Password shown)
 *      No-> Informs User they need an account to access commands
 */
module.exports = function (controller) {

    controller.hears(["^create"], 'direct_message,direct_mention', function (bot, message) {
        serverList = require('./getAccessTokens.js')
        virlServers = serverList.virlServersTokens//Get List of Virl2 Servers
        username = message.user.substring(0, message.user.lastIndexOf("@"))//Obtain Username 
        generateNewPassword = require('./generateRandomPassword.js')
        newPassword = generateNewPassword.randomPasswordGenerator()//Generate Random User Password
        bot.startPrivateConversationWithPersonId(message.data["personId"], function (err, convo) {
            convo.ask("@"+ username+ " Would you like to create an account?</br>(<strong>YES | NO</strong>)" ,[
                {
                    pattern:"yes",
                    callback: function(response,convo){
                        newUser = require('./adduser.js')
                        newUser.addNewUser(message,newPassword).then(body=>{
                            createdUser = body.slice(-virlServers.length)
                            convo.next()
                            if(createdUser.lastIndexOf("error")>-1)
                            {
                                console.log("Error Add User")
                                convo.gotoThread("error");
                    
                            }
                            if(createdUser.lastIndexOf("exists")>-1)
                            {
                                console.log("User Exists")
                                convo.gotoThread("exists");
                    
                            }
                            if(createdUser.length == 0)
                            {
                                console.log("ERROR WITH REQUEST")
                                convo.gotoThread("errorRequest");
                            }
                            else
                            {
                                console.log("User Added")
                                convo.gotoThread("added");
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
                    text: "Understood<br>You need an account before you can access the Virl2 Commands"
                },
                "noNewUser"
                )
                convo.addMessage({
                    text: "I'm sorry, I did not understand your reply. <br>",
                    action: "default",
                },
                "unknownAnswer"
                )
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
                convo.addMessage({
                    text: "Sorry @" + username + ", I am having some trouble creating your account<br>Please Try Again.",
                },
                "errorRequest"
                )

        })
    });
}