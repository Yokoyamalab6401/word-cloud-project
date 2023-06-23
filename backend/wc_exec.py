import csv, glob, MeCab, requests
from tqdm import tqdm
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# matplotlibで日本語を使えるように
import matplotlib
matplotlib.rc_file('matplotlibrc')  
plt.rcParams['font.family'] = 'IPAexGothic'


"""
その年で話題になったもの
国会議員別のwordcloud
発言テーマ別の発言回数が多かった議員を出力


"""


def get_stopwords():
    url = "http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt"
    r = requests.get(url)
    stopwords = r.text.split('\r\n')
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


def visualize_frequent_nouns(name, save_name, text_list):
    stopwords = get_stopwords()
    noun_freq = get_noun_frequencies(text_list, stopwords)
    top_nouns = noun_freq.most_common(100)
    word_freq = dict(top_nouns)

    wordcloud = WordCloud(width=800, 
                        height=400, 
                        background_color='white', 
                        font_path="/home/shintaro/.local/lib/python3.8/site-packages/japanize_matplotlib/fonts/ipaexg.ttf").generate_from_frequencies(word_freq)

    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'{name}の口癖の出現頻度')
    plt.tight_layout()
    plt.savefig(f"../pictures/{save_name}.jpg")


def wc_execution(name, save_name):
    sentences = []    
    files_path = glob.glob('/Users/shintaro/vscode/word-cloud-project/preproccesing/csv_data/202*_data/*.csv', recursive=True)
    for file in tqdm(files_path, desc="検索中..."):
        with open(file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            for row in rows:
                if row[3] == name:
                    sentences.append(row[8])

    visualize_frequent_nouns(name, save_name, sentences)

if __name__ == "__main__":
    name  = input("気になる国会議員の名前を入力してください: ")
    save_name = input("保存名は: ")

    wc_execution(name, save_name)
