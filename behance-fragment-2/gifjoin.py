# Joins GIFs that each use their own global palette into one looping GIF:
# every frame of every input gets that input's palette as a local colour table.
import struct, sys

def parse(path):
    d = open(path, 'rb').read()
    assert d[:6] in (b'GIF89a', b'GIF87a')
    w, h, flags = struct.unpack('<HHB', d[6:11])
    pos = 13
    gct = b''
    if flags & 0x80:
        size = 3 * (2 ** ((flags & 7) + 1)); gct = d[pos:pos + size]; pos += size
    blocks = []
    while pos < len(d):
        b = d[pos]
        if b == 0x3B: break
        if b == 0x21:                                  # extension: keep all except NETSCAPE loop
            label = d[pos + 1]; start = pos; pos += 2
            app = b''
            while True:
                n = d[pos]; 
                if label == 0xFF and not app: app = d[pos + 1:pos + 1 + n]
                pos += 1 + n
                if n == 0: break
            if not app.startswith(b'NETSCAPE'): blocks.append(d[start:pos])
        elif b == 0x2C:                                # image: descriptor (+ local table) + data
            desc = bytearray(d[pos:pos + 10]); pos += 10
            lflags = desc[9]; lct = b''
            if lflags & 0x80:
                size = 3 * (2 ** ((lflags & 7) + 1)); lct = d[pos:pos + size]; pos += size
            start = pos; pos += 1                      # LZW min code size
            while True:
                n = d[pos]; pos += 1 + n
                if n == 0: break
            blocks.append(('img', bytes(desc), lct, d[start:pos]))
        else: raise ValueError('bad block %x at %d' % (b, pos))
    return w, h, flags, gct, blocks

out = bytearray(b'GIF89a')
inputs = [parse(p) for p in sys.argv[2:]]
w, h = inputs[0][0], inputs[0][1]
out += struct.pack('<HHBBB', w, h, 0x70, 0, 0)          # no global table; every frame has its own
out += b'\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00'    # loop forever
for _, _, gflags, gct, blocks in inputs:
    bits = gflags & 7
    for blk in blocks:
        if isinstance(blk, tuple):
            _, desc, lct, data = blk
            desc = bytearray(desc)
            if not lct:                                # attach this input's palette locally
                desc[9] = (desc[9] & 0x40) | 0x80 | bits; lct = gct
            out += desc + lct + data
        else:
            out += blk
out += b'\x3B'
open(sys.argv[1], 'wb').write(out)
print(len(out))
