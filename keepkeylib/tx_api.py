# This file is part of the TREZOR project.
#
# Copyright (C) 2012-2016 Marek Palatinus <slush@satoshilabs.com>
# Copyright (C) 2012-2016 Pavol Rusnak <stick@satoshilabs.com>
# Copyright (C) 2016      Jochen Hoenicke <hoenicke@gmail.com>
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

import binascii
from decimal import Decimal
import requests
import json
from . import types_pb2 as proto_types

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

cache_dir = None

class TxApi(object):

    def __init__(self, network, url):
        self.network = network
        self.url = url

    def fetch_json(self, url, resource, resourceid):
        global cache_dir
        if cache_dir:
            cache_file = '%s/%s_%s_%s.json' % (cache_dir, self.network, resource, resourceid)
            try: # looking into cache first
                j = json.load(open(cache_file))
                return j
            except:
                pass
        try:
            r = requests.get('%s/%s/%s' % (self.url, resource, resourceid), headers={'User-agent': 'Mozilla/5.0'})
            j = r.json()
        except:
            raise Exception('URL error: %s' % url)
        if cache_file:
            try: # saving into cache
                json.dump(j, open(cachefile, 'w'))
            except:
                pass
        return j

    def get_tx(self, txhash):
        raise NotImplementedError


class TxApiInsight(TxApi):

    def __init__(self, network, url, zcash=None):
        super(TxApiInsight, self).__init__(network, url)
        self.zcash = zcash

    def get_tx(self, txhash):

        data = self.fetch_json(self.url, 'tx', txhash)

        t = proto_types.TransactionType()
        t.version = data['version']
        t.lock_time = data['locktime']

        for vin in data['vin']:
            i = t.inputs.add()
            if 'coinbase' in vin.keys():
                i.prev_hash = b"\0"*32
                i.prev_index = 0xffffffff # signed int -1
                i.script_sig = binascii.unhexlify(vin['coinbase'])
                i.sequence = vin['sequence']

            else:
                i.prev_hash = binascii.unhexlify(vin['txid'])
                i.prev_index = vin['vout']
                i.script_sig = binascii.unhexlify(vin['scriptSig']['hex'])
                i.sequence = vin['sequence']

        for vout in data['vout']:
            o = t.bin_outputs.add()
            o.amount = int(Decimal(str(vout['value'])) * 100000000)
            o.script_pubkey = binascii.unhexlify(vout['scriptPubKey']['hex'])

        if self.zcash:
            if t.version == 2:
                joinsplit_cnt = len(data['vjoinsplit'])
                if joinsplit_cnt == 0:
                    t.extra_data =b'\x00'
                else:
                    if joinsplit_cnt >= 253:
                        # we assume cnt < 253, so we can treat varIntLen(cnt) as 1
                        raise ValueError('Too many joinsplits')
                    extra_data_len = 1 + joinsplit_cnt * 1802 + 32 + 64
                    raw = self.fetch_json(self.url, 'rawtx', txhash)
                    raw = binascii.unhexlify(raw['rawtx'])
                    t.extra_data = raw[-extra_data_len:]

        return t

    def get_raw_tx(self, txhash):
        data = self.fetch_json(self.url, 'rawtx', txhash)['rawtx']
        return data

class TxApiSmartbit(TxApi):

    def get_tx(self, txhash):

        data = self.fetch_json(self.url, 'tx', txhash)

        data = data['transaction']

        t = proto_types.TransactionType()
        t.version = int(data['version'])
        t.lock_time = data['locktime']

        for vin in data['inputs']:
            i = t.inputs.add()
            if 'coinbase' in vin.keys():
                i.prev_hash = b"\0"*32
                i.prev_index = 0xffffffff # signed int -1
                i.script_sig = binascii.unhexlify(vin['coinbase'])
                i.sequence = vin['sequence']

            else:
                i.prev_hash = binascii.unhexlify(vin['txid'])
                i.prev_index = vin['vout']
                i.script_sig = binascii.unhexlify(vin['script_sig']['hex'])
                i.sequence = vin['sequence']

        for vout in data['outputs']:
            o = t.bin_outputs.add()
            o.amount = int(Decimal(vout['value']) * 100000000)
            o.script_pubkey = binascii.unhexlify(vout['script_pub_key']['hex'])

        return t

# rpc ----
rpcuser = None
rpcpassword = None
rpcbindip = None
rpcport = None

def get_tx_rpc(txhash):
    global rpcuser, rpcpassword, rpcbindip, rpcport
    serverURL = 'http://' + rpcuser + ':' + rpcpassword + '@' + rpcbindip + ':' + str(rpcport)
    access = AuthServiceProxy(serverURL)

    data = access.getrawtransaction(txhash.decode("utf-8"), 1)

    t = proto_types.TransactionType()
    t.version = data['version']
    t.lock_time = data['locktime']

    for vin in data['vin']:
        i = t.inputs.add()
        if 'coinbase' in vin.keys():
            i.prev_hash = binascii.unhexlify(b'0000000000000000000000000000000000000000000000000000000000000000')
            i.prev_index = 0xffffffff # signed int -1
            i.script_sig = binascii.unhexlify(vin['coinbase'])
            i.sequence = vin['sequence']

        else:
            i.prev_hash = binascii.unhexlify(vin['txid'])
            i.prev_index = vin['vout']
            i.script_sig = binascii.unhexlify(vin['scriptSig']['hex'])
            i.sequence = vin['sequence']

    for vout in data['vout']:
        o = t.bin_outputs.add()
        o.amount = int(Decimal(str(vout['value'])) * 100000000)
        o.script_pubkey = binascii.unhexlify(vout['scriptPubKey']['hex'])

    return t

class TXAPIDashrpc(object):
    def get_tx(self, txhash):
        rpc_raw_tx = get_tx_rpc(txhash)
        return rpc_raw_tx

TxApiBitcoin = TxApiInsight(network='insight_bitcoin', url='https://insight.bitpay.com/api/')
TxApiTestnet = TxApiInsight(network='insight_testnet', url='https://test-insight.bitpay.com/api/')
TxApiSegnet = TxApiSmartbit(network='smartbit_segnet', url='https://segnet-api.smartbit.com.au/v1/blockchain/')
TxApiZcashTestnet = TxApiInsight(network='insight_zcashtestnet', url='https://explorer.testnet.z.cash/api/', zcash=True)
