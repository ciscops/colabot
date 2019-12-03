/**
 * Botkit Controller Fallback command When a command isn't understood
 * 
 * Command : *Unknown Command, Not Help,List,Show,Create,Reset*
 * 
 * Order=>
 * Inform User that the Command is not Understood and they Should try the command Help
 */
module.exports = function (controller) {

    controller.hears(["(.*)"], 'direct_message,direct_mention', function (bot, message) {
        username = message.user.substring(0, message.user.lastIndexOf("@"))
        var mardown = "@"+ username+ " Sorry, I did not understand.<br/>Please Try the command: "
            + bot.enrichCommand(message, "HELP");
            
        bot.reply(message, mardown);
    });
}