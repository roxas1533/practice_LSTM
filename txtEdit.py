import sys
import re
import io

path = 'henshin.txt'
bindata = open(path, "rb")
lines = bindata.readlines()
for line in lines:
    text = line.decode('Shift_JIS')  # Shift_JISで読み込み
    text = re.split(r'\r', text)[0]  # 改行削除
    text = text.replace('｜', '')  # ルビ前記号削除
    text = re.sub(r'《.+?》', '', text)  # ルビ削除
    text = re.sub(r'［＃.+?］', '', text)  # 入力者注削除
    print(text)
    file = open('data_rojinto_umi.txt', 'a', encoding='utf-8').write(text)  # UTF-8に変換
