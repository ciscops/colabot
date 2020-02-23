const request = require('request-promise');

function WEBEX_methods_class(obj) {
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

module.exports = WEBEX_methods_class;
