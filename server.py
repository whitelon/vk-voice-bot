from aiohttp import web

import config  # noqa
import vk
import yandex


async def download_small_file(file_link, session):
    async with session.get(file_link) as resp:
        file = await resp.read()
        return file


async def recognize(audio_link, session):
    audio = await download_small_file(audio_link, session)
    recognized_text = await yandex.recognize(audio, session)
    return recognized_text


app = web.Application()
app.add_routes([web.post('/bot', vk.handle_callback)])


def run():
    web.run_app(app, port=80)


if __name__ == '__main__':
    run()
