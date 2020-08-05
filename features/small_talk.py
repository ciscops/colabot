from webex import WebExClient
import random


async def small_talk(activity):
    if activity.get('text') == 'bye':
        responses = ['Bye &#x1F60A;', 'Good bye &#x1F60A;', 'Make it a great day! &#x1F603;']
        reply = responses[random.randint(0, (len(responses) - 1))]
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        message = dict(text=reply,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        return {'status_code': 200}

    if activity.get('text') == 'thanks':
        responses = ["You're welcome! &#x1F60A;", 'Anytime &#x1F603;', 'No problem &#x1F603;', '$#x1F970;']
        reply = responses[random.randint(0, (len(responses) - 1))]
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        message = dict(text=reply,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        return {'status_code': 200}

    if activity.get('text') == 'troubleshoot':
        excuses = ['clock speed',
                   'solar flares',
                   'electromagnetic radiation from satellite debris',
                   'poor power conditioning',
                   'static buildup',
                   'doppler effect',
                   'hardware stress fractures',
                   'temporary routing anomaly',
                   'fat electrons in the lines',
                   'excess surge protection',
                   'floating point processor overflow',
                   'network packets travelling uphill',
                   'radiosity depletion',
                   'CPU radiator broken',
                   'positron router malfunction',
                   'cellular telephone interference',
                   'techtonic stress',
                   'spaghetti cable caused packet failure',
                   'bad ether in the cables',
                   'Bogon emissions',
                   'high pressure system failure',
                   'CPU needs recalibration',
                   'bit bucket overflow',
                   'runt packets',
                   'electromagnetic energy loss',
                   'Internet outage',
                   'IRQ dropout',
                   'root nameservers are out of sync',
                   'sticky bits on disk',
                   "unplugged"
                   'daemons loose in system',
                   'party-bug in the Aloha protocol.',
                   'big to little endian conversion error',
                   'zombie processes haunting the computer',
                   'broadcast packets on wrong frequency',
                   'multicasts on broken packets',
                   'ether leak',
                   'bit rot',
                   'electrons on a bender',
                   'token fell out of the ring',
                   'routing problems on the neural net',
                   'firewall needs cooling',
                   'POP server is out of Coke',
                   'fiber optics caused gas main leak',
                   'network failure -  call NBC',
                   "parity check is overdrawn and you're out of cache",
                   'parallel processors running perpendicular today',
                   'incorrectly configured static routes on the core routers',
                   'increased sunspot activity',
                   'SYN flooding has your computer underwater',
                   'maintenance window broken',
                   'stop bit received',
                   'sticky bit has come loose',
                   'overflow error in /dev/null',
                   "greenpeace freed the mallocs"]
        reply_index = random.randint(0, (len(excuses) - 1))
        reply = 'Could be ' + excuses[reply_index]
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        message = dict(text=reply,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        return {'status_code': 200}

    if activity.get('text') == 'upset':
        emojis = ['&#x1F308;', '&#x1F92A;', '&#x1F921;', '&#x1F63D;', '&#x1F48B;', '&#x2764;', '&#x1F486;', '&#x1F483;',
                  '&#x1F57A;', '&#x1F46F;', '&#x1F938;', '&#x1F6C0;', '&#x1F6CC;', '&#x1F429;', '&#x1F408;',
                  '&#x1F984;', '&#x1F43F;', '&#x1F423;', '&#x1F99C;', '&#x1F41A;', '&#x1F490;', '&#x1F34D;',
                  '&#x1F96C;', '&#x1F966;', '&#x1F957;', '&#x1F366;', '&#x2615;', '&#x26F5;', '&#x1F388;', '&#x1F3A3;',
                  '&#x1F9F8;']
        reply = ''
        for i in range(0, random.randint(1, 10)):
            reply += emojis[random.randint(0, (len(emojis) - 1))]
        full_response = 'Maybe this will help \n ' + reply
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        message = dict(text=full_response,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        return {'status_code': 200}
