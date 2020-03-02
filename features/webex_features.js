/**
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License.
 */

const { BotkitConversation } = require('botkit');

module.exports = function(controller) {

    const NEW_ROOM_DIALOG = 'new_room_dialog';
    const dialog = new BotkitConversation(NEW_ROOM_DIALOG, controller);
    dialog.say('I created this room so we could continue our conversation in private...');
    dialog.ask('How does that sound?', async(response, convo, bot) => {

    }, {key: 'how_it_sounds'});
    dialog.say('Ah, {{vars.how_it_sounds}}, eh?');
    dialog.say('I guess that is that.')

    controller.addDialog(dialog);

    controller.hears('delete','message,direct_message', async(bot, message) => {

        let reply = await bot.reply(message,'This message will be deleted in a few seconds.');
        setTimeout(async () => {
            let res = await bot.deleteMessage(reply);
        }, 5000);

    });


    controller.hears('create a room','message,direct_message', async(bot, message) => {

        // create a room
        let room = await bot.api.rooms.create({title: 'botkit test room'});

        // add user as member (bot is automatically added)
        let membership2 = await bot.api.memberships.create({
            roomId: room.id,
            personId: message.user,
        });

        await bot.startConversationInRoom(room.id, message.user);
        await bot.beginDialog(NEW_ROOM_DIALOG);

    });

    // controller.on('memberships.created', async(bot, message) => {
    //             console.log(message)
    //             console.log(controller.adapter._identity)
    //
    //
    //     if (controller.adapter._identity.id === message.data.personId) {
    //         let markDown = '**Available commands:**  \n';
    //
    //         controller.commandHelp.sort((a, b) => {
    //
    //             return ((a.command < b.command) ? -1 : ((a.command > b.command) ? 1 : 0));
    //         });
    //
    //         controller.commandHelp.forEach(element => {
    //
    //             markDown += `**${controller.checkAddMention(message.roomType, element.command)}**: ${element.text}  \n`
    //         });
    //
    //         await bot.reply(message, {markdown: markDown});
    //     }
    // });


}