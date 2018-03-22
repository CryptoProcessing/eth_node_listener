import websocket
import json
import threading

from web3 import Web3, HTTPProvider

class ETHListener:
    NEW_HEAD_SUB_MSG = {
        'id': 1,
        'method': 'eth_subscribe',
        'params': ['newHeads'],
    }
    NEW_TXS_SUB_MSG = {
        'id': 2,
        'method': 'eth_subscribe',
        'params': ['newPendingTransactions'],
    }

    _ws = None

    _sub_new_head, _sub_new_txs = True, False

    new_head_sub_id, new_txs_sub_id  = '', ''

    def __init__(
            self, app,
            ws_addr='ws://localhost:8546',
            rpc_addr='http://127.0.0.1:8545'):
        self._app = app
        self._ws_addr = ws_addr
        self._web3 = Web3(HTTPProvider(rpc_addr))

    def _on_message(self, ws, message):
        print(message)
        j = json.loads(message)
        if 'id' in j:
            sub_id = j['result']
            if int(j['id']) == self.NEW_HEAD_SUB_MSG['id']:
                self.new_head_sub_id = sub_id
            if int(j['id']) == self.NEW_TXS_SUB_MSG['id']:
                self.new_txs_sub_id = sub_id
        else:
            result = self._process_sub_result(j)

    def _on_error(self, ws, error):
        return

    def _on_close(self, ws):
        return

    def _on_open(self, ws):
        def run(*args):
            if self._sub_new_head:
                ws.send(json.dumps(self.NEW_HEAD_SUB_MSG))
            if self._sub_new_txs:
                ws.send(json.dumps(self.NEW_TXS_SUB_MSG))

        th = threading.Thread(target=run)
        th.daemon = True
        th.start()

    def start(self, sub_new_head=True, sub_new_txs=False):
        self._ws = websocket.WebSocketApp(
            self._ws_addr,
            on_open=self._on_open, on_message=self._on_message,
            on_error=self._on_error, on_close=self._on_close)
    
        self._sub_new_head = sub_new_head
        self._sub_new_txs = sub_new_txs

        self._ws = threading.Thread(target=self._ws.run_forever)
        self._ws.daemon = True
        self._ws.start()

    def _process_sub_result(self, result):
        res = result['params']['result']
        if result['params']['subscription'] == self.new_head_sub_id:
            return self._process_new_head(res)
        if result['params']['subscription'] == self.new_txs_sub_id:
            return self._process_new_tx(res)

    def _process_new_head(self, new_head):
        block = self._web3.eth.getBlock(new_head['hash'], full_transactions=True)
        print('new head')
        return

    def _process_new_tx(self, new_tx):
        tx = self._web3.eth.getTransaction(new_tx)
        print('new tx')
        return
