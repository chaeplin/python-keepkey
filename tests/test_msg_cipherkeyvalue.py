import unittest
import common
import binascii

from keepkeylib.client import CallException

class TestMsgCipherkeyvalue(common.KeepKeyTest):

    def test_encrypt(self):
        self.setup_mnemonic_nopin_nopassphrase()

        # different ask values
        res = self.client.encrypt_keyvalue([0, 1, 2], "test", "testing message!", ask_on_encrypt=True, ask_on_decrypt=True)
        self.assertEqual(binascii.hexlify(res), '676faf8f13272af601776bc31bc14e8f')

        res = self.client.encrypt_keyvalue([0, 1, 2], "test", "testing message!", ask_on_encrypt=True, ask_on_decrypt=False)
        self.assertEqual(binascii.hexlify(res), '5aa0fbcb9d7fa669880745479d80c622')

        res = self.client.encrypt_keyvalue([0, 1, 2], "test", "testing message!", ask_on_encrypt=False, ask_on_decrypt=True)
        self.assertEqual(binascii.hexlify(res), '958d4f63269b61044aaedc900c8d6208')

        res = self.client.encrypt_keyvalue([0, 1, 2], "test", "testing message!", ask_on_encrypt=False, ask_on_decrypt=False)
        self.assertEqual(binascii.hexlify(res), 'e0cf0eb0425947000eb546cc3994bc6c')

        # different key
        res = self.client.encrypt_keyvalue([0, 1, 2], "test2", "testing message!", ask_on_encrypt=True, ask_on_decrypt=True)
        self.assertEqual(binascii.hexlify(res), 'de247a6aa6be77a134bb3f3f925f13af')

        # different message
        res = self.client.encrypt_keyvalue([0, 1, 2], "test", "testing message! it is different", ask_on_encrypt=True, ask_on_decrypt=True)
        self.assertEqual(binascii.hexlify(res), '676faf8f13272af601776bc31bc14e8f3ae1c88536bf18f1b44f1e4c2c4a613d')

        # different path
        res = self.client.encrypt_keyvalue([0, 1, 3], "test", "testing message!", ask_on_encrypt=True, ask_on_decrypt=True)
        self.assertEqual(binascii.hexlify(res), 'b4811a9d492f5355a5186ddbfccaae7b')

    def test_decrypt(self):
        self.setup_mnemonic_nopin_nopassphrase()

        # different ask values
        res = self.client.decrypt_keyvalue([0, 1, 2], "test", binascii.unhexlify("676faf8f13272af601776bc31bc14e8f"), ask_on_encrypt=True, ask_on_decrypt=True)
        self.assertEqual(res, 'testing message!')

        res = self.client.decrypt_keyvalue([0, 1, 2], "test", binascii.unhexlify("5aa0fbcb9d7fa669880745479d80c622"), ask_on_encrypt=True, ask_on_decrypt=False)
        self.assertEqual(res, 'testing message!')

        res = self.client.decrypt_keyvalue([0, 1, 2], "test", binascii.unhexlify("958d4f63269b61044aaedc900c8d6208"), ask_on_encrypt=False, ask_on_decrypt=True)
        self.assertEqual(res, 'testing message!')

        res = self.client.decrypt_keyvalue([0, 1, 2], "test", binascii.unhexlify("e0cf0eb0425947000eb546cc3994bc6c"), ask_on_encrypt=False, ask_on_decrypt=False)
        self.assertEqual(res, 'testing message!')

        # different key
        res = self.client.decrypt_keyvalue([0, 1, 2], "test2", binascii.unhexlify("de247a6aa6be77a134bb3f3f925f13af"), ask_on_encrypt=True, ask_on_decrypt=True)
        self.assertEqual(res, 'testing message!')

        # different message
        res = self.client.decrypt_keyvalue([0, 1, 2], "test", binascii.unhexlify("676faf8f13272af601776bc31bc14e8f3ae1c88536bf18f1b44f1e4c2c4a613d"), ask_on_encrypt=True, ask_on_decrypt=True)
        self.assertEqual(res, 'testing message! it is different')

        # different path
        res = self.client.decrypt_keyvalue([0, 1, 3], "test", binascii.unhexlify("b4811a9d492f5355a5186ddbfccaae7b"), ask_on_encrypt=True, ask_on_decrypt=True)
        self.assertEqual(res, 'testing message!')

    def test_encrypt_badlen(self):
        self.setup_mnemonic_nopin_nopassphrase()
        self.assertRaises(Exception, self.client.encrypt_keyvalue, [0, 1, 2], "test", "testing")

    def test_decrypt_badlen(self):
        self.setup_mnemonic_nopin_nopassphrase()
        self.assertRaises(Exception, self.client.decrypt_keyvalue, [0, 1, 2], "test", "testing")

if __name__ == '__main__':
    unittest.main()
