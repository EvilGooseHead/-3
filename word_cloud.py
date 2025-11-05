import pandas as pd  # 导入pandas库用于数据处理
from sklearn.feature_extraction.text import TfidfVectorizer  # 导入TfidfVectorizer用于计算TF-IDF值
import numpy as np  # 导入numpy库用于数值运算
from wordcloud import WordCloud, ImageColorGenerator  # 导入WordCloud用于生成词云
import matplotlib.pyplot as plt  # 导入matplotlib.pyplot用于绘图
import os  # 导入os库用于读取、处理电脑上的文件
from PIL import Image, ImageDraw, ImageFont  # 导入PIL库中的模块用于图像处理
import jieba  # 导入jieba库用于中文分词
from matplotlib import colors #用于自定义词云图的美术

output_dir = 'wordcloud_images1'  # 定义输出目录路径（最后把图片保存在一个文件夹里）
os.makedirs(output_dir, exist_ok=True)  # 创建输出目录，如果目录已存在则忽略
input_file = 'douban_reviews1.xlsx'  # 定义输入文件路径（后续读取爬取整理好的评论）
df = pd.read_excel(input_file) #（使用pandas包的pd函数读取EXCEL，并将其赋给变量df）

df.drop_duplicates(subset=['title', 'comment'], inplace=True)  # 去除df中重复的评论（豆瓣一般不会出现）
df.to_excel('test1.xlsx', index=False) #（将处理好的df保存在excel中）

with open('cn_stopwords.txt', 'r', encoding='utf-8') as f:
    stopwords = set(f.read().splitlines())  # 读取停用词并存入集合 （定义停用词，把一些无实际含义的词屏蔽掉）

# 接下来是定义分词函数
def tokenize(text):
    jieba.load_userdict("user_dict.txt") # 导入适用于《南京照相馆》评论的一些专有名词
    words = jieba.lcut(text, cut_all= True)  # 使用jieba进行分词
    filtered_words = [word for word in words if word not in stopwords]  # 去除停用词
    return ' '.join(filtered_words)  # 将结果用空格连接

# 对评论进行分词处理
df['comment_tokenized'] = df['comment'].apply(tokenize)  # 应用分词函数到每一行评论；我储存评论的的变量叫做“comment”

# 过滤掉空字符串的行
df = df[df['comment_tokenized'] != '']

# 定义TF-IDP方法计算每个词的权重的函数
def compute_tfidf(data_chunk):
    vectorizer = TfidfVectorizer(max_features=500)  # 初始化TfidfVectorizer对象，最大特征数为500
    tfidf_matrix = vectorizer.fit_transform(data_chunk)  # 计算TF-IDF矩阵
    feature_names = vectorizer.get_feature_names_out()  # 获取特征名称（即词汇）
    sum_tfidf_scores = np.asarray(tfidf_matrix.sum(axis=0)).flatten()  # 计算每个词汇的TF-IDF得分总和
    print("TF-IDF特征示例:")
    print(feature_names[:100])
    return feature_names, sum_tfidf_scores  # 返回词汇及其对应的TF-IDF得分总和
# 直接对整个数据集进行TF-IDF计算
feature_names, sum_tfidf_scores = compute_tfidf(df['comment_tokenized'])
feature_df = pd.DataFrame({'Word': feature_names, 'TF-IDF Score': sum_tfidf_scores})  # 创建包含词汇和TF-IDF得分的数据框（第一列是词汇，第二列是TF-IDF得分）
feature_df = feature_df.sort_values(by='TF-IDF Score', ascending=False).reset_index(drop=True)  # 按TF-IDF得分降序排序
top_300_features = feature_df.head(200)  # 获取前300个重要词汇
word_freq_dict = dict(zip(top_300_features['Word'], top_300_features['TF-IDF Score']))  # 创建词汇和TF-IDF得分的字典

#定义颜色
nanjing_colors = [
    '#2F4F4F',  # 深石板灰
    '#121212',  # 炭黑
    '#5C4033',  # 深棕
    '#545454',  # 工业灰
    '#6E7B8B'   # 雾岩灰
]
colormap = colors.ListedColormap(nanjing_colors)# 调用颜色

#定义生成并保存词云图的函数
def generate_wordcloud(word_freq_dict, font_path=None, filename="overall_wordcloud.png"):
    if font_path is None:
        try:
            font_path = 'simhei.ttf'  # 设置字体路径
            ImageFont.truetype(font_path)  # 检查字体是否存在
        except IOError:
            print("不存在 simhei.ttf 字体")  # 如果找不到字体，则打印提示信息
            font_path = None
    wordcloud = WordCloud(
        font_path='msyhbd.ttc',
        width=1500,  # 增加宽度（像素）
        height=1000,  # 增加高度（像素）
        background_color='white',
        colormap=colormap,
        contour_width=3,
        contour_color='steelblue',
        margin=10,  # 增加字间距（像素）
        prefer_horizontal=1,  # 增加水平排列比例
        max_font_size=200,  # 增大最大字体
        min_font_size=5,  # 设置最小字体
        relative_scaling=0.5,  # 调整字体大小差异
        scale=2,  # 增加缩放比例（提高分辨率）
        collocations=False  # 不显示词组搭配
    ).generate_from_frequencies(word_freq_dict)  # 根据频率生成词云
    plt.figure(figsize=(15, 10), dpi=300)  # 创建一个新的图形
    plt.imshow(wordcloud, interpolation='bilinear')  # 显示词云图像 # 设置图形标题
    plt.axis('off')  # 关闭坐标轴
    plt.savefig(os.path.join(output_dir, filename), bbox_inches='tight', dpi=300)  # 保存图像到文件
    plt.close()  # 关闭图形

generate_wordcloud(word_freq_dict, filename="overall_wordcloud_1.png")  # 使用函数生成整体评论词云