# Gives a GIF whose frames all carry local colour tables a global colour table (frame 0's palette,
# which frame 0 then uses directly): the layout every decoder expects, Apple's ImageIO (Safari) included.
import struct, sys
d = open(sys.argv[1], 'rb').read(); out = bytearray()
w, h, flags = struct.unpack('<HHB', d[6:11]); assert not flags & 0x80, 'already has a global table'
pos = 13
# find the first image descriptor (skip extensions)
p = pos
while d[p] == 0x21:
    p += 2
    while d[p]: p += 1 + d[p]
    p += 1
assert d[p] == 0x2C
lflags = d[p + 9]; assert lflags & 0x80
size = 3 * 2 ** ((lflags & 7) + 1); lct = d[p + 10:p + 10 + size]
out += d[:6] + struct.pack('<HHB', w, h, 0xF0 | (lflags & 7)) + d[11:13] + lct      # global table = frame 0's
out += d[pos:p] + d[p:p + 9] + bytes([lflags & 0x40]) + d[p + 10 + size:]          # frame 0 drops its local copy
open(sys.argv[2], 'wb').write(out); print(len(out))
