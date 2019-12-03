var rp = require('request-promise');
var Promise = require('promise');
var debug = require('debug')('pcap');

var help_text = 'Hello!  I am colabot!';

module.exports = function(controller) {

    controller.hears(['help'], 'direct_message,direct_mention', function(bot, message) {
        bot.reply(message, help_text);
    });

    controller.hears(['.*'], 'direct_message,direct_mention', function(bot, message) {
        bot.reply(message, 'I\'m sorry, I did not understand your request.  Try asking me for help using the **help** command.');
    });
    
};

