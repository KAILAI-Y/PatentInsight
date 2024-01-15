from django.db.models import Count
from django.db import models
from django.conf import settings
from collections import defaultdict
from django.shortcuts import render
from wordcloud import WordCloud
from heapq import nlargest
from io import BytesIO
import base64
import os

from ..models import Patent, UserSearch


def search(query):
    if query:
        return Patent.objects.filter(title__icontains=query)
    else:
        return Patent.objects.none()


def year_distribution(request):
    query = request.GET.get("q", "")
    patents = search(query)

    year_distribution = (
        patents.values("year").annotate(count=models.Count("id")).order_by("year")
    )

    years = [item["year"] for item in year_distribution]
    counts = [item["count"] for item in year_distribution]

    most_patents_year = max(year_distribution, key=lambda x: x["count"])["year"]
    least_patents_year = min(year_distribution, key=lambda x: x["count"])["year"]

    context = {
        "years": years,
        "counts": counts,
        "most_patents_year": most_patents_year,
        "least_patents_year": least_patents_year,
    }
    return render(request, "distribution.html", context)


def province_innovation(request):
    query = request.GET.get("q", "")
    patents = search(query)

    province_counts = (
        patents.values("province").annotate(count=Count("id")).order_by("-count")[:10]
    )
    print(province_counts)

    provinces = [item["province"] for item in province_counts]
    province_count = [item["count"] for item in province_counts]

    context = {
        "provinces": provinces,
        "province_count": province_count,
        # "baidu_map_ak": settings.BAIDU_MAP_AK,
    }
    return render(request, "innovation.html", context)


def network_view(request):
    query = request.GET.get("q", "")
    patents = search(query)

    nodes = set()
    links = defaultdict(int)

    for patent in patents:
        entities = patent.apos.split(";")
        for entity in entities:
            nodes.add(entity)
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                links[(entities[i], entities[j])] += 1

    nodes_data = [{"name": node} for node in nodes]
    links_data = [
        {"source": source, "target": target, "value": links[(source, target)]}
        for source, target in links
    ]

    return render(
        request,
        "network.html",
        {
            "nodes_data": nodes_data,
            "links_data": links_data,
        },
    )


# extract keywords using jieba
# def extract_keywords_from_patent(patent, topK=5):
#     text = patent.title + " " + patent.abstract

#     stopwords_path = os.path.join(
#         settings.BASE_DIR, "patent_api", "static", "baidu_stopwords.txt"
#     )

#     # 设置结巴分词的停用词
#     jieba.analyse.set_stop_words(stopwords_path)

#     # 进行分词和词性标注
#     words = pseg.cut(text)

#     # 提取名词
#     nouns = [
#         word
#         for word, flag in words
#         if flag.startswith("n") and word not in stopwords_path
#     ]

#     combined_nouns = " ".join(nouns)

#     keywords = jieba.analyse.textrank(combined_nouns, topK=topK, withWeight=False)
#     # print(keywords)

#     return keywords


##################################
# fetch featurewords from models
def generate_wordcloud_from_keywords(keywords_list, font_path):
    # 将关键词列表合并为一个字符串
    combined_keywords = " ".join(keywords_list)

    # 创建词云对象
    wc = WordCloud(
        font_path=font_path,
        width=800,
        height=400,
        background_color="white",
    )

    # 生成词云
    wc.generate(combined_keywords)

    # 将词云图像转换为 Base64 编码
    img = wc.to_image()
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return image_base64


def get_top_keywords(patents, topK=100):
    # 创建一个字典来存储所有关键词和它们的总权重
    keyword_weights = {}

    # 遍历所有专利，累加权重
    for patent in patents:
        featurewords = patent.featurewords.split(";")
        probs = [float(p) for p in patent.probs.split(";")]

        for word, weight in zip(featurewords, probs):
            if word not in keyword_weights:
                keyword_weights[word] = weight
            else:
                keyword_weights[word] += weight

    # 获取权重最高的topK个关键词
    top_keywords = nlargest(topK, keyword_weights, key=keyword_weights.get)
    # 返回这些关键词及其权重
    return {word: keyword_weights[word] for word in top_keywords}


def generate_wordcloud_view(request):
    query = request.GET.get("q", "")
    patents = search(query)
    user = request.user

    user_search, created = UserSearch.objects.get_or_create(
        user=user, search_word=query
    )

    if user_search and user_search.wordcloud_base64:
        wordcloud_image_base64 = user_search.wordcloud_base64
    else:
        if patents.exists():
            top_keywords = get_top_keywords(patents, 100)

            # 获取字体路径
            font_path = os.path.join(
                settings.BASE_DIR, "patent_api", "static", "font", "SimSun.ttf"
            )

            # 生成词云图像的 Base64 编码
            wordcloud_image_base64 = generate_wordcloud_from_keywords(
                top_keywords, font_path
            )
        else:
            wordcloud_image_base64 = None

    user_search.wordcloud_base64 = wordcloud_image_base64
    user_search.save()

    return render(
        request,
        "wordcloud.html",
        {
            "wordcloud_image_base64": wordcloud_image_base64,
        },
    )
