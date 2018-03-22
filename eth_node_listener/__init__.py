from flask import Flask
from eth_node_listener.eth_listener import ETHListener

app = Flask(__name__)

eth_listener = ETHListener(app)
eth_listener.start(sub_new_head=True, sub_new_txs=True)

@app.route('/')
def hello():
    return "Hello"

if __name__ == 'main':
    app.run()