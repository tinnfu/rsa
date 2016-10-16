#coding: utf-8

import os
import math
import binascii
import hashlib
import sys
import random

def is_prim(num):
    assert num > 0

    if num == 1 or str(num).endswith('0'):
        return False

    if str(num).endswith('5'):
        return num == 5

    if num & 0x1 == 0:
        return num == 2

    ret = True 

    i = 2
    while i * i <= num:
        if num % i == 0:
            ret = False
            break
        i += 1

    return ret

def get_big_prim(start = 65535):
    num = start + 1
    while not is_prim(num):
        num += 1
    return num

def get_random():
    RND_FILE = '/dev/urandom'

    rnd = 0
    with open(RND_FILE, 'rb') as f:
        rnd = f.read(8)

    return long(binascii.b2a_hex(rnd)[:4], 16)

def ex_gcd(a, b, xy):
    ''' x0=y1; y0=x1-(a/b)*y1 '''

    if b == 0:
        xy[0] = 1
        xy[1] = 0
        return a

    r = ex_gcd(b,a%b,xy)
    t = xy[0]
    xy[0] = xy[1]
    xy[1] = t - a / b * xy[1]
    return r

def calc_x_y(a, b):
    ''' f(x, y) = 1 => a*x + b*y = 1'''

    xy = [0, 0]
    d = ex_gcd(a, b, xy)

    return xy


def md5sum(filename):
    md5 = ''
    with open(filename, 'r') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    return long(md5[:6], 16)

def gen_magic(a, b, m):
    r=1
    a %= m
    while b>1:
        if (b&1)!=0:
            r = (r*a)%m

        a = (a*a)%m
        b/=2

    return (r*a)%m

def encrypt(n, e, msg):
    ''' m**e ≡ c (mod n) -> c = m**e % n '''

    en_msg = ''
    for ch in msg:
        magic_num = hex(gen_magic(ord(ch), e, n))
        en_msg += str(magic_num)

    return en_msg

def decrypt(n, d, msg):
    ''' c**d ≡ m (mod n) -> m = c**d % n '''
    de_msg = []
    for ch in msg:
        de_msg.append(chr(gen_magic(long(ch, 16), d, n)))

    return de_msg

def main():
    x = -1
    n = 0
    e = 0
    while x < 0:
        # 1. get two big prim num
        prim_0 = get_big_prim(get_random())
        prim_1 = get_big_prim(get_random())
        while prim_1 == prim_0:
            prim_1 = get_big_prim(get_random())

        print 'p, q: %s, %s' % (prim_0, prim_1)

        # 2. get n
        n = prim_0 * prim_1

        # 3. get n'
        n_ = (prim_0 - 1) * (prim_1 - 1)

        # 4. get prim x, 1 < x < n' and PRIM(x, n')
        rnd = random.randint(65537, max(int(str(n_)[:8]), 65537) + 1)
        e = get_big_prim(rnd)

        # 5. ed ≡ 1 (mod n') -> ed - 1 = k * n' -> ex + n'y = 1
        x, y = calc_x_y(e, n_)

    print '(n, e): %s, %s' % (n, e)
    print '(n, d): %s, %s' % (n, x)

    def show_msg(de_msg):
        msg = ''
        for ch in de_msg:
            msg += ch

        print msg

    with open(sys.argv[1], 'r') as f:
        enc = encrypt(n, e, f.read())

    with open('%s.rsa' % sys.argv[1], 'w') as f:
        f.write(enc)

    buf = ''
    with open('%s.rsa' % sys.argv[1], 'r') as f:
        buf = f.read()
    buf = [c.strip() for c in buf.split('0x') if c.strip() != '']
    show_msg(decrypt(n, x, buf))

if __name__ == '__main__':
    main()
