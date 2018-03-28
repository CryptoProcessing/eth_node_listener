import websocket, json, pika, time
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
            rpc_addr='http://127.0.0.1:8545',
            amqp_connection_params=pika.ConnectionParameters(host='localhost'),
            queue_name='eth_node_events'):
        self._app = app
        self._ws_addr = ws_addr
        self._web3 = Web3(HTTPProvider(rpc_addr))

        self._amqp_connection = pika.BlockingConnection(amqp_connection_params)
        self._mq_queue_name = queue_name

        self._channel = self._amqp_connection.channel()
        self._channel.queue_declare(queue=self._mq_queue_name)

    def _publish_to_amqp(
            self, body='', 
            exchange='', routing_key='eth_node_events'):
        if not routing_key:
            routing_key = self._mq_queue_name
        self._channel.basic_publish(
            exchange=exchange, routing_key=routing_key, body=body)

    def _on_message(self, ws, message):
        try:
            j = json.loads(message)
            if 'id' in j:
                sub_id = j['result']
                if int(j['id']) == self.NEW_HEAD_SUB_MSG['id']:
                    self.new_head_sub_id = sub_id
                if int(j['id']) == self.NEW_TXS_SUB_MSG['id']:
                    self.new_txs_sub_id = sub_id
                return 'subscribed'
            else:
                result = self._process_sub_result(j)
                return result
        except Exception as e:
            print(e)

    def _on_error(self, ws, error):
        return

    def _on_close(self, ws):
        self._amqp_connection.close()
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
        block = self._web3.eth.getBlock(
            new_head['hash'], full_transactions=True)
        block_as_dict = dict(block)
        tx_list = []
        for tx in block['transactions']:
            tx_list.append(dict(tx))
        block_as_dict['transactions'] = tx_list
        mq_msg = {
            'ethNodeEvent': 'newHead',
            'data': block_as_dict,
        }
        self._publish_to_amqp(body=json.dumps(mq_msg))
        return mq_msg

    def _process_new_tx(self, new_tx):
        tx = self._web3.eth.getTransaction(new_tx)
        mq_msg = {
            'ethNodeEvent': 'newPendingTransaction',
            'data': dict(tx),
        }
        self._publish_to_amqp(body=json.dumps(mq_msg))
        return mq_msg
