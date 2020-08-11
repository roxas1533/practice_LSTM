import glob
from binascii import *
from types import *
import sys
import os


def variable(b, midi, list):
    while b > b'\x80':
        b = midi.read(1)
        list.append(int.from_bytes(b, 'big'))


def read_midi(path):
    flag = False
    with open(path, mode='rb') as midi:
        data = {'header': [], 'tracks': []}
        track = {'header': [], 'chunks': []}
        chunk = {'delta': [], 'status': [], 'meta': [], 'length': [], 'body': []}
        bs = midi.read(14)
        data['header'] = [b for b in bs]
        lastEvent = b''
        while 1:
            if flag or bs == b'':
                break
            bs = midi.read(4)
            track['header'] = [b for b in bs]
            bs = midi.read(4)
            track['header'] += [b for b in bs]
            MaxPoint = int.from_bytes(bs, 'big')
            lastPoint = midi.tell()
            SRR = False  # ステータスランニングルール
            while (midi.tell() - lastPoint) < MaxPoint:
                if flag:
                    break
                if not SRR:
                    b = midi.read(1)
                    chunk['delta'].append(int.from_bytes(b, 'big'))
                    variable(b, midi, chunk['delta'])
                    b = midi.read(1)
                if b == b'\xFF':
                    SRR = False
                    lastEvent = b
                    chunk['status'].append(int.from_bytes(b, 'big'))
                    b = midi.read(1)
                    if b in (b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07'):
                        chunk['meta'].append(int.from_bytes(b, 'big'))
                        b = midi.read(1)
                        chunk['length'].append(int.from_bytes(b, 'big'))
                        bs = midi.read(int.from_bytes(b, 'big'))
                        chunk['body'] += [b for b in bs]
                    elif b == b'\x20':
                        chunk['meta'].append(int.from_bytes(b, 'big'))
                        bs = midi.read(1)
                        chunk['meta'] += [b for b in bs]
                        b = midi.read(1)
                        chunk['body'].append(int.from_bytes(b, 'big'))
                    elif b == b'\x51':
                        chunk['meta'].append(int.from_bytes(b, 'big'))
                        bs = midi.read(1)
                        chunk['meta'] += [b for b in bs]
                        bs = midi.read(3)
                        chunk['body'] += [b for b in bs]
                    elif b == b'\x58':
                        chunk['meta'].append(int.from_bytes(b, 'big'))
                        bs = midi.read(1)
                        chunk['meta'] += [b for b in bs]
                        bs = midi.read(4)
                        chunk['body'] += [b for b in bs]
                    elif b == b'\x2F':
                        chunk['meta'].append(int.from_bytes(b, 'big'))
                        bs = midi.read(1)
                        chunk['meta'] += [b for b in bs]
                    elif b == b'\x59':
                        chunk['meta'].append(int.from_bytes(b, 'big'))
                        bs = midi.read(3)
                        chunk['meta'] += [b for b in bs]
                    elif b == b'\x54':
                        chunk['meta'].append(int.from_bytes(b, 'big'))
                        bs = midi.read(1)
                        chunk['meta'].append(int.from_bytes(b, 'big'))
                        bs = midi.read(5)
                        chunk['meta'] += [b for b in bs]
                    else:
                        print('不明なメタデータ')
                        print(f'データ:{b.hex()}')
                        print(f'アドレス:{hex(midi.tell())}')
                elif b in (b'\xF0', b'\xF8\7'):
                    lastEvent = b
                    SRR = False
                    chunk['status'].append(int.from_bytes(b, 'big'))
                    bs = b'\xFF'
                    maxP = 0
                    while bytes([bs[0] & 0x80]) == b'\x80':
                        bs = midi.read(1)
                        chunk['length'] += [b for b in bs]
                        maxP += [bs[0] & 0x7F][0]
                    nowP = midi.tell()
                    while (midi.tell() - nowP) < maxP:
                        bs = midi.read(1)
                        chunk['body'] += [b for b in bs]
                elif int(b2a_hex(b), 16) >= int('E0', 16):
                    lastEvent = b
                    SRR = False
                    chunk['status'].append(int.from_bytes(b, 'big'))
                    bs = midi.read(2)
                    chunk['body'] += [b for b in bs]
                elif int(b2a_hex(b), 16) >= int('C0', 16):
                    lastEvent = b
                    SRR = False
                    chunk['status'].append(int.from_bytes(b, 'big'))
                    bs = midi.read(1)
                    chunk['body'] += [b for b in bs]
                elif int(b2a_hex(b), 16) >= int('80', 16):
                    lastEvent = b
                    SRR = False
                    chunk['status'].append(int.from_bytes(b, 'big'))
                    bs = midi.read(2)
                    chunk['body'] += [b for b in bs]
                else:
                    print('不明なイベントデータ')
                    print(f'データ:{b.hex()}')
                    print(f'アドレス:{hex(midi.tell())}')
                    print('ステータス・ランニング・ルールを適用')
                    print(f'ラストイベント：{lastEvent}')
                    b = lastEvent
                    SRR = True
                if not SRR:
                    track['chunks'].append(chunk)
                    chunk = {'delta': [], 'status': [], 'meta': [], 'length': [], 'body': []}

            data['tracks'].append(track)
            track = {'header': [], 'chunks': []}

        print(midi.tell())
        print(data)
        print(len(data['tracks']))
        for i in data['tracks']:
            code = ''
            for j in i['chunks']:
                if len(j['meta']) == 0:
                    if format(j['status'][0], 'x')[0] in ('8', '9', 'C', 'B'):
                        code = ''.join(list(map(lambda X: format(X, '02x'), j['delta']))) + '_' + format(j['status'][0],
                                                                                                         'x') + '_' + ''.join(
                            list(map(lambda X: format(X, '02x'), j['body'])))
                    file = open('code.txt', 'a', encoding='utf-8').write(code + ' ')
        return data


if __name__ == "__main__":
    midiList = glob.glob(r'MIDI/*.mid')
    for mid in midiList:
        read_midi(mid)
