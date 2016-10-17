#coding: utf-8

import os
import math
import binascii
import hashlib
import sys
import random
from optparse import OptionParser

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

def encrypt(n, e, src_filename, dst_filename):
    ''' m**e ≡ c (mod n) -> c = m**e % n '''

    with open(src_filename, 'rb') as src_file:
        with open(dst_filename, 'wb') as dst_file:
            msg = src_file.read()

            en_msg = ''
            for ch in msg:
                magic_num = hex(gen_magic(ord(ch), e, n))
                en_msg += str(magic_num)

            dst_file.write(en_msg)

def decrypt(n, d, src_filename, dst_filename):
    ''' c**d ≡ m (mod n) -> m = c**d % n '''

    with open(src_filename, 'rb') as src_file:
        with open(dst_filename, 'wb') as dst_file:
            msg = src_file.read()
            msg = [c.replace('L', '').strip() for c in msg.split('0x') if c.strip() != '']

            de_msg = ''
            for ch in msg:
                de_msg += chr(gen_magic(long(ch, 16), d, n))

            dst_file.write(de_msg)

def main(options):
    x = -1
    n = 0
    e = 0

    if options.is_decrypt:
        n = options.n
        x = options.d
    src_filename = options.src_filename
    dst_filename = options.dst_filename

    while x < 0:
        # 1. get two big prim num
        prim_0 = get_big_prim(get_random())
        prim_1 = get_big_prim(get_random())
        while prim_1 == prim_0:
            prim_1 = get_big_prim(get_random())

        # 2. get n
        n = prim_0 * prim_1

        # 3. get n'
        n_ = (prim_0 - 1) * (prim_1 - 1)

        # 4. get prim x, 1 < x < n' and PRIM(x, n')
        rnd = random.randint(65537, max(int(str(n_)[:8]), 65537) + 1)
        e = get_big_prim(rnd)

        # 5. ed ≡ 1 (mod n') -> ed - 1 = k * n' -> ex + n'y = 1
        x, y = calc_x_y(e, n_)

    if not options.is_decrypt:
        with open(src_filename + '.rsa_meta', 'wb') as f:
            f.write('%s, %s\n%s, %s\n%s, %s' % (prim_0, prim_1, n, e, n, x))
        print 'gen rsa_meta done ...'

        encrypt(n, e, src_filename, dst_filename)

        print 'encrypt done ...'
    else:
        decrypt(n, x, src_filename, dst_filename)
        print 'decrypt done ...'

def ParseCmdArgs(argv = sys.argv[1:]):
    parser = OptionParser(usage = 'Usage: python %prog [options]',
                          version = '%prog v0.1, debug version',
                          description = "DESC: %prog  encrypt a 'short' file with RSA")
    parser.add_option('-s', '--src_file',
                      dest = 'src_filename',
                      help = "source filename to be encrypt(or decrypt)")
    parser.add_option('-d', '--dst_file',
                      dest = 'dst_filename',
                      help = "the encrypt(or decrypt) msg write on")
    parser.add_option('-t', '--decrypt',
                      dest = 'is_decrypt',
                      action = 'store_true',
                      default = False,
                      help = 'is decrypt src_filename ?')
    parser.add_option('-x', '--x',
                      dest = 'n',
                      default = 0,
                      type = int,
                      help = 'use to decrypt: (n, d)')
    parser.add_option('-y', '--y',
                      dest = 'd',
                      default = 0,
                      type = int,
                      help = 'use to decrypt: (n, d)')

    (options, args) = parser.parse_args(argv)
    if len(args) > 0:
        gLogger.error('unknow argument: %s' % str(args))
        parser.print_help()
        return None

    if options.is_decrypt == True:
        if options.d == 0 or options.n == 0:
            print "I need 'd' and 'n'"
            parser.print_help()
            return None

    if options.src_filename is None:
        print "I need 'src_filename'"
        parser.print_help()
        return None

    if options.dst_filename is None:
        print "I need 'dst_filename'"
        parser.print_help()
        return None

    return (options, args)

if __name__ == '__main__':
    ret = ParseCmdArgs()
    if ret is None:
        sys.exit(-1)

    main(ret[0])
