from read_midi import *


def write_midi(path):
    with open(path, 'wb') as midi:
        midi.write(b"\x4D\x54\x68\x64\x00\x00\x00\x06\x00\x01\x00\x02\x00\xF0")
        data = read_midi(path='MIDI/minuet_bach.mid')['tracks'][0]
        midi.write(bytearray(data['header']))
        for chunk in data['chunks']:
            for c in chunk.values():
                midi.write(bytearray(c))
        midi.write(bytearray(data['header']))
        with open('AI_MUSIC_58.txt', 'r') as code:
            co = code.read().split(' ')[:-1]
            length = len(co) * 8
            midi.write(int.to_bytes(length + 6, 4, 'big'))
            for one in co:
                bs = one.split('_')
                midi.write(int(bs[0], 16).to_bytes(2, byteorder='big'))
                midi.write(int(bs[1], 16).to_bytes(1, byteorder='big'))
                midi.write(int(bs[2], 16).to_bytes(4, byteorder='big'))
            midi.write(b'\xFF\x2F\x00')


write_midi('AIMUSIC.mid')
