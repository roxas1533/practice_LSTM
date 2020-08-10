from read_midi import *


def write_midi(path):
    with open(path, 'wb') as midi:
        midi.write(b"\x4D\x54\x68\x64\x00\x00\x00\x06\x00\x01\x00\x02\x00\xF0")
        data = read_midi(path='MIDI/minuet_bach.mid')['tracks'][0]
        midi.write(bytearray(data['header']))
        for chunk in data['chunks']:
            for c in chunk.values():
                midi.write(bytearray(c))

        with open('AI_MUSIC_58.txt', 'r') as code:
            co = code.read().split(' ')[:-1]
            length = 0
            for l in co:
                length += int((len(l) - 2) / 2)
            data['header'][4:] = int.to_bytes(length + 4, 4, 'big')
            midi.write(bytearray(data['header']))
            for one in co:
                bs = one.split('_')
                midi.write(int(bs[0], 16).to_bytes(int(len(bs[0]) / 2), byteorder='big'))
                midi.write(int(bs[1], 16).to_bytes(1, byteorder='big'))
                midi.write(int(bs[2], 16).to_bytes(2, byteorder='big'))
            midi.write(b'\x00\xFF\x2F\x00')


write_midi('AIMUSIC.mid')
