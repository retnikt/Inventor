import qrcode.image.svg

import random
import io

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LENGTH = 9


def gen_key():
    return ''.join(random.choice(ALPHABET) for _ in range(LENGTH))


def gen_qr(key):
    image = qrcode.make(key, image_factory=qrcode.image.svg.SvgPathFillImage)
    bytes_io = io.BytesIO()
    image.save(bytes_io)
    return bytes_io.getvalue()
