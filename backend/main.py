from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv, glob, MeCab, requests
from tqdm import tqdm
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import sys
import base64

import matplotlib

"""
その年で話題になったもの
国会議員別のwordcloud
発言テーマ別の発言回数が多かった議員を出力
"""

app = FastAPI()

matplotlib.rc_file('matplotlibrc')  
plt.rcParams['font.family'] = 'IPAexGothic'
matplotlib.use('TkAgg')

class NameInput(BaseModel):
    name: str

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_stopwords():
    url = "http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt"
    r = requests.get(url)
    stopwords = r.text.split('\r\n')
    with open("./stopwords.txt", "r") as f:
        self_stopwords = f.read().split("\n")
    stopwords = stopwords + self_stopwords
    stopwords = [word for word in stopwords if len(word) > 0]
    return stopwords

def get_noun_frequencies(text_list, stopwords):
    tagger = MeCab.Tagger()
    nouns = []
    for text in text_list:
        node = tagger.parseToNode(text)
        while node:
            if node.feature.split(',')[0] == '名詞' and node.surface not in stopwords:
                noun = node.surface
                if len(noun) > 1:
                    nouns.append(noun)
            node = node.next
    noun_freq = Counter(nouns)
    return noun_freq

def visualize_frequent_nouns(name, text_list):
    stopwords = get_stopwords()
    noun_freq = get_noun_frequencies(text_list, stopwords)
    top_nouns = noun_freq.most_common(100)
    word_freq = dict(top_nouns)

    wordcloud = WordCloud(width=800, 
                        height=400, 
                        background_color='white', 
                        font_path="/Library/Fonts/ipaexg.ttf").generate_from_frequencies(word_freq)

    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'{name}の口癖の出現頻度')
    plt.tight_layout()
    
    # ワードクラウド画像をBase64エンコードして取得
    image_base64 = get_wordcloud_base64(wordcloud)
    
    return image_base64

def get_wordcloud_base64(wordcloud):
    # ワードクラウド画像を一時的に保存
    temp_path = "/Users/shintaro/vscode/word-cloud-project/pictures/result.jpg"
    wordcloud.to_file(temp_path)
    
    # ファイルをBase64エンコード
    with open(temp_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    
    return encoded_image

def wc_execution(name):
    sentences = []    
    files_path = glob.glob('/Users/shintaro/vscode/word-cloud-project/preprocessing/csv_data/*/*.csv', recursive=True)
    for file in tqdm(files_path, desc="検索中..."):
        with open(file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            for row in rows:
                if row[3] == name:
                    sentences.append(row[8])

    return visualize_frequent_nouns(name, sentences)

@app.get("/")
def Hello():
    return {"message":"Hello World!"}

@app.post("/")
def hello_name(name_input: NameInput):
    name:str = name_input.name
    cloud_jpg = wc_execution(name)
    return {"image_data": cloud_jpg}


# python3 -m uvicorn main:app