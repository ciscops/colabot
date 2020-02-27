/**
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License.
 */
const {BotkitConversation} = require('botkit');
const WEBEX_methods = require('./WEBEX_methods_class.js');
const WEBEX_data = require('./WEBEX_data_class.js');
const VIRL_methods = require('./VIRL_methods_class.js');
const VIRL_data = require('./VIRL_data_class.js');
const MongoClient = require('mongodb').MongoClient;
const assert = require('assert');
virlServers = [];
virlServers = process.env.SERVER_LIST.split(',');
const VIRL_USERNAME = process.env.VIRL_USERNAME;
const VIRL_PASSWORD = process.env.VIRL_PASSWORD;
const MONGO_INITDB_ROOT_USERNAME = process.env.MONGO_INITDB_ROOT_USERNAME;
const MONGO_INITDB_ROOT_PASSWORD = process.env.MONGO_INITDB_ROOT_PASSWORD;
const MONGO_SERVER = process.env.MONGO_SERVER;
const MONGO_PORT = process.env.MONGO_PORT;
const MONGO_DB = process.env.MONGO_DB;
const MONGO_COLLECTIONS = process.env.MONGO_COLLECTIONS;


module.exports = function (controller) {
    /*
    VIRL Add Account Code
     */
    const ADD_USER_DIALOG = 'AddUser';
    const add_dialog = new BotkitConversation(ADD_USER_DIALOG, controller);
    add_dialog.say('I created this room so we could continue our create account conversation in private.');
    add_dialog.say('Please prepend "@COLABot" to replies');
    add_dialog.ask("\nWould you like to create a VIRL account? (yes|no)", async (response, convo, bot) => {

        if (convo.vars.response_add === 'yes') {
            let webex_data = new WEBEX_data();
            webex_data.webex_user_id = convo.vars.user;
            let webex_methods = new WEBEX_methods(webex_data);
            await webex_methods.get_webex_email_and_username();

            let new_virl_pwd = await new VIRL_methods().randomPasswordGenerator();
            let virl_result;
            virl_result = 'Account Created: \n' + '    username: ' + webex_data.webex_username + '\n    password: ' + new_virl_pwd;

            let n;
            for (n = 0; n < virlServers.length; n++) {
                let virl_server_url = 'https://' + virlServers[n];
                let virl_data = new VIRL_data(VIRL_USERNAME, VIRL_PASSWORD, virl_server_url);
                let virl_methods = new VIRL_methods(virl_data);
                await virl_methods.get_token();
                await virl_methods.add_user(webex_data.webex_username, webex_data.webex_user_email, new_virl_pwd);

                if (virl_data.result === 'OK') {
                    console.log('Success - created account: \n' + '    username: ' + webex_data.webex_username);
                    virl_result += '\n        ** Success: ' + virlServers[n]
                } else {
                    console.log('Fail - error creating account username : ' + webex_data.webex_username + ' ' + virl_data.result.error.code + ' - ' + virl_data.result.error.description);
                    virl_result += '\n        ** Failure: ' + virlServers[n] + ' ' + virl_data.result.error.code + ' - ' + virl_data.result.error.description
                }
                convo.vars.response_add = virl_result;
            }
        } else {
            convo.vars.response_add = 'You chose not to create an account'
        }
    }, {key: 'response_add'});
    add_dialog.say('{{vars.response_add}}');
    controller.addDialog(add_dialog);
    controller.hears('VIRL create account', 'message,direct_message', async (bot, message) => {
        let webex_data = new WEBEX_data();
        webex_data.webex_user_id = message.user;
        let webex_methods = new WEBEX_methods(webex_data);
        await webex_methods.get_webex_email_and_username();
        await bot.reply(message, webex_data.display_name + ' - Please join me in room "VIRL Create User"');
        let room = await bot.api.rooms.create({title: 'VIRL Create User'});
        let membership2 = await bot.api.memberships.create({
            roomId: room.id,
            personId: message.user,
        });
        await bot.startConversationInRoom(room.id, message.user);
        await bot.beginDialog(ADD_USER_DIALOG);
    });
    controller.on('memberships.created', async (bot, message) => {
    });
    /*
    VIRL Delete Account Code
     */
    const DELETE_USER_DIALOG = 'DeleteUser';
    const delete_dialog = new BotkitConversation(DELETE_USER_DIALOG, controller);
    delete_dialog.say('I created this room so we could continue our delete account conversation in private.');
    delete_dialog.say('Please prepend "@COLABot" to replies');
    delete_dialog.ask("\nWould you like to delete your VIRL account? (yes|no)", async (response, convo, bot) => {
        if (convo.vars.response_delete === 'yes') {
            let webex_data = new WEBEX_data();
            webex_data.webex_user_id = convo.vars.user;
            let webex_methods = new WEBEX_methods(webex_data);
            await webex_methods.get_webex_email_and_username();
            let virl_result;
            virl_result = 'Account ' + webex_data.webex_username + ' deleted from servers:';
            let n;
            for (n = 0; n < virlServers.length; n++) {
                let virl_server_url = 'https://' + virlServers[n];
                let virl_data = new VIRL_data(VIRL_USERNAME, VIRL_PASSWORD, virl_server_url);
                let virl_methods = new VIRL_methods(virl_data);
                await virl_methods.get_token();

                await virl_methods.list_labs_ids(webex_data.webex_username);
                if (virl_data.list_labs_ids.length > 0) {
                    let g;
                    for (g = 0; g < virl_data.list_labs_ids.length; g++) {
                        await virl_methods.stop_lab(virl_data.list_labs_ids[g]);
                        await virl_methods.wipe_lab(virl_data.list_labs_ids[g]);
                        await virl_methods.delete_lab(virl_data.list_labs_ids[g]);
                    }
                }
                await virl_methods.delete_user(webex_data.webex_username);

                if (virl_data.result === 'OK') {
                    console.log('Success - Account deleted: ' + webex_data.webex_username);
                    virl_result += '\n        ** Success: ' + virlServers[n]
                } else {
                    console.log('Fail - Error deleting account: ' + webex_data.webex_username + ' ' + virl_data.result.error.code + ' - ' + virl_data.result.error.description);
                    virl_result += '\n        ** Failure: ' + virlServers[n] + ' ' + virl_data.result.error.code + ' - ' + virl_data.result.error.description
                }
                convo.vars.response_delete = virl_result;
            }
        } else {
            convo.vars.response_delete = 'You chose not to remove your account'
        }
    }, {key: 'response_delete'});
    delete_dialog.say('{{vars.response_delete}}');
    controller.addDialog(delete_dialog);
    controller.hears('VIRL delete account', 'message,direct_message', async (bot, message) => {
        let webex_data = new WEBEX_data();
        webex_data.webex_user_id = message.user;
        let webex_methods = new WEBEX_methods(webex_data);
        await webex_methods.get_webex_email_and_username();
        await bot.reply(message, webex_data.display_name + ' - Please join me in room "VIRL Delete User"');
        let room = await bot.api.rooms.create({title: 'VIRL Delete User'});
        let membership2 = await bot.api.memberships.create({
            roomId: room.id,
            personId: message.user,
        });
        await bot.startConversationInRoom(room.id, message.user);
        await bot.beginDialog(DELETE_USER_DIALOG);
    });
    controller.on('memberships.created', async (bot, message) => {
    });
    /*
    VIRL Change Password Code
     */
    const CHANGE_PASSWORD_DIALOG = 'ChangePassword';
    const change_password_dialog = new BotkitConversation(CHANGE_PASSWORD_DIALOG, controller);
    change_password_dialog.say('I created this room so we could continue our reset password conversation in private.');
    change_password_dialog.say('Please prepend "@COLABot" to replies');
    change_password_dialog.ask("\nWould you like to reset your VIRL account password? (yes|no)", async (response, convo, bot) => {


        if (convo.vars.response_change_password === 'yes') {
            let webex_data = new WEBEX_data();
            webex_data.webex_user_id = convo.vars.user;
            let webex_methods = new WEBEX_methods(webex_data);
            await webex_methods.get_webex_email_and_username();

            let new_virl_pwd = await new VIRL_methods().randomPasswordGenerator();
            let virl_result;
            virl_result = 'Password reset: \n' + '    username: ' + webex_data.webex_username + '\n    new password: ' + new_virl_pwd;

            let n;
            for (n = 0; n < virlServers.length; n++) {
                let virl_server_url = 'https://' + virlServers[n];

                let virl_data = new VIRL_data(VIRL_USERNAME, VIRL_PASSWORD, virl_server_url);
                let virl_methods = new VIRL_methods(virl_data);
                await virl_methods.get_token();
                await virl_methods.change_password(webex_data.webex_username, new_virl_pwd);

                if (virl_data.result === null) {
                    console.log('Success -  Password reset: \n' + '    username: ' + webex_data.webex_username + '\n    password: ' + new_virl_pwd);
                    virl_result += '\n        ** Success: ' + virlServers[n]
                } else {
                    console.log('Fail - Error resetting password username: ' + webex_data.webex_username + ' ' +virl_data.result.error.code + ' - ' + virl_data.result.error.description);
                    virl_result += '\n        ** Failure: ' + virlServers[n] + ' ' + virl_data.result.error.code + ' - ' + virl_data.result.error.description
                }
                convo.vars.response_change_password = virl_result;
            }
        } else {
            convo.vars.response_change_password = 'You chose not to reset your VIRL password'
        }
    }, {key: 'response_change_password'});
    change_password_dialog.say('{{vars.response_change_password}}');
    controller.addDialog(change_password_dialog);
    controller.hears('VIRL reset password', 'message,direct_message', async (bot, message) => {
        let webex_data = new WEBEX_data();
        webex_data.webex_user_id = message.user;
        let webex_methods = new WEBEX_methods(webex_data);
        await webex_methods.get_webex_email_and_username();
        await bot.reply(message, webex_data.display_name + ' - Please join me in room "VIRL Reset Password"');
        let room = await bot.api.rooms.create({title: 'VIRL Reset Password'});
        let membership2 = await bot.api.memberships.create({
            roomId: room.id,
            personId: message.user,
        });
        await bot.startConversationInRoom(room.id, message.user);
        await bot.beginDialog(CHANGE_PASSWORD_DIALOG);
    });
    controller.on('memberships.created', async (bot, message) => {
    });
    /*
    VIRL Display Users Code
     */
    controller.hears('VIRL list users', 'message,direct_message', async (bot, message) => {
        let user_string = '';
        let n;
        for (n = 0; n < virlServers.length; n++) {
            let virl_server_url = 'https://' + virlServers[n];
            let virl_data = new VIRL_data(VIRL_USERNAME, VIRL_PASSWORD, virl_server_url);
            let virl_methods = new VIRL_methods(virl_data);
            await virl_methods.get_token();
            await virl_methods.list_users();
            user_string += '\n' + virlServers[n] + ' users are: ';
            let i;
            for (i = 0; i < virl_data.users.length; i++) {
                user_string += '\n' + '        **  ' + virl_data.users[i]
            }
        }
        await bot.reply(message, user_string)
    });
    /*
    VIRL List Labs for single user Code
     */
    controller.hears('VIRL list my labs', 'message,direct_message', async (bot, message) => {
        let webex_data = new WEBEX_data();
        webex_data.webex_user_id = message.personId;
        let webex_methods = new WEBEX_methods(webex_data);
        await webex_methods.get_webex_email_and_username();

        let labs_string = 'Labs for ' + webex_data.webex_username + ':';

        let n;
        for (n = 0; n < virlServers.length; n++) {
            let virl_server_url = 'https://' + virlServers[n];
            let virl_data = new VIRL_data(VIRL_USERNAME, VIRL_PASSWORD, virl_server_url);
            let virl_methods = new VIRL_methods(virl_data);
            await virl_methods.get_token();

            await virl_methods.list_labs(webex_data.webex_username);
            if (virl_data.list_labs.length > 0) {
                labs_string += '\n' + virlServers[n] + ':\n';
                let i;
                for (i = 0; i < virl_data.list_labs.length; i++) {
                    labs_string += virl_data.list_labs[i]
                }
            }
        }
        await bot.reply(message, labs_string)
    });
    /*
    VIRL List Labs for all users Code
     */
    controller.hears('VIRL list all labs', 'message,direct_message', async (bot, message) => {
        let labs_string = '';
        let n;
        for (n = 0; n < virlServers.length; n++) {
            let virl_server_url = 'https://' + virlServers[n];
            let virl_data = new VIRL_data(VIRL_USERNAME, VIRL_PASSWORD, virl_server_url);
            let virl_methods = new VIRL_methods(virl_data);
            await virl_methods.get_token();
            await virl_methods.list_labs_all();
            labs_string += virlServers[n] + ' labs: ' + '\n';
            let i;
            for (i = 0; i < virl_data.list_labs_all.length; i++) {
                labs_string += virl_data.list_labs_all[i]
            }
        }
        await bot.reply(message, labs_string)
    });
    /*
    VIRL Delete Lab Code
    */
    const DELETE_LAB_DIALOG = 'DeleteLab';
    const delete_lab_dialog = new BotkitConversation(DELETE_LAB_DIALOG, controller);
    delete_lab_dialog.say('I created this room so we could continue our delete labs conversation in private.');
    delete_lab_dialog.say('Please prepend "@COLABot" to replies');
    delete_lab_dialog.ask("What is your VIRL password?", async (response, convo, bot) => {
        let webex_data = new WEBEX_data();
        webex_data.webex_user_id = convo.vars.user;
        let webex_methods = new WEBEX_methods(webex_data);
        await webex_methods.get_webex_email_and_username();
        convo.setVar('virl_username', webex_data.webex_username);
        let lab_string = '';

        let n;
        for (n = 0; n < virlServers.length; n++) {
            let virl_server_url = 'https://' + virlServers[n];

            let virl_data = new VIRL_data(webex_data.webex_username, convo.vars.virl_password, virl_server_url);
            let virl_methods = new VIRL_methods(virl_data);
            await virl_methods.get_token();

            if (virl_data.bearer === '') {
                lab_string += '\nLogin failed for: ' + virlServers[n]
            } else {
                virl_data.lab_details = [];
                await virl_methods.list_user_labs();
                let c;
                for (c = 0; c < virl_data.labs.length; c++) {
                    await virl_methods.get_lab_details(virl_data.labs[c]);
                }
                if (virl_data.lab_details.length > 0) {
                    lab_string += '\n' + virlServers[n] + ' labs are: ';
                    let i;
                    for (i = 0; i < virl_data.lab_details.length; i++) {
                        lab_string += '\n' + '        **  Lab ID: ' + virl_data.lab_details[i].id + '\n            * Title: ' + virl_data.lab_details[i].lab_title + '\n            * Created: ' + virl_data.lab_details[i].created + '\n            * Node count: ' + virl_data.lab_details[i].node_count + '\n            * State: ' + virl_data.lab_details[i].state
                    }
                }
                if (lab_string.length > 0) {
                    convo.setVar('labs', lab_string)
                } else {
                    convo.gotoThread('no_labs')
                }

            }
        }
    }, {key: 'virl_password'});
    delete_lab_dialog.say('{{vars.labs}}');
    delete_lab_dialog.ask("\nPlease provide the fully qualified domain name of your VIRL server, e.g.'cpn-rtp-virl5.ciscops.net': ", async (response, convo, bot) => {
    }, {key: 'virl_server'});

    delete_lab_dialog.ask("Please enter the Lab ID of the lab you would like to delete or 'quit' to exit: ", async (response, convo, bot) => {
        if (convo.vars.lab_id === 'quit') {
            convo.gotoThread('goodbye')
        } else {
            let virl_server = 'https://' + convo.vars.virl_server;
            let virl_data = new VIRL_data(convo.vars.virl_username, convo.vars.virl_password, virl_server);
            let virl_methods = new VIRL_methods(virl_data);
            await virl_methods.get_token();
            await virl_methods.stop_lab(convo.vars.lab_id);
            await virl_methods.wipe_lab(convo.vars.lab_id);
            await virl_methods.delete_lab(convo.vars.lab_id);
            let virl_result;
            if (virl_data.result === '') {
                console.log('Success - Deleted Lab ID: ' + convo.vars.lab_id);
                virl_result = 'Lab successfully deleted'
            } else {
                console.log('Fail - Error deleting lab: ' + convo.vars.lab_id + ' ' + virl_data.result.error.code + ' - ' + virl_data.result.error.description);
                virl_result = 'Error: ' + virl_data.result.error.code + ' - ' + virl_data.result.error.description
            }
            convo.setVar('delete_result', virl_result);
        }
    }, {key: 'lab_id'});
    delete_lab_dialog.say('{{vars.delete_result}}');
    delete_lab_dialog.addMessage('Your password was not accepted by server {{vars.virl_server}}', 'bad_password');
    delete_lab_dialog.addMessage('Ok - Bye', 'goodbye');
    delete_lab_dialog.addMessage('You have no labs. Good Bye', 'no_labs');
    controller.addDialog(delete_lab_dialog);
    controller.hears('VIRL delete lab', 'message,direct_message', async (bot, message) => {
        let webex_data = new WEBEX_data();
        webex_data.webex_user_id = message.user;
        let webex_methods = new WEBEX_methods(webex_data);
        await webex_methods.get_webex_email_and_username();
        await bot.reply(message, webex_data.display_name + ' - Please join me in room "VIRL Delete Lab"');
        let room = await bot.api.rooms.create({title: 'VIRL Delete Lab'});
        let membership2 = await bot.api.memberships.create({
            roomId: room.id,
            personId: message.user,
        });
        await bot.startConversationInRoom(room.id, message.user);
        await bot.beginDialog(DELETE_LAB_DIALOG);
    });
    controller.on('memberships.created', async (bot, message) => {
    });
    /*
    VIRL List your lab details Code
    */
    const LAB_DETAILS_DIALOG = 'LabDetails';
    const details_lab_dialog = new BotkitConversation(LAB_DETAILS_DIALOG, controller);
    details_lab_dialog.say('I created this room so we could continue our delete labs conversation in private.');
    details_lab_dialog.say('Please prepend "@COLABot" to replies');
    details_lab_dialog.ask("What is your VIRL password?", async (response, convo, bot) => {
        let webex_data = new WEBEX_data();
        webex_data.webex_user_id = convo.vars.user;
        let webex_methods = new WEBEX_methods(webex_data);
        await webex_methods.get_webex_email_and_username();
        convo.setVar('virl_username', webex_data.webex_username);
        let lab_string = '';

        let n;
        for (n = 0; n < virlServers.length; n++) {
            let virl_server_url = 'https://' + virlServers[n];

            let virl_data = new VIRL_data(webex_data.webex_username, convo.vars.virl_password, virl_server_url);
            let virl_methods = new VIRL_methods(virl_data);
            await virl_methods.get_token();

            if (virl_data.bearer === '') {
                lab_string += '\nLogin failed for: ' + virlServers[n]
            } else {
                virl_data.lab_details = [];
                await virl_methods.list_user_labs();
                let labs_details = [];
                let c;
                for (c = 0; c < virl_data.labs.length; c++) {
                    await virl_methods.get_lab_details(virl_data.labs[c]);
                }
                if (virl_data.lab_details.length > 0) {
                    lab_string += '\n' + virlServers[n] + ' labs are: ';
                    let i;
                    for (i = 0; i < virl_data.lab_details.length; i++) {
                        lab_string += '\n' + '        **  Lab ID: ' + virl_data.lab_details[i].id + '\n            * Title: ' + virl_data.lab_details[i].lab_title + '\n            * Created: ' + virl_data.lab_details[i].created + '\n            * Node count: ' + virl_data.lab_details[i].node_count + '\n            * State: ' + virl_data.lab_details[i].state
                    }
                }
                if (lab_string.length > 0) {
                    convo.setVar('labs', lab_string)
                } else {
                    convo.setVar('labs', '** You have no labs')
                }

            }
        }
    }, {key: 'virl_password'});

    details_lab_dialog.say('{{vars.labs}}');

    controller.addDialog(details_lab_dialog);
    controller.hears('VIRL list my lab details', 'message,direct_message', async (bot, message) => {
        let webex_data = new WEBEX_data();
        webex_data.webex_user_id = message.user;
        let webex_methods = new WEBEX_methods(webex_data);
        await webex_methods.get_webex_email_and_username();
        await bot.reply(message, webex_data.display_name + ' - Please join me in room "VIRL my lab details"');
        let room = await bot.api.rooms.create({title: 'VIRL my lab details'});
        let membership2 = await bot.api.memberships.create({
            roomId: room.id,
            personId: message.user,
        });
        await bot.startConversationInRoom(room.id, message.user);
        await bot.beginDialog(LAB_DETAILS_DIALOG);
    });
    controller.on('memberships.created', async (bot, message) => {
    });
    /*
    VIRL Test Password Generation Function Code
     */
    controller.hears('VIRL new password', 'message,direct_message', async (bot, message) => {
        let virl_data = new VIRL_data(VIRL_USERNAME, VIRL_PASSWORD, virl_server_url);
        let virl_methods = new VIRL_methods(virl_data);
        await virl_methods.get_token();
        let pwd = await virl_methods.randomPasswordGenerator();
        await bot.reply(message, pwd)
    });
    /*
    VIRL Show Server Utilization Code
     */
    controller.hears('VIRL show server utilization', 'message,direct_message', async (bot, message) => {
        let utilization_string = '';
        let n;
        for (n = 0; n < virlServers.length; n++) {
            let virl_server_url = 'https://' + virlServers[n];
            let virl_data = new VIRL_data(VIRL_USERNAME, VIRL_PASSWORD, virl_server_url);
            let virl_methods = new VIRL_methods(virl_data);
            await virl_methods.get_token();
            await virl_methods.get_system_status();
            let cpu = Math.round(virl_data.system_status.clusters.cluster_1.high_level_drivers.compute_1.cpu.percent);
            let memory_ratio = Math.round(virl_data.system_status.clusters.cluster_1.high_level_drivers.compute_1.memory.used / virl_data.system_status.clusters.cluster_1.high_level_drivers.compute_1.memory.total * 100);
            utilization_string += '** ' + virlServers[n] + ':' + '\n            CPU: ' + cpu + '%' + '        Memory: ' + memory_ratio + '%\n'
        }
        await bot.reply(message, utilization_string)
    });
    /*
    VIRL Stop Lab Code
    */
    const STOP_LAB_DIALOG = 'StopLab';
    const stop_lab_dialog = new BotkitConversation(STOP_LAB_DIALOG, controller);
    stop_lab_dialog.say('I created this room so we could continue our stop lab conversation in private.');
    stop_lab_dialog.say('Please prepend "@COLABot" to replies');
    stop_lab_dialog.ask("What is your VIRL password?", async (response, convo, bot) => {
        let webex_data = new WEBEX_data();
        webex_data.webex_user_id = convo.vars.user;
        let webex_methods = new WEBEX_methods(webex_data);
        await webex_methods.get_webex_email_and_username();
        convo.setVar('virl_username', webex_data.webex_username);
        let lab_string = '';

        let n;
        for (n = 0; n < virlServers.length; n++) {
            let running_labs_flag = false;
            let virl_server_url = 'https://' + virlServers[n];

            let virl_data = new VIRL_data(webex_data.webex_username, convo.vars.virl_password, virl_server_url);
            let virl_methods = new VIRL_methods(virl_data);
            await virl_methods.get_token();

            if (virl_data.bearer === '') {
                lab_string += '\nLogin failed for: ' + virlServers[n]
            } else {
                virl_data.lab_details = [];
                await virl_methods.list_user_labs();
                let c;
                for (c = 0; c < virl_data.labs.length; c++) {
                    await virl_methods.get_lab_details(virl_data.labs[c]);
                }
                if (virl_data.lab_details.length > 0) {
                    let temp_lab_string = '\n' + virlServers[n] + ' labs are: ';
                    let i;
                    for (i = 0; i < virl_data.lab_details.length; i++) {
                        if (virl_data.lab_details[i].state === 'STARTED') {
                            running_labs_flag = true;
                            temp_lab_string += '\n' + '        **  Lab ID: ' + virl_data.lab_details[i].id + '\n            * Title: ' + virl_data.lab_details[i].lab_title + '\n            * Created: ' + virl_data.lab_details[i].created + '\n            * Node count: ' + virl_data.lab_details[i].node_count + '\n            * State: ' + virl_data.lab_details[i].state
                        }
                        if (running_labs_flag === true) {
                            lab_string += temp_lab_string
                        }
                    }
                }
                if (lab_string.length > 0) {
                    convo.setVar('labs', lab_string)
                } else {
                    // convo.setVar('labs', '** You have no running labs')
                    convo.gotoThread('no_running_labs')
                }

            }
        }
    }, {key: 'virl_password'});
    stop_lab_dialog.say('{{vars.labs}}');
    stop_lab_dialog.ask("\nPlease provide the fully qualified domain name of your VIRL server, e.g.'cpn-rtp-virl5.ciscops.net': ", async (response, convo, bot) => {
    }, {key: 'virl_server'});

    stop_lab_dialog.ask("Please enter the Lab ID of the lab you would like to stop or 'quit' to exit: ", async (response, convo, bot) => {
        if (convo.vars.lab_id === 'quit') {
            convo.gotoThread('goodbye')
        } else {
            let virl_server = 'https://' + convo.vars.virl_server;
            let virl_data = new VIRL_data(convo.vars.virl_username, convo.vars.virl_password, virl_server);
            let virl_methods = new VIRL_methods(virl_data);
            await virl_methods.get_token();
            await virl_methods.stop_lab(convo.vars.lab_id);
            let virl_result;
            if (virl_data.result === 'Success') {
                console.log('Success - Stopped Lab ID: ' + convo.vars.lab_id);
                virl_result = 'Lab successfully stopped'
            } else {
                console.log('Fail - Error stopping Lab Id: ' + convo.vars.lab_id + ' ' + virl_data.result.error.code + ' - ' + virl_data.result.error.description);
                virl_result = 'Error: ' + virl_data.result.error.code + ' - ' + virl_data.result.error.description
            }
            convo.setVar('stop_result', virl_result);
        }
    }, {key: 'lab_id'});
    stop_lab_dialog.say('{{vars.stop_result}}');
    stop_lab_dialog.addMessage('Your password was not accepted by server {{vars.virl_server}}', 'bad_password');
    stop_lab_dialog.addMessage('Ok - Bye', 'goodbye');
    stop_lab_dialog.addMessage('You have no running labs. Good Bye', 'no_running_labs');
    controller.addDialog(stop_lab_dialog);
    controller.hears('VIRL stop lab', 'message,direct_message', async (bot, message) => {
        let webex_data = new WEBEX_data();
        webex_data.webex_user_id = message.user;
        let webex_methods = new WEBEX_methods(webex_data);
        await webex_methods.get_webex_email_and_username();
        await bot.reply(message, webex_data.display_name + ' - Please join me in room "VIRL Stop Lab"');
        let room = await bot.api.rooms.create({title: 'VIRL Stop Lab'});
        let membership2 = await bot.api.memberships.create({
            roomId: room.id,
            personId: message.user,
        });
        await bot.startConversationInRoom(room.id, message.user);
        await bot.beginDialog(STOP_LAB_DIALOG);
    });
    controller.on('memberships.created', async (bot, message) => {
    });
    /*
    VIRL Extend Lab Code
     */
    let extend_cmd_regex = '^VIRL extend lab (.*)$';
    controller.hears(extend_cmd_regex, 'message,direct_message', async (bot, message) => {
        if (MONGO_SERVER != 'mongodb.example.com') {
            const url = 'mongodb://' + MONGO_INITDB_ROOT_USERNAME + ':' + MONGO_INITDB_ROOT_PASSWORD + '@' + MONGO_SERVER + ':' + MONGO_PORT;
            const client = new MongoClient(url, {useNewUrlParser: true});
            let regex1 = new RegExp(extend_cmd_regex);
            let lab_and_server_string = regex1.exec(message.text);
            let lab_and_server_list = lab_and_server_string[1].split(' on ');
            if (!Array.isArray(lab_and_server_list) || lab_and_server_list.length != 2) {
                await bot.reply(message, 'Error parsing message. Example "@COLABot VIRL extend lab a1234z on cpn-rtp-virl5.ciscops.net"');
            } else {
                let query_filter = {
                    'server': lab_and_server_list[1],
                    'user_id': message.personId,
                    'lab_id': lab_and_server_list[0]
                };
                let result = await client.connect();
                if (result.s.url === undefined) {
                    await bot.reply(message, 'Error connecting to database')
                } else {
                    const db = await client.db(MONGO_DB);
                    const collection = await db.collection(MONGO_COLLECTIONS);
                    const record = await collection.findOne(query_filter);
                    if (record == null) {
                        await bot.reply(message, 'Could not find record for lab ' + lab_and_server_list[0] + ' on server ' + lab_and_server_list[1])
                    } else {
                        let epoch_time_now = Math.floor(new Date().getTime() / 1000.0);
                        result = await collection.updateOne(query_filter, {
                            $set: {
                                'renewal_flag': true,
                                'warning_date': epoch_time_now
                            }
                        });
                        if (result.modifiedCount === 1) {
                            console.log('Success - Extended Lab ID: ' + lab_and_server_list[0] + ' on server ' + lab_and_server_list[1]);
                            await bot.reply(message, 'Record for lab ' + lab_and_server_list[0] + ' on server ' + lab_and_server_list[1] + 'extended')
                        } else {
                            console.log('Fail - Extending Lab ID: ' + lab_and_server_list[0] + ' on server ' + lab_and_server_list[1]);
                            await bot.reply(message, 'Error extending lab')
                        }
                    }
                }
            }
        } else {
            await bot.reply(message, '@COLABot is not configured for lab extension.')
        }
    });
    /*
    Below commandHelp statements are read by the Help function
     */
    controller.commandHelp.push({
        command: 'VIRL create account',
        text: 'Use to create your VIRL account(creates private room)'
    });
    controller.commandHelp.push({
        command: 'VIRL delete account',
        text: 'Use to delete your VIRL account(creates private room)'
    });
    controller.commandHelp.push({
        command: 'VIRL reset password',
        text: 'Use to reset your VIRL account password(creates private room)'
    });
    controller.commandHelp.push({command: 'VIRL list users', text: 'Use to list user accounts'});
    controller.commandHelp.push({command: 'VIRL list my labs', text: 'Use to list your labs'});
    controller.commandHelp.push({
        command: 'VIRL list my lab details',
        text: 'Use to list your lab with details(creates private room)'
    });
    controller.commandHelp.push({command: 'VIRL list all labs', text: 'Use to list all labs running'});
    controller.commandHelp.push({
        command: 'VIRL delete lab',
        text: 'Choose a lab to delete from a list of your labs(creates private room)'
    });
    controller.commandHelp.push({
        command: 'VIRL stop lab',
        text: 'Choose a lab to stop from a list of your labs(creates private room)'
    });
    controller.commandHelp.push({
        command: 'VIRL show server utilization',
        text: 'Use to show current CPU and Memory usage'
    });
};
