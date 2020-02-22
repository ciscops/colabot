/**
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License.
 */
const {BotkitConversation} = require('botkit');
const request = require('request-promise');
virlServers = [];
virlServers = process.env.SERVER_LIST.split(',');
const VIRL_USERNAME = process.env.VIRL_USERNAME;
const VIRL_PASSWORD = process.env.VIRL_PASSWORD;

function VIRL_data(username_virl, password_virl, server_name) {
    this.username_virl = username_virl;
    this.password_virl = password_virl;
    this.server_name = server_name;
}

function VIRL_methods(obj) {
    this.get_token = async function () {
        let authenticate_options = {
            method: 'POST',
            uri: obj.server_name + '/api/v0/authenticate',
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json'
                },
            body: {username: obj.username_virl, password: obj.password_virl},
            json: true
        };
        let response = async () =>
            request(authenticate_options).then(function (resp) {
                return resp
            }).catch(function (err) {
                return ''
            });
        obj.bearer = await response();
    };
    this.randomPasswordGenerator = function () {
        let charList = "abcdefghijkmnpqrstuvwxyz0123456789ABCDEFGHJKLMNPQRSTUVWXYZ0123456789";
        let listLength = charList.length;
        let passwordString = '';
        let i;
        for (i = 0; i < 9; i++) {
            let x = Math.floor((Math.random() * listLength));
            passwordString += charList[x];
        }
        return passwordString
    };
    this.list_users = async () => {
        let list_users_options = {
            method: 'GET',
            uri: obj.server_name + '/api/v0/users',
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'cache-control': "no-cache",
                    "Authorization": "Bearer " + obj.bearer
                },
            json: true
        };
        let response = async () =>
            request(list_users_options).then(function (resp) {
                return resp
            }).catch(function (err) {
                return err
            });
        let results = await response();
        obj.users = [];
        for (let [key, value] of Object.entries(results)) {
            obj.users.push(results[key].username);
        }
        console.log(obj.users);
    };
    this.add_user = async (username_webex, user_email, new_password) => {
        let add_user_options = {
            method: 'POST',
            uri: obj.server_name + '/api/v0/users/' + username_webex,
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'cache-control': "no-cache",
                    "Authorization": "Bearer " + obj.bearer
                },
            body: {
                "password": new_password,
                "fullname": user_email,
                "description": "",
                "roles": [
                    "User"
                    // "admin"
                ],
                "context": {}
            },
            json: true
        };
        let response = async () =>
            request(add_user_options).then(function (resp) {
                return resp
            }).catch(function (err) {
                return err
            });
        obj.result = await response();
    };
    this.delete_user = async (username_webex) => {
        let delete_user_options = {
            method: 'DELETE',
            uri: obj.server_name + '/api/v0/users/' + username_webex,
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'cache-control': "no-cache",
                    "Authorization": "Bearer " + obj.bearer
                },
            json: true
        };
        let response = async () =>
            request(delete_user_options).then(function (resp) {
                return resp
            }).catch(function (err) {
                return err
            });
        obj.result = await response();
    };
    this.change_password = async (username_webex, new_password) => {
        let change_password_options = {
            method: 'PUT',
            uri: obj.server_name + '/api/v0/users/' + username_webex + '/change_password',
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'cache-control': "no-cache",
                    "Authorization": "Bearer " + obj.bearer
                },
            body: {
                "old_password": '',
                "new_password": new_password
            },
            json: true
        };
        let response = async () =>
            request(change_password_options).then(function (resp) {
                // A null response is a good response for this API call
                return resp
            }).catch(function (err) {
                return err
            });
        obj.result = await response();
    };
    this.list_labs = async (username_webex) => {
        let list_labs_options = {
            method: 'GET',
            uri: obj.server_name + '/api/v0/diagnostics',
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'cache-control': "no-cache",
                    "Authorization": "Bearer " + obj.bearer
                },
            json: true
        };
        let response = async () =>
            request(list_labs_options).then(function (resp) {
                return resp
            }).catch(function (err) {
                return err
            });
        let result = await response();

        let labs = result.user_roles.labs_by_user[username_webex];
        console.log(labs);
        if (labs) {
            let epoch_time_now = Math.floor(new Date().getTime() / 1000.0);
            let results_list = [];
            let x;
            let labs_str = '';
            for (x = 0; x < labs.length; x++) {
                let created_seconds = Math.floor(result.labs[labs[x]].created);
                let seconds = epoch_time_now - created_seconds;
                let days = Math.floor(seconds / (3600 * 24));
                seconds -= days * 3600 * 24;
                let hrs = Math.floor(seconds / 3600);
                seconds -= hrs * 3600;
                let mnts = Math.floor(seconds / 60);
                seconds -= mnts * 60;
                let uptime = days + " days, " + hrs + " Hrs, " + mnts + " Minutes, " + seconds + " Seconds";

                labs_str = '        **  Lab id: ' + labs[x] + '        Uptime: ' + uptime + '\n';
                results_list.push(labs_str);
            }
            obj.list_labs = results_list;
        } else {
            obj.list_labs = []
        }
    };
    this.list_labs_all = async () => {
        let list_labs_all_options = {
            method: 'GET',
            uri: obj.server_name + '/api/v0/diagnostics',
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'cache-control': "no-cache",
                    "Authorization": "Bearer " + obj.bearer
                },
            json: true
        };
        let response = async () =>
            request(list_labs_all_options).then(function (resp) {
                return resp
            }).catch(function (err) {
                return err
            });
        let result = await response();
        let epoch_time_now = Math.floor(new Date().getTime() / 1000.0);
        let results_list = [];
        let labs_str = '';
        let labs;
        for (let [key, value] of Object.entries(result.user_roles.labs_by_user)) {
            labs = result.user_roles.labs_by_user[key];
            if (labs.length > 0) {
                results_list.push('    ' + '* Labs for account: ' + key + '\n');
                let x;
                for (x = 0; x < labs.length; x++) {
                    let created_seconds = Math.floor(result.labs[labs[x]].created);
                    let seconds = epoch_time_now - created_seconds;
                    let days = Math.floor(seconds / (3600 * 24));
                    seconds -= days * 3600 * 24;
                    let hrs = Math.floor(seconds / 3600);
                    seconds -= hrs * 3600;
                    let mnts = Math.floor(seconds / 60);
                    seconds -= mnts * 60;
                    let uptime = days + " days, " + hrs + " Hrs, " + mnts + " Minutes, " + seconds + " Seconds";

                    labs_str = '            **  Lab id: ' + labs[x] + '        Uptime: ' + uptime + '\n';
                    results_list.push(labs_str);
                }
            }
        }
        obj.list_labs_all = results_list;
    };
    this.list_user_labs = async () => {
        let list_users_options = {
            method: 'GET',
            uri: obj.server_name + '/api/v0/labs',
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'cache-control': "no-cache",
                    "Authorization": "Bearer " + obj.bearer
                },
            json: true
        };
        let response = async () =>
            request(list_users_options).then(function (resp) {
                return resp
            }).catch(function (err) {
                return err
            });
        obj.labs = await response();
    };
    this.get_lab_details = async (lab_id) => {
        let get_lab_details_options = {
            method: 'GET',
            uri: obj.server_name + '/api/v0/labs/' + lab_id,
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'cache-control': "no-cache",
                    "Authorization": "Bearer " + obj.bearer
                },
            json: true
        };
        let response = async () =>
            request(get_lab_details_options).then(function (resp) {
                return resp
            }).catch(function (err) {
                return err
            });

        obj.lab_details.push(await response());
    };
    this.delete_lab = async function (lab_id) {
        let delete_lab_options = {
            method: 'DELETE',
            uri: obj.server_name + '/api/v0/labs/' + lab_id,
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'cache-control': "no-cache",
                    "Authorization": "Bearer " + obj.bearer
                },
            json: true
        };
        let response = async () =>
            request(delete_lab_options).then(function (resp) {
                return resp
            }).catch(function (err) {
                return err
            });
        obj.result = await response();
    };
    this.list_labs_ids = async (username_webex) => {
        let list_labs_ids_options = {
            method: 'GET',
            uri: obj.server_name + '/api/v0/diagnostics',
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'cache-control': "no-cache",
                    "Authorization": "Bearer " + obj.bearer
                },
            json: true
        };
        let response = async () =>
            request(list_labs_ids_options).then(function (resp) {
                return resp
            }).catch(function (err) {
                return err
            });
        let result = await response();
        labs = result.user_roles.labs_by_user[username_webex];
        if (labs) {
            obj.list_labs_ids = labs;
        } else {
            obj.list_labs_ids = []
        }
    };
    this.get_system_status = async () => {
        let get_system_status_options = {
            method: 'GET',
            uri: obj.server_name + '/api/v0/system_stats',
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'cache-control': "no-cache",
                    "Authorization": "Bearer " + obj.bearer
                },
            json: true
        };
        let response = async () =>
            request(get_system_status_options).then(function (resp) {
                return resp
            }).catch(function (err) {
                return err
            });
        obj.system_status = await response();
    };
}

