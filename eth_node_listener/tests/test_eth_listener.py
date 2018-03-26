import unittest, json

from unittest.mock import patch, Mock

from eth_node_listener.tests.base import BaseTestCase

from eth_node_listener.eth_listener import ETHListener

class TestEthereumListener(BaseTestCase):

    def setUp(self):
        super(TestEthereumListener, self).setUp()
        self.eth_listener = ETHListener(self.app)

    def test_default_params(self):
        self.assertEqual(self.eth_listener._ws_addr, 'ws://localhost:8546')
        self.assertEqual(self.eth_listener._mq_queue_name, 'eth_node_events')

    def test_eth_event_subscrive(self):

        sub_new_head_response = '{"jsonrpc":"2.0","id":1,"result":"0x158fe87f5cf3dff06e50dbd3e81b2242"}'
        sub_new_pending_tx_response = '{"jsonrpc":"2.0","id":2,"result":"0xe23f4554e89b8200e5b01a8e135a75fd"}'

        self.eth_listener._on_message(None, sub_new_head_response)
        self.assertEqual(
            self.eth_listener.new_head_sub_id, 
            '0x158fe87f5cf3dff06e50dbd3e81b2242')
        self.assertEqual(self.eth_listener.new_txs_sub_id, '')

        self.eth_listener._on_message(None, sub_new_pending_tx_response)
        self.assertEqual(
            self.eth_listener.new_txs_sub_id, 
            '0xe23f4554e89b8200e5b01a8e135a75fd')

        sub_result_obj = {
            "jsonrpc": "2.0",
            "method": "eth_subscription",
            "params": {
                "subscription":"0xe23f4554e89b8200e5b01a8e135a75fd",
                "result": "0x7fdad3955043ea23a677ab9af4838e4e083ba794be4ea0f19b0798e43245ec10",
            }
        }
        sub_result_msg = json.dumps(sub_result_obj)
        
        mock_obj = self.eth_listener
        mock_obj._process_sub_result = Mock(return_value='sub result')
        res = self.eth_listener._on_message(None, sub_result_msg)
        self.assertEqual(res, 'sub result')

    def test_ws_msg_parse(self):
        mock_obj = self.eth_listener
        mock_obj._process_new_head = Mock(return_value='new head')
        mock_obj._process_new_tx = Mock(return_value='new tx')

        self.eth_listener.new_head_sub_id = '0x158fe87f5cf3dff06e50dbd3e81b2242'
        self.eth_listener.new_txs_sub_id = '0xe23f4554e89b8200e5b01a8e135a75fd'

        new_head_obj = {
            "jsonrpc": "2.0",
            "method": "eth_subscription",
            "params": {
                "subscription":"0x158fe87f5cf3dff06e50dbd3e81b2242",
                "result": {
                    "parentHash":"0x861460c705436142ea7eaf3a8fe4f2409188db79d8c485d431b3bedb2cbc8a44",
                    "sha3Uncles":"0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
                    "miner":"0x4badd354e0edda5ebdc7ca00e084be02449db03f",
                    "stateRoot":"0x9cb77ba9ac09c43ce5c323209ff75ba1e8bcd174deed60d91a60cba379f4ad62",
                    "transactionsRoot":"0xd167e0629b7029a06a09e423ae22619901f495e9e4b09c2593fbd7e228ba8103",
                    "receiptsRoot":"0xc31797c9aabe8ca46ac19808046ccc2b31c5909072590896c23add4cbb195c14",
                    "logsBloom":"0x0",
                    "difficulty":"0x1a0d3238",
                    "number":"0x2ba6bb",
                    "gasLimit":"0x47e7c4",
                    "gasUsed":"0x2eaf2c",
                    "timestamp":"0x5aae8cdf",
                    "extraData":"0xd783010702846765746885676f312e398777696e646f7773",
                    "mixHash":"0xa7472c0c8b88c1557a58dc2244efe4f6b44b87ac7d338c20369f13968c48f61a",
                    "nonce":"0xdd0635a005f64414",
                    "hash":"0xf05d00e92dfc5397779023b0ccaa01dea1fe04882e61b077852d96f3219cf098"
                }
            }
        }
        new_head_msg = json.dumps(new_head_obj)
        new_tx_obj = {
            "jsonrpc": "2.0",
            "method": "eth_subscription",
            "params": {
                "subscription":"0xe23f4554e89b8200e5b01a8e135a75fd",
                "result": "0x7fdad3955043ea23a677ab9af4838e4e083ba794be4ea0f19b0798e43245ec10",
            }
        }
        new_tx_msg = json.dumps(new_tx_obj)

        res = self.eth_listener._on_message(None, new_head_msg)
        self.assertEqual(res, 'new head')
        res = self.eth_listener._on_message(None, new_tx_msg)
        self.assertEqual(res, 'new tx')

    @patch('web3.eth.Eth.getBlock')
    def test_process_new_head(self, mock_get_block):
        mock_get_block.return_value = {
            'hash': '0xf05d00e92dfc5397779023b0ccaa01dea1fe04882e61b077852d96f3219cf098', 
            'transactions': [
                {
                    'blockHash': '0x13ae71542d56f6f2d8c461c1e144e67bb6a13e189a0a194e1511b72436224c71', 
                    'blockNumber': 2834271, 
                    'from': '0x0D6CE14b31A5a5F7e3F206AE9a022D59ACAAaCFF', 
                    'gas': 471238, 
                    'gasPrice': 31000000000, 
                    'hash': '0x96694c93ae2393945dd3d21392a78da5ec0f14be373f9747c5bbd7175ad64ebf', 
                    'nonce': 98, 
                    'to': None, 
                    'input': '',
                    'transactionIndex': 0, 
                    'value': 0,
                }, 
                {
                    'blockHash': '0x13ae71542d56f6f2d8c461c1e144e67bb6a13e189a0a194e1511b72436224c71', 
                    'blockNumber': 2834271, 
                    'from': '0xdB427262Ed122f6E849060E23FdA96927DD44Fc4', 
                    'gas': 1000000, 
                    'gasPrice': 5000000000, 
                    'hash': '0xd3da732c9473fb15b57b2457714fe18bf0f47dac1c1da2daaba635e6930daa3c', 
                    'nonce': 38659, 
                    'to': '0xE1421B0AaA23b8DBdA90Fb3F9145f546f1740FC5', 
                    'input': '',
                    'transactionIndex': 1, 
                    'value': 0,
                },
            ],
        }
        mock_obj = self.eth_listener
        mock_obj._publish_to_amqp = Mock(return_value='published')

        new_head = {
            'parentHash': '0x861460c705436142ea7eaf3a8fe4f2409188db79d8c485d431b3bedb2cbc8a44',
            'sha3Uncles': '0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347',
            'miner': '0x4badd354e0edda5ebdc7ca00e084be02449db03f',
            'stateRoot': '0x9cb77ba9ac09c43ce5c323209ff75ba1e8bcd174deed60d91a60cba379f4ad62',
            'transactionsRoot': '0xd167e0629b7029a06a09e423ae22619901f495e9e4b09c2593fbd7e228ba8103',
            'receiptsRoot': '0xc31797c9aabe8ca46ac19808046ccc2b31c5909072590896c23add4cbb195c14',
            'logsBloom': '0x0',
            'difficulty': '0x1a0d3238',
            'number': '0x2ba6bb',
            'gasLimit': '0x47e7c4',
            'gasUsed': '0x2eaf2c',
            'timestamp': '0x5aae8cdf',
            'extraData': '0xd783010702846765746885676f312e398777696e646f7773',
            'mixHash': '0xa7472c0c8b88c1557a58dc2244efe4f6b44b87ac7d338c20369f13968c48f61a',
            'nonce': '0xdd0635a005f64414',
            'hash': '0xf05d00e92dfc5397779023b0ccaa01dea1fe04882e61b077852d96f3219cf098'
        }

        res = self.eth_listener._process_new_head(new_head)
        self.assertEqual(res['ethNodeEvent'], 'newHead')
        self.assertEqual(res['data']['hash'], new_head['hash'])
        self.assertEqual(len(res['data']['transactions']), 2)

    @patch('web3.eth.Eth.getTransaction')
    def test_process_new_tx(self, mock_get_tx):
        mock_get_tx.return_value = {
            'blockHash': '0x13ae71542d56f6f2d8c461c1e144e67bb6a13e189a0a194e1511b72436224c71', 
            'blockNumber': 2834271, 
            'from': '0xdB427262Ed122f6E849060E23FdA96927DD44Fc4', 
            'gas': 1000000, 
            'gasPrice': 5000000000, 
            'hash': '0xd3da732c9473fb15b57b2457714fe18bf0f47dac1c1da2daaba635e6930daa3c', 
            'nonce': 38659, 
            'to': '0xE1421B0AaA23b8DBdA90Fb3F9145f546f1740FC5', 
            'input': '',
            'transactionIndex': 1, 
            'value': 0,
        }

        new_tx = '0xd3da732c9473fb15b57b2457714fe18bf0f47dac1c1da2daaba635e6930daa3c'

        mock_obj = self.eth_listener
        mock_obj._publish_to_amqp = Mock(return_value='published')

        res = self.eth_listener._process_new_tx(new_tx)
        self.assertEqual(res['ethNodeEvent'], 'newPendingTransaction')
        self.assertEqual(res['data']['hash'], new_tx)