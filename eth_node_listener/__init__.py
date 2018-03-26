from flask import Flask
from eth_node_listener.eth_listener import ETHListener

import pika

CONFIG_FILE_PATH = '../config.py'

def create_eth_listener(app):
    mq_settings = app.config.get('ETH_MQ', None)
    if mq_settings:
        mq_credentials = pika.PlainCredentials(
            mq_settings.get('user', 'guest'),
            mq_settings.get('pass', 'guest')
        )
        parameters = pika.ConnectionParameters(
            host=mq_settings.get('host', 'localhost'),
            port=mq_settings.get('port', 5672),
            credentials=mq_credentials)
        eth_listener = ETHListener(
            app, amqp_connection_params=parameters,
            ws_addr=app.config.get('ETH_WS_ADDR', 'ws://localhost:8546'),
            rpc_addr=app.config.get('ETH_RPC_ADDR', 'http://127.0.0.1:8545'))
    else:
        eth_listener = ETHListener(
            app,
            ws_addr=app.config.get('ETH_WS_ADDR', 'ws://localhost:8546'),
            rpc_addr=app.config.get('ETH_RPC_ADDR', 'http://127.0.0.1:8545'))
    eth_listener.start(sub_new_head=True)

app = Flask(__name__)
app.config.from_pyfile(CONFIG_FILE_PATH)

create_eth_listener(app)


if __name__ == 'main':
    app.run()