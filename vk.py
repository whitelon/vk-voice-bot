import config
import logging
from aiohttp import ClientSession, web
from random import randint


bot_token = config.vk['bot_token']
api_link = config.vk['api_link']
api_version = config.vk['api_version']
confirmation_string = config.vk['confirmation_string']


def parameters(**kwargs):
    params = {
        'v': api_version,
        'access_token': bot_token
    }
    params.update(kwargs)
    return params


async def get_user_name(session, user_id):
    get_user_params = parameters(user_ids=user_id)

    async with session.get(api_link + 'users.get',
                           params=get_user_params) as resp:
        user = await resp.json()
        logging.debug(user)
        user = user['response'][0]

        return user['first_name']


async def get_group_name(session, group_id):
    get_group_params = parameters(group_ids=group_id)

    async with session.get(api_link + 'groups.getById',
                           params=get_group_params) as resp:
        group = await resp.json()
        logging.debug(group)
        group = group['response'][0]

        return group['name']


async def get_sender_name(session, sender_id):
    if sender_id > 0:
        return await get_user_name(session, sender_id)
    elif sender_id < 0:
        return await get_group_name(session, sender_id)


def find_audio(message):
    if len(message['attachments']) > 0 and \
       message['attachments'][0]['type'] == 'audio_message':
            return message['attachments'][0]['audio_message']['link_ogg']
    else:
            return None


async def send_message(session, recipient_id, message_text):
    send_message_params = parameters(message=message_text,
                                     peer_id=recipient_id,
                                     random_id=randint(0, 2000000000))

    await session.get(api_link + 'messages.send',
                      params=send_message_params)


async def handle_message(message, level=0, recipient_id=None):
    sender_id = message['from_id']
    recipient_id = recipient_id or message['peer_id']
    text = message['text'] or '--'
    audio = find_audio(message)

    async with ClientSession() as session:

        for inner_message in message.get('fwd_messages', []):
            await handle_message(inner_message, level + 1, recipient_id)

        sender_name = await get_sender_name(session, sender_id)
        response_text = f'{"| "*level}{sender_name}: {audio or text}'
        await send_message(session, recipient_id, response_text)


async def handle_callback(request):
    message = await request.json()
    logging.debug(message)

    if message['type'] == 'message_new':
        await handle_message(message['object'])

    elif message['type'] == 'confirmation':
        return web.Response(text=confirmation_string)

    return web.Response(text='ok')
