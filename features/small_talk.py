from webex import WebExClient
import random
from features.catch_all import catch_all


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

    if activity.get('text') == 'affirmation':
        responses = ['You are naturally funny', 'You always have something funny to say',
                     'You have a great sense of humor', 'You see the funny side of every situation',
                     'You are always making others laugh and brightening their day',
                     'You are sharp witted and full of funny ideas',
                     'Others hang on your every word because you’re always making everyone laugh',
                     'You laugh at yourself and this makes your life so much easier',
                     'You make others calm with your ability to find funniness in stressful situations',
                     'You are naturally charismatic', 'You become funnier with each passing day',
                     'You are turning into someone who always has something funny to say',
                     'Others are starting to see that you are a really funny person',
                     'You see the funny side of life more and more',
                     'You are transforming into someone who is outgoing and makes others laugh',
                     'Being funny seems to be taking less effort',
                     'You are noticing that others are more drawn to you because you are funny',
                     'You are feeling wittier and more naturally funny', 'Life is becoming easier and less serious',
                     'My mind is becoming much sharper', 'Seeing the funny side of life comes naturally to you\t',
                     'Others see you as outgoing and full of laughter',
                     'You love cracking a good joke at the perfect moment', 'You make people laugh wherever y go',
                     'Coming up with funny things to say is easy for you',
                     'You can calm any situation by having a good laugh',
                     'You just naturally see the funny side to life', 'Making others laugh is easy for you',
                     'My mind is just naturally sharp and witty all the time',
                     'You find it easy to laugh at yourself and make light of any situation',
                     'You are a wonderful person', 'The more you like yourself, the more others will like you',
                     'You are becoming better with each day', 'You are happy to be here',
                     'You have people who care about you and will help you if you need it',
                     'You will ask for help if you need it',
                     'You are always learning more about who you are and what matters to you',
                     'You understand that your actions become habits so you will try to do the right thing',
                     'You love and respect your family for all they do for you',
                     'You are an intelligent being, but you don’t know everything',
                     'You are proud to represent the values that matter to you and your community', 'You love yourself',
                     'You feel lucky to have the opportunities that you do', 'Your dreams are achievable',
                     'The only people who may be judging you, are the people who are most afraid of being judged',
                     'In 5 years it is not going to matter what you wore today',
                     'In 15 years the only thing that will remain is what you have learned',
                     'People can be mean, but it only reflects the kind of person they are',
                     'You are happy. Who else are you trying to please?',
                     'You accept and love the way you look without comparing yourself to others',
                     'You are completely unique and therefore, there are no rules to what you are and are not',
                     'You give yourself permission to do what is best for you',
                     'You admit that you may not always know what is best for you, so you are open to advice from people who you respect',
                     'You do not need drugs or alcohol to have fun',
                     'You do not need to share every personal detail with your entire social network',
                     'You are responsible with your technology', 'Your opinion matters',
                     'You acknowledge that sometimes it is not appropriate to voice your opinion',
                     'You care about what is going on in the world', 'You can say no, and no will mean no',
                     'You stand up for yourself because you matter', 'You love yourself unconditionally',
                     'You see the beauty in stopping to appreciate your blessings',
                     'You are not in a race, there is plenty of time',
                     'Reputation is important, but it is not defining', 'Your friends are not always right',
                     "You are not lost, your're still creating yourself",
                     'When there is a bump in the road, you keep going',
                     'If someone is trying to bring you down, it means you are above them',
                     'You have all the tools to be successful',
                     'Though times may be difficult, they will eventually get better',
                     'You do not regret yesterday and you are excited for tomorrow', 'This is only the beginning',
                     'You will do better next time', 'You haven’t even seen what you are capable of yet',
                     'You will savor your youth', 'You do not wish for age but instead experiences and knowledge',
                     'You will do today what you will appreciate tomorrow',
                     'You begin your day by affirming the positive and end your day with gratitude',
                     'You are doing work that you enjoy and find fulfilling',
                     'You play a big role in your own career success',
                     'You ask for and do meaningful, wonderful and rewarding work',
                     'You engage in work that impacts this world positively',
                     'You believe in your ability to change the world with the work that you do', 'You are enough',
                     'You are worthy', "You're proud of yourself", 'Nobody else is like you',
                     'You deserve to treat yourself', "You're strong", 'You deserve a beautiful life',
                     'Not everyone has to like you', 'You are here for a reason',
                     "You're releasing self-judgement and embracing self-love",
                     'Your friends and family love you for who you are', 'You love your body',
                     "You're not perfect, but nobody is", 'You love you life', 'You deserve love',
                     "You're good enough, smart enough, and, doggone it, people like you",
                     "You're kind of a big deal"]
        reply = responses[random.randint(0, (len(responses) - 1))]
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        message = dict(text=reply,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        return {'status_code': 200}

    if activity.get('text') == 'accept_apology':
        responses = ["It's ok &#x1F60A;",
                     "About what? &#x1F609;",
                     "Apology accepted! &#x1F60A;",
                     "Sorry fixed everything &#x1F60A;",
                     "Thank you for being wonderful &#x1F60D;"]
        reply = responses[random.randint(0, (len(responses) - 1))]
        webex = WebExClient(webex_bot_token=activity['webex_bot_token'])
        message = dict(text=reply,
                       roomId=activity['roomId'],
                       attachments=[])
        await webex.post_message_to_webex(message)
        return {'status_code': 200}

    await catch_all(activity)
    return {'status_code': 200}
