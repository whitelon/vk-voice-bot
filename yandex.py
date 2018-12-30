import config
import logging


oauth_token = config.yandex['OAuth_token']
folder_id = config.yandex['folderId']
iam_url = config.yandex['iam_url']
stt_url = config.yandex['stt_url']
iam_token = None


async def get_iam_token(session):
    json_request = {"yandexPassportOauthToken": oauth_token}
    async with session.post(iam_url, json=json_request) as resp:
        json_response = await resp.json()
        logging.debug(json_response)
        return json_response['iamToken']


async def recognize(audio, session):
    global iam_token
    if iam_token is None:
        iam_token = await get_iam_token(session)
    headers = {
        'Authorization': f'Bearer {iam_token}'
    }
    params = {
        'folderId': folder_id,
    }
    async with session.post(
        stt_url,
        params=params,
        headers=headers,
        data=audio
    ) as resp:
        json_resp = await resp.json()
        logging.debug(f'{resp.status} {json_resp}')
        if resp.status == 401:
            iam_token = await get_iam_token(session)
            return await recognize(audio, session)
        else:
            return json_resp['result']
