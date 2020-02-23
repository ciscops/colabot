const request = require('request-promise');

function VIRL_methods_class(obj) {
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

module.exports = VIRL_methods_class;