import os
import glob # 使われていないが、もし将来使う可能性があれば残しても良い
import numpy as np
from sklearn.manifold import TSNE
from collections import Counter
from gensim.models import Word2Vec
from sklearn.feature_extraction import text
import re

import matplotlib.pyplot as plt

# テキストファイルがあるディレクトリ
TEXT_DIR = './data'  # 適宜変更
langs = [
    'python',
    'TypeScript',
    'javascript',
    'java',
    'c++',
    'c#',
    'php',
    'shell',
    'C',
    'go'
]

# テキストファイルの読み込み
def load_texts(text_dir):
    texts = {}
    for lang in langs:
        file_path = os.path.join(text_dir, f"{lang}.txt") # os.path.join を使用してパスを構築
        if os.path.exists(file_path): # ファイルの存在を確認
            with open(file_path, encoding='utf-8') as f:
                texts[lang] = f.read()
        else:
            print(f"Warning: File not found for language '{lang}' at {file_path}. Skipping.")
    return texts

# 簡易的な単語分割（日本語の場合はMeCab等を推奨）
def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

# 各ファイルの頻出単語を取得
def get_top_words(texts, top_n=30):
    stop_words = set(text.ENGLISH_STOP_WORDS)  # 英語のストップワード
    top_words = {}
    for fname, text_content in texts.items(): # 変数名を修正
        words = tokenize(text_content)
        # ストップワード除去
        words = [w for w in words if w not in stop_words]
        freq = Counter(words)
        common = [w for w, _ in freq.most_common(top_n)]
        top_words[fname] = common
    return top_words

# Word2Vecモデルの学習
def train_word2vec(texts):
    sentences = [tokenize(text) for text in texts.values()]
    # sentencesが空の場合のハンドリング
    if not sentences:
        print("Warning: No sentences to train Word2Vec model.")
        return None
    model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=2, seed=42)
    return model

# t-SNEで可視化
def plot_tsne(top_words, model):
    if model is None: # モデルが学習できなかった場合のハンドリング
        print("Error: Word2Vec model is not trained. Cannot plot t-SNE.")
        return

    plt.figure(figsize=(10, 10)) # 図のサイズを少し大きく
    colors = [
            'blue',
            'orange',
            'green',
            'red',
            'purple',
            'brown',
            'pink',
            'gray',
            'cyan',
            'magenta'
        ]
    for idx, (fname, words) in enumerate(top_words.items()):
        vectors = []
        labels = []
        for word in words:
            if word in model.wv:
                vectors.append(model.wv[word])
                labels.append(word)
        if not vectors:
            continue
        # perplexityはn_samples未満である必要がある
        # len(vectors) >= 2 であることは保証されている
        perplexity = min(30, len(vectors) - 1)
        tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity, init='random', learning_rate='auto') # initとlearning_rateを追加 (TSNEの警告対策)
        reduced = tsne.fit_transform(np.array(vectors))

        plt.scatter(reduced[:,0], reduced[:,1], label=fname, alpha=0.7, color=colors[idx % len(colors)])
        for i, label in enumerate(labels):
            plt.annotate(label, (reduced[i,0], reduced[i,1]), fontsize=8)

    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left') # 凡例がグラフと重ならないように調整
    plt.title('t-SNE of Top Words per File')
    plt.grid(True) # グリッドを追加
    plt.tight_layout(rect=[0, 0, 0.85, 1]) # 凡例のためにスペースを確保
    plt.xlim(-30, 30)
    plt.ylim(-30, 30)
    plt.savefig('4-2.png')
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    plt.savefig('4-3.png') # 軸の制限を適用した図を保存
    plt.show() # 図を表示 (必要であれば)

def main():
    # データディレクトリが存在しない場合は作成
    if not os.path.exists(TEXT_DIR):
        print(f"Error: Directory '{TEXT_DIR}' not found. Please create it and place your language .txt files there.")
        return

    texts = load_texts(TEXT_DIR)
    if not texts: # テキストが読み込まれなかった場合のハンドリング
        print("No texts loaded. Exiting.")
        return

    top_words = get_top_words(texts, top_n=100)
    model = train_word2vec(texts)
    plot_tsne(top_words, model)

if __name__ == '__main__':
    main()
