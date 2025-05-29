import sys
from sklearn.feature_extraction.text import TfidfVectorizer
import string
from sklearn.feature_extraction import text

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

# 英語のストップワードと記号を除外
stop_words = text.ENGLISH_STOP_WORDS.union(set(string.punctuation))

# TfidfVectorizerでストップワードを指定
def load_text(filename):
    with open(filename, encoding='utf-8') as f:
        return f.read()

def main():
    for lang in langs:
        print(f"Language: {lang}")
        documents = [load_text(f"data/{lang}.txt")]

        vectorizer = TfidfVectorizer(stop_words=list(stop_words))
        tfidf_matrix = vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]

        # 単語とスコアをペアにしてソート
        word_scores = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)

        print("上位の単語:")
        for word, score in word_scores[:10]:
            print(f"{word:12}: {score:.4f}")

        print()

if __name__ == "__main__":
    main()
