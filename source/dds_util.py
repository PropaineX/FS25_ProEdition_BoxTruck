# DDS writing helper shared by the texture scripts.
import os, struct
from PIL import Image

def save_dds_mips(img, path, fmt):
    """DXT1/DXT5 .dds with a full mipmap chain: Pillow writes one level per file; the levels are joined here."""
    levels = []; cur = img
    while True:
        tmp = path + '.lvl.dds'; cur.save(tmp, pixel_format=fmt)
        data = open(tmp, 'rb').read(); os.remove(tmp)
        if not levels: header = bytearray(data[:128])
        levels.append(data[128:])
        if cur.width == 1 and cur.height == 1: break
        cur = cur.resize((max(1, cur.width // 2), max(1, cur.height // 2)), Image.LANCZOS)
    struct.pack_into('<I', header, 8, struct.unpack_from('<I', header, 8)[0] | 0x20000)      # DDSD_MIPMAPCOUNT
    struct.pack_into('<I', header, 28, len(levels))                                           # mipMapCount
    struct.pack_into('<I', header, 108, struct.unpack_from('<I', header, 108)[0] | 0x400008)  # COMPLEX | MIPMAP
    open(path, 'wb').write(bytes(header) + b''.join(levels))
    return len(levels)
