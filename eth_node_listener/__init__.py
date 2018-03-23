from flask import Flask
from eth_node_listener.eth_listener import ETHListener

CONFIG_FILE_PATH = '../config.py'

app = Flask(__name__)
app.config.from_pyfile(CONFIG_FILE_PATH)

eth_listener = ETHListener(
    app,
    ws_addr=app.config.get('ETH_WS_ADDR', 'ws://localhost:8546'),
    rpc_addr=app.config.get('ETH_RPC_ADDR', 'http://127.0.0.1:8545'))
eth_listener.start(sub_new_head=True, sub_new_txs=True)


if __name__ == 'main':
    app.run()