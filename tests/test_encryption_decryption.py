import unittest
import random
import nalenc


class MyTestCase(unittest.TestCase):
    def test_random(self):
        password = [random.randint(0, 255) for _ in range(512)]
        msg = [random.randint(0, 255) for _ in range(random.randint(1, 20000))]
        n = nalenc.NALEnc(password)
        enc = n.encrypt(msg)
        dec1 = n.decrypt(enc)
        dec2 = nalenc.NALEnc(password).decrypt(enc)
        self.assertEqual(msg, dec1)
        self.assertEqual(dec1, dec2)

    def test_static(self):
        rand = random.Random(42)
        passwd1, passwd2, passwd3 = list(range(256)) + list(range(256)), list(range(255, -1, -1)) + list(range(255, -1, -1)), [rand.randint(0, 255) for _ in range(512)]
        n = nalenc.NALEnc(passwd1)
        with open("msg1", "rb") as f:
            cont = f.read()
            self.assertEqual(b'test 1 complete', bytes(n.decrypt(cont)))
            self.assertEqual(cont, bytes(n.encrypt('test 1 complete')))
        n = nalenc.NALEnc(passwd2)
        with open("msg2", "rb") as f:
            cont = f.read()
            self.assertEqual(b'author is from Ukraine', bytes(n.decrypt(cont)))
            self.assertEqual(cont, bytes(n.encrypt('author is from Ukraine')))
        n = nalenc.NALEnc(passwd3)
        with open("msg3", "rb") as f:
            cont = f.read()
            self.assertEqual(b'test 3 complete', bytes(n.decrypt(cont)))
            self.assertEqual(cont, bytes(n.encrypt('test 3 complete')))


if __name__ == '__main__':
    unittest.main()