with open('input_file', 'rb') as f:
    data = f.read()

signature = b'\xFF\xD8\xFF'
h_size = b'\x00\x08'
v_size = b'\x00\x08'

blocks = []
for i in range(0, len(data), 64):
    blocks.append(data[i:i+64])

for i, block in enumerate(blocks):
    blocks[i] = bytes([b-127 for b in block])

dct_blocks = []
for block in blocks:
    dct_block = []
    for u in range(8):
        for v in range(8):
            sum = 0
            for x in range(8):
                for y in range(8):
                    sum += (block[x*8+y] - 127) * \
                           math.cos((2*x+1)*u*math.pi/16) * \
                           math.cos((2*y+1)*v*math.pi/16)
            dct_block.append(int(sum/4))
    dct_blocks.append(dct_block)

for i, block in enumerate(dct_blocks):
    dct_blocks[i] = [int(b/8) for b in block]

zigzag = []
for i, block in enumerate(dct_blocks):
    flat_block = [block[j*8+k] for j in range(8) for k in range(8)]
    if i % 2 == 0:
        zigzag += flat_block
    else:
        zigzag += flat_block[::-1]

for i, val in enumerate(zigzag):
    if val < -127:
        zigzag[i] = -127
    elif val > 127:
        zigzag[i] = 127

while zigzag[-1] == 0:
    zigzag.pop()
zigzag.append(-128)

jpeg_data = bytes([min(127, max(-128, b)) for b in zigzag])

with open('output_file.jpg', 'wb') as f:
    f.write(signature + h_size + v_size + jpeg_data)

with open('output_file.jpg', 'rb') as f:
    data = f.read()

data = data[3:]

values = [int.from_bytes(data[i:i+1], signed=True) for i in range(len(data))]

blocks = []
block = []
for val in values:
    if val == -128:
        blocks.append(block)
        block = []
    else:
        block.append(val)

for i, block in enumerate(blocks):
    new_block = [0] * 64
    if i % 2 == 0:
        flat_block = block
    else:
        flat_block = block[::-1]
    for j, val in enumerate(flat_block):
        x, y = zigzag_to_xy(j)
        new_block[x*8+y] = val
    blocks[i] = new_block

for i, block in enumerate(blocks):
    blocks[i] = [b*8 for b in block]

for i, block in enumerate(blocks):
    inv_dct_block = []
    for x in range(8):
        for y in range(8):
            sum = 0
            for u in range(8):
                for v in range(8):
                    sum += math.cos((2*x+1)*u*math.pi/16) * \
                           math.cos((2*y+1)*v*math.pi/16) * \
                           blocks[i][u*8+v]
            inv_dct_block.append(int(sum/4))
    blocks[i] = [b+127 for b in inv_dct_block]

data = bytes([min(255, max(0, b)) for block in blocks for b in block])
data += b'\x00' * (len(data) % 64)

with open('output_file', 'wb') as f:
    f.write(data)