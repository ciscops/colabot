from webex import WebExClient


async def catch_all(activity):
    if activity.get('text'):
        if activity.get('roomType') == 'group':
            message = dict(
                text='"' + activity.get(
                    'original_text') + '"   &#x1F914;  Please reply ' + "**@" +
                     activity['bot_name'] + " help** to see my available commands",
                roomId=activity['roomId'],
                attachments=[])
            webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
            await webex.post_message_to_webex(message)
            return
        else:
            message = dict(text='"' + activity.get(
                'original_text') + '"' + "   &#x1F914;  Please reply 'help' to see my available commands",
                           roomId=activity['roomId'],
                           attachments=[])
            webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
            await webex.post_message_to_webex(message)
            return
    else:
        if activity.get('roomType') == 'group':
            message = dict(
                text="   &#x1F914;  Please reply " + "**@" +
                     activity['bot_name'] + " help** to see my available commands",
                roomId=activity['roomId'],
                attachments=[])
            webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
            await webex.post_message_to_webex(message)
            return
        else:
            message = dict(text="   &#x1F914;  Please reply 'help' to see my available commands",
                           roomId=activity['roomId'],
                           attachments=[])
            webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
            await webex.post_message_to_webex(message)
            return
