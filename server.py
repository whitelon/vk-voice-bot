from aiohttp import web

import config  # noqa
from vk import handle_callback

app = web.Application()
app.add_routes([web.post('/bot', handle_callback)])


def run():
    web.run_app(app, port=80)


if __name__ == '__main__':
    run()