function WEBEX_data() {
    this.webex_token = process.env.ACCESS_TOKEN
}

function WEBEX_methods(obj) {
    this.get_webex_email_and_username = async function () {
        let authenticate_options = {
            method: 'GET',
            uri: 'https://api.ciscospark.com/v1/people?id=' + obj.webex_user_id,
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json',
                    "Authorization": "Bearer " + obj.webex_token
                },
            json: true
        };
        let response = async () =>
            request(authenticate_options).then(function (resp) {
                return resp
            }).catch(function (err) {
                return err
            });
        let result = await response();
        obj.webex_user_email = result.items[0].emails[0];
        obj.webex_username = obj.webex_user_email.substring(0, obj.webex_user_email.lastIndexOf("@"));
        obj.display_name = result.items[0].displayName;
    };
    this.get_id_from_email = async function (email) {
        let web_email = email.replace(/@/, "%40");
        let get_id_from_email_options = {
            method: 'GET',
            uri: 'https://api.ciscospark.com/v1/people?email=' + web_email,
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json',
                    "Authorization": "Bearer " + obj.webex_token
                },
            json: true
        };
        let response = async () =>
            request(get_id_from_email_options).then(function (resp) {
                return resp
            }).catch(function (err) {
                return err
            });
        let result = await response();
        obj.webex_user_id = result.items[0].id;
    };
    this.send_message = async function (message) {
        let message_options = {
            method: 'POST',
            uri: 'https://api.ciscospark.com/v1/messages',
            rejectUnauthorized: false,
            headers:
                {
                    'Content-Type': 'application/json',
                    "Authorization": "Bearer " + obj.webex_token
                },
            body: {
                "toPersonId": obj.webex_user_id,
                "text": message,
            },
            json: true
        };
        let response = async () =>
            request(message_options).then(function (resp) {
                return resp
            }).catch(function (err) {
                return err
            });
        let result = await response();
    };
}

