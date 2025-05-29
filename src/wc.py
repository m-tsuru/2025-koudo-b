from wordcloud import WordCloud
import matplotlib.pyplot as plt

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

for lang in langs:
    with open(f'data/{lang}.txt', 'r', encoding='utf-8') as file:
        text = file.read()

    # ワードクラウド生成
    wc = WordCloud(font_path=None, width=800, height=400, background_color="white").generate(text)

    # 表示
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")  # 軸を非表示にする
    plt.title(f"{lang.capitalize()} Language Word Cloud")
    plt.savefig(f"result_3-{langs.index(lang)+1}.png")
