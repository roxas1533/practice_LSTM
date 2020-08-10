from __future__ import print_function

from janome.tokenizer import Tokenizer
from keras.callbacks import LambdaCallback
from keras.models import Sequential
from keras.layers import Dense, Activation, CuDNNLSTM
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import matplotlib.pyplot as plt  # 追加
import numpy as np
import random
import sys
import io
import tensorflow as tf

config = tf.compat.v1.ConfigProto(gpu_options=
                                  tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.8)
                                  # device_count = {'GPU': 1}
                                  )
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(session)
path = './code.txt'
with io.open(path, encoding='utf-8') as f:
    text = f.read().lower()

# text = Tokenizer().tokenize(text, wakati=True)  # 分かち書きする
text = text.split(' ')[:-1]

chars = text
count = 0
char_indices = {}  # 辞書初期化
indices_char = {}  # 逆引き辞書初期化

for word in chars:
    if not word in char_indices:  # 未登録なら
        char_indices[word] = count  # 登録する
        count += 1
        print(count, word)  # 登録した単語を表示
# 逆引き辞書を辞書から作成する
indices_char = dict([(value, key) for (key, value) in char_indices.items()])

# cut the text in semi-redundant sequences of maxlen characters
maxlen = 4
step = 1
sentences = []
next_chars = []
for i in range(0, len(text) - maxlen, step):
    sentences.append(text[i: i + maxlen])
    next_chars.append(text[i + maxlen])
print('nb sequences:', len(sentences))
print('Vectorization...')
x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        x[i, t, char_indices[char]] = 1
    y[i, char_indices[next_chars[i]]] = 1

model = Sequential()
model.add(LSTM(128, input_shape=(maxlen, len(chars))))
model.add(Dense(len(chars)))
model.add(Activation('softmax'))

optimizer = RMSprop(lr=0.01)
model.compile(loss='categorical_crossentropy', optimizer=optimizer)


def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


def on_epoch_end(epoch, logs):
    # Function invoked at end of each epoch. Prints generated text.
    print()
    print('----- Generating text after Epoch: %d' % epoch)

    start_index = random.randint(0, len(text) - maxlen - 1)
    for diversity in [0.2]:  # diversity = 0.2 のみとする
        print('----- diversity:', diversity)

        generated = ''
        sentence = text[start_index: start_index + maxlen]
        generated += " ".join(sentence)
        print(sentence)
        print('----- Generating with seed: "' + " ".join(sentence) + '"')

        if epoch in (1, 58):
            for i in range(400):
                x_pred = np.zeros((1, maxlen, len(chars)))
                for t, char in enumerate(sentence):
                    x_pred[0, t, char_indices[char]] = 1.

                preds = model.predict(x_pred, verbose=0)[0]
                next_index = sample(preds, diversity)
                next_char = indices_char[next_index]

                generated += next_char
                sentence = sentence[1:]
                # sentence はリストなので append で結合する
                sentence.append(next_char)
                file = open(f'AI_MUSIC_{epoch}.txt', 'a', encoding='utf-8').write(next_char + ' ')  # UTF-8に変換
                sys.stdout.write(next_char + ' ')
                sys.stdout.flush()
            print()


print_callback = LambdaCallback(on_epoch_end=on_epoch_end)

history = model.fit(x, y,
                    batch_size=128,
                    epochs=60,
                    callbacks=[print_callback])

# Plot Training loss & Validation Loss
loss = history.history["loss"]
epochs = range(1, len(loss) + 1)
plt.plot(epochs, loss, "bo", label="Training loss")
plt.title("Training loss")
plt.legend()
plt.savefig("loss.png")
plt.close()
