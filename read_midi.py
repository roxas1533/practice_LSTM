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
        while 1:
            if flag or bs == b'':
                break
            bs = midi.read(4)
            track['header'] = [b for b in bs]
            bs = midi.read(4)
            track['header'] += [b for b in bs]
            MaxPoint = int.from_bytes(bs, 'big')
            lastPoint = midi.tell()
            while (midi.tell() - lastPoint) < MaxPoint:
                if flag:
                    break
                b = midi.read(1)
                chunk['delta'].append(int.from_bytes(b, 'big'))
                variable(b, midi, chunk['delta'])
                b = midi.read(1)
                if b == b'\xFF':
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
                        chunk['length'].append(3)
                        bs = midi.read(3)
                        chunk['body'] += [b for b in bs]
                    elif b == b'\x58':
                        chunk['meta'].append(int.from_bytes(b, 'big'))
                        bs = midi.read(1)
                        chunk['meta'] += [b for b in bs]
                        chunk['length'].append(4)
                        bs = midi.read(4)
                        chunk['body'] += [b for b in bs]
                    elif b == b'\x2F':
                        chunk['meta'].append(int.from_bytes(b, 'big'))
                        bs = midi.read(1)
                        chunk['meta'] += [b for b in bs]
                    else:
                        print('不明なメタデータ')
                        print(b.hex())
                elif b in (b'\xF0', b'\xF8\7'):
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
                    chunk['status'].append(int.from_bytes(b, 'big'))
                    chunk['length'].append(2)
                    bs = midi.read(2)
                    chunk['body'] += [b for b in bs]
                elif int(b2a_hex(b), 16) >= int('C0', 16):
                    chunk['status'].append(int.from_bytes(b, 'big'))
                    chunk['length'].append(1)
                    bs = midi.read(1)
                    chunk['body'] += [b for b in bs]
                elif int(b2a_hex(b), 16) >= int('B0', 16):
                    chunk['status'].append(int.from_bytes(b, 'big'))
                    chunk['length'].append(2)
                    bs = midi.read(2)
                    chunk['body'] += [b for b in bs]
                elif int(b2a_hex(b), 16) >= int('80', 16):
                    chunk['status'].append(int.from_bytes(b, 'big'))
                    chunk['length'].append(2)
                    bs = midi.read(2)
                    chunk['body'] += [b for b in bs]
                else:
                    print('不明なイベントデータ')
                    flag = True
                    print(midi.tell())
                track['chunks'].append(chunk)
                chunk = {'delta': [], 'status': [], 'meta': [], 'length': [], 'body': []}

            data['tracks'].append(track)
            track = {'header': [], 'chunks': []}

        print(midi.tell())
        print(data['tracks'][1])


read_midi('minuet_bach.mid')