module.exports = function (controller) {
    /*
    VIRL Add Account Code
     */
    const ADD_USER_DIALOG = 'AddUser';
    const add_dialog = new BotkitConversation(ADD_USER_DIALOG, controller);
    add_dialog.say('I created this room so we could continue our create account conversation in private.');
    add_dialog.say('Please prepend "@my_bot_name" to replies');
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
                console.log(virl_data.result);

                if (virl_data.result === 'OK') {
                    console.log('Account Created: \n' + '    username: ' + webex_data.webex_username + '\n    password: ' + new_virl_pwd);
                    virl_result += '\n        ** Success: ' + virlServers[n]
                } else {
                    console.log('Error: ' + virl_data.result.error.code + ' - ' + virl_data.result.error.description);
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
        console.log('memberships created', message);
    });
    /*
    VIRL Delete Account Code
     */
    const DELETE_USER_DIALOG = 'DeleteUser';
    const delete_dialog = new BotkitConversation(DELETE_USER_DIALOG, controller);
    delete_dialog.say('I created this room so we could continue our delete account conversation in private.');
    delete_dialog.say('Please prepend "@my_bot_name" to replies');
    delete_dialog.ask("\nWould you like to delete your VIRL account? (yes|no)", async (response, convo, bot) => {
        if (convo.vars.response_delete === 'yes') {
            let webex_data = new WEBEX_data();
            webex_data.webex_user_id = convo.vars.user;
            let webex_methods = new WEBEX_methods(webex_data);
            await webex_methods.get_webex_email_and_username();
            let virl_result;
            virl_result = 'Account ' + webex_data.webex_username + ' successfully deleted from servers:'
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
                        await virl_methods.delete_lab(virl_data.list_labs_ids[g]);
                    }
                }
                await virl_methods.delete_user(webex_data.webex_username);
                console.log(virl_data.result);

                if (virl_data.result === 'OK') {
                    console.log('Account ' + webex_data.webex_username + ' successfully deleted');
                    virl_result += '\n        ** Success: ' + virlServers[n]
                } else {
                    console.log('Error: ' + virl_data.result.error.code + ' - ' + virl_data.result.error.description);
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
        console.log('memberships created', message);
    });
    /*
    VIRL Change Password Code
     */
    const CHANGE_PASSWORD_DIALOG = 'ChangePassword';
    const change_password_dialog = new BotkitConversation(CHANGE_PASSWORD_DIALOG, controller);
    change_password_dialog.say('I created this room so we could continue our reset password conversation in private.');
    change_password_dialog.say('Please prepend "@my_bot_name" to replies');
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
                    console.log('Password reset: \n' + '    username: ' + webex_data.webex_username + '\n    password: ' + new_virl_pwd);
                    virl_result += '\n        ** Success: ' + virlServers[n]
                } else {
                    console.log('Error: ' + virl_data.result.error.code + ' - ' + virl_data.result.error.description);
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
        console.log('memberships created', message);
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
    delete_lab_dialog.say('Please prepend "@my_bot_name" to replies');
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
                // convo.gotoThread('bad_password')
                lab_string += '\nLogin failed for: ' + virlServers[n]
            } else {
                virl_data.lab_details = [];
                await virl_methods.list_user_labs();
                let labs_details = [];
                let c;
                for (c = 0; c < virl_data.labs.length; c++) {
                    await virl_methods.get_lab_details(virl_data.labs[c]);
                }
                console.log(virl_data.lab_details);
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
    delete_lab_dialog.say('{{vars.labs}}');
    delete_lab_dialog.ask("\nPlease provide the fully qualified domain name of your VIRL server, e.g.'cpn-rtp-virl5.ciscops.net': ", async (response, convo, bot) => {
        let webex_data = new WEBEX_data();
        webex_data.webex_user_id = convo.vars.user;
        let webex_methods = new WEBEX_methods(webex_data);
        await webex_methods.get_webex_email_and_username();
        convo.setVar('virl_username', webex_data.webex_username);
        let virl_server = 'https://' + convo.vars.virl_server;
        let virl_data = new VIRL_data(webex_data.webex_username, convo.vars.virl_password, virl_server);
        let virl_methods = new VIRL_methods(virl_data);
        await virl_methods.get_token();

        if (virl_data.bearer === '') {
            convo.gotoThread('bad_password')
        } else {
            virl_data.lab_details = [];
            await virl_methods.list_user_labs();
            let labs_details = [];
            let c;
            for (c = 0; c < virl_data.labs.length; c++) {
                await virl_methods.get_lab_details(virl_data.labs[c]);
            }
            console.log(virl_data.lab_details);
            let lab_string = 'Current ' + virl_data.server_name.slice(8) + ' labs are: ';
            let i;
            for (i = 0; i < virl_data.lab_details.length; i++) {
                lab_string += '\n\n' + '        **  Lab ID: ' + virl_data.lab_details[i].id + '\n            * Title: ' + virl_data.lab_details[i].lab_title + '\n            * Created: ' + virl_data.lab_details[i].created + '\n            * Node count: ' + virl_data.lab_details[i].node_count + '\n            * State: ' + virl_data.lab_details[i].state
            }
            convo.setVar('labs', lab_string)
        }
    }, {key: 'virl_server'});

    // delete_lab_dialog.say('{{vars.labs}}');
    delete_lab_dialog.ask("Please enter the Lab ID of the lab you would like to delete or 'quit' to exit: ", async (response, convo, bot) => {
        if (convo.vars.lab_id === 'quit') {
            convo.gotoThread('goodbye')
        } else {
            let virl_server = 'https://' + convo.vars.virl_server;
            let virl_data = new VIRL_data(convo.vars.virl_username, convo.vars.virl_password, virl_server);
            let virl_methods = new VIRL_methods(virl_data);
            await virl_methods.get_token();
            await virl_methods.delete_lab(convo.vars.lab_id);
            let virl_result;
            if (virl_data.result === '') {
                console.log('Lab ID: ' + convo.vars.lab_id + ' successfully deleted');
                virl_result = 'Lab successfully deleted'
            } else {
                console.log('Error: ' + virl_data.result.error.code + ' - ' + virl_data.result.error.description);
                virl_result = 'Error: ' + virl_data.result.error.code + ' - ' + virl_data.result.error.description
            }
            convo.setVar('delete_result', virl_result);
        }
    }, {key: 'lab_id'});
    delete_lab_dialog.say('{{vars.delete_result}}');
    delete_lab_dialog.addMessage('Your password was not accepted by server {{vars.virl_server}}', 'bad_password');
    delete_lab_dialog.addMessage('Ok - Bye', 'goodbye');
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
        console.log('memberships created', message);
    });
    /*
    VIRL List your lab details Code
    */
    const LAB_DETAILS_DIALOG = 'LabDetails';
    const details_lab_dialog = new BotkitConversation(LAB_DETAILS_DIALOG, controller);
    details_lab_dialog.say('I created this room so we could continue our delete labs conversation in private.');
    details_lab_dialog.say('Please prepend "@my_bot_name" to replies');
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
                // convo.gotoThread('bad_password')
                lab_string += '\nLogin failed for: ' + virlServers[n]
            } else {
                virl_data.lab_details = [];
                await virl_methods.list_user_labs();
                let labs_details = [];
                let c;
                for (c = 0; c < virl_data.labs.length; c++) {
                    await virl_methods.get_lab_details(virl_data.labs[c]);
                }
                console.log(virl_data.lab_details);
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
    // details_lab_dialog.addMessage('Your password was not accepted by server {{vars.virl_server}}', 'bad_password');

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
        console.log('memberships created', message);
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
        command: 'VIRL show server utilization',
        text: 'Use to show current CPU and Memory usage'
    });
};
