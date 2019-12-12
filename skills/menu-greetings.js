/**
 * Botkit Controller to Serve As the Main Greeting/Landing Page when the Bot is Greeted with a Hello or Help
 * 
 * Command : Help, Hello, Hi
 * 
 * Order=>
 * Shows the Current List of menu itemsfor Virl2 Commands
 *          -Create (Create User Account)
 *          -Reset (Reset User's Password)
 *          -List  (List User's Lab)
 *          -Show (Show Detail of User's Lab)
 *          -Help (Show this Help Menu)
 */
module.exports = function (controller) {

    controller.hears(["hello", "hi","help"], 'direct_message,direct_mention', function (bot, message) {
        bot.startConversation(message,function(err,convo)
        {
            var menuText = "Here are my List of Options:";
            menuText += "\n- " + bot.enrichCommand(message, "Create ") + "Account: Will Create an Account on the Virl2 Servers";
            menuText += "\n- " + bot.enrichCommand(message, "Reset ") + "Password: Will Reset Your Password";
            menuText += "\n- " + bot.enrichCommand(message, "List ") + "Labs: Will List Your Current Labs";
            menuText += "\n- " + bot.enrichCommand(message, "Show ") + "Lab Details: Will List Details of Lab specified by Lab ID";
            menuText += "\n- " + bot.enrichCommand(message, "Help ") + ": Will Reload This Main Menu";
            convo.say('Hi, I am the VIRL2 Bot </br>My Role is to help you with getting started in VIRL2!<br/>'+ menuText)
        })
    });

}

