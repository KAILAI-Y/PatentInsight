from heapq import nlargest
import heapq
import os
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Count
from django.db import models
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from collections import defaultdict
from io import BytesIO
import base64
from base64 import b64decode
from wordcloud import WordCloud
import jieba.analyse
import jieba.posseg as pseg
from itertools import combinations
import networkx as nx
from networkx import community
import matplotlib
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import csv
import json
from openai import OpenAI
from .models import Patent
from .models import UserSearch

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def index(request):
    return render(request, "index.html")


def search(query):
    temp_user_id = "001"
    if query:
        # generate_all_data_for_query(query)
        return Patent.objects.filter(title__icontains=query)
    else:
        return Patent.objects.none()


def patent_list(request):
    query = request.GET.get("q", "")
    patents = search(query)

    paginator = Paginator(patents, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "result.html",
        {
            "page_obj": page_obj,
            "total_count": paginator.count,
        },
    )


def download_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="patents.csv"'
    response.write("\ufeff".encode("utf8"))

    writer = csv.writer(response)
    writer.writerow(["Title", "Year", "Abstract"])

    query = request.GET.get("q", "")
    patents = search(query)

    for patent in patents:
        writer.writerow([patent.title, patent.year, patent.abstract])

    return response


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


def generate_pdf(request):
    pdfmetrics.registerFont(TTFont("SimSun", "SimSun.ttf"))
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            text = data.get("text", "")

            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="report.pdf"'

            buffer = BytesIO()
            p = canvas.Canvas(buffer)

            image_height = 300
            y_position = 750

            for chart in data.get("charts", []):
                title = chart.get("title", "")
                chart_image = b64decode(chart["imageData"].split(",")[1])
                chart_image_stream = BytesIO(chart_image)
                chart_image_stream.seek(0)

                if y_position < 300:
                    p.showPage()
                    y_position = 750

                p.setFont("SimSun", 12)
                p.drawString(50, y_position, title)
                y_position -= 20

                y_position -= image_height

                p.drawImage(
                    ImageReader(chart_image_stream),
                    50,
                    y_position,
                    width=400,
                    height=image_height,
                )

            p.showPage()
            p.setFont("SimSun", 14)
            y_position = 750
            p.drawString(50, y_position, "结论")
            y_position -= 20
            p.setFont("SimSun", 12)
            p.drawString(50, y_position, text)
            p.save()
            buffer.seek(0)
            response.write(buffer.getvalue())
            buffer.close()

            return response
        except Exception as e:
            return HttpResponse(f"Error generating PDF: {e}", status=500)

    return HttpResponse("Invalid request", status=400)


@csrf_exempt
@require_http_methods(["POST"])
def gpt_request(request):
    try:
        # 解析请求体中的数据
        data = json.loads(request.body)
        base64_images = data.get("base64_images", [])
        text = data.get("text")

        # 构建用于 GPT-4 视觉模型的消息
        messages = [{"type": "text", "text": text}]
        messages.extend(
            [
                {"type": "image_url", "image_url": {"url": base64_image}}
                for base64_image in base64_images
            ]
        )

        # 调用 OpenAI GPT-4 视觉模型
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": messages,
                }
            ],
            max_tokens=300,
        )

        # 提取并返回响应数据
        generated_text = response.choices[0].message.content
        last_period_index = generated_text.rfind("。")
        if last_period_index != -1:
            generated_text = generated_text[: last_period_index + 1]
        return JsonResponse({"response": generated_text})

    except json.JSONDecodeError as e:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


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

    return render(
        request, "wordcloud.html", {"wordcloud_image_base64": wordcloud_image_base64}
    )


def calculate_cooccurrence(featurewords_list):
    cooccurrence_counts = defaultdict(int)
    for featurewords in featurewords_list:
        words = featurewords.split(";")
        # Count co-occurrences
        for word1, word2 in combinations(set(words), 2):
            cooccurrence_counts[(word1, word2)] += 1
            cooccurrence_counts[(word2, word1)] += 1
    return cooccurrence_counts


def create_network_graph(cooccurrence_counts):
    # 创建一个空的无向图
    G = nx.Graph()

    # 遍历共现关系字典，添加边到图中
    for (word1, word2), weight in cooccurrence_counts.items():
        # 添加边，其中word1和word2是节点，weight是共现次数或权重
        G.add_edge(word1, word2, weight=weight)

    return G


def detect_communities(G):
    communities = community.girvan_newman(G)
    top_level_communities = next(communities)
    return sorted(map(sorted, top_level_communities))


matplotlib.use("Agg")
plt.rcParams["font.sans-serif"] = ["SimSun"]


# function to create node colour list
def create_community_node_colors(graph, communities):
    print(len(communities))
    number_of_colors = len(communities[0])
    colors = ["#D4FCB1", "#CDC5FC", "#FFC2C4", "#F2D140", "#BCC6C8"][:number_of_colors]
    node_colors = []
    for node in graph:
        current_community_index = 0
        # for community in communities:
        for i, community in enumerate(communities):
            if node in community:
                # node_colors.append(colors[current_community_index])
                node_colors.append(colors[i % len(colors)])
                break
            current_community_index += 1
    return node_colors


# def create_community_node_colors(graph, communities):
#     # 定义一个足够大的颜色列表或循环使用的颜色
#     colors = [
#         "#D4FCB1",
#         "#CDC5FC",
#         "#FFC2C4",
#         "#F2D140",
#         "#BCC6C8",
#         "#1f78b4",
#         "#b2df8a",
#         "#33a02c",
#         "#fb9a99",
#         "#e31a1c",
#         "#fdbf6f",
#         "#ff7f00",
#         "#cab2d6",
#         "#6a3d9a",
#         "#ffff99",
#         "#b15928",
#     ]

#     # 创建一个字典来映射每个节点到它的社区编号
#     community_map = {}
#     for idx, community in enumerate(communities):
#         for node in community:
#             community_map[node] = idx % len(colors)  # 使用取余数来循环颜色

#     # 为每个节点分配颜色
#     node_colors = [colors[community_map[node]] for node in graph]
#     return node_colors


# function to plot graph with node colouring based on communities
def visualize_communities(graph, communities):
    node_colors = create_community_node_colors(graph, communities)
    modularity = round(nx.community.modularity(graph, communities), 6)
    title = f"Community Visualization of {len(communities)} communities with modularity of {modularity}"
    pos = nx.spring_layout(graph, k=0.8, iterations=100)

    plt.title(title)
    nx.draw(
        graph,
        pos=pos,
        node_size=2000,
        node_color=node_colors,
        with_labels=True,
        font_size=16,
        font_color="black",
        font_family="SimSun",
    )


def limit_cooccurrences(cooccurrence, max_connections=5):
    # 创建一个新的字典来存储限制后的共现关系
    limited_cooccurrence = defaultdict(dict)

    # 为每个词收集共现对
    for (word1, word2), weight in cooccurrence.items():
        limited_cooccurrence[word1][word2] = weight

    # 限制每个词的共现对数量
    for word, connections in limited_cooccurrence.items():
        # 如果共现对的数量超过最大限制，则只保留权重最高的几个
        if len(connections) > max_connections:
            top_connections = heapq.nlargest(
                max_connections, connections.items(), key=lambda x: x[1]
            )
            limited_cooccurrence[word] = dict(top_connections)

    # 转换回原始格式
    final_cooccurrence = {}
    for word1, connections in limited_cooccurrence.items():
        for word2, weight in connections.items():
            final_cooccurrence[(word1, word2)] = weight

    return final_cooccurrence


def keyword_network(patents):
    if not patents:
        return JsonResponse({"error": "No patents found"})
    else:
        # all_keywords = [extract_keywords_from_patent(patent) for patent in patents]
        all_featurewords = [patent.featurewords for patent in patents]

        cooccurrence = calculate_cooccurrence(all_featurewords)
        sorted_cooccurrences = sorted(
            cooccurrence.items(), key=lambda item: item[1], reverse=True
        )
        # top_cooccurrences = dict(sorted_cooccurrences[:2000])
        top_cooccurrences = limit_cooccurrences(
            dict(sorted_cooccurrences[:2000]), max_connections=5
        )

        print(len(top_cooccurrences))
        G = create_network_graph(top_cooccurrences)

        communities = detect_communities(G)

        plt.figure(figsize=(30, 15))

        # 绘制网络图并保存
        visualize_communities(G, communities)
        img_data = BytesIO()
        plt.savefig(img_data, format="png")
        plt.close()
        img_data.seek(0)
        img_base64 = base64.b64encode(img_data.read()).decode("utf-8")

        return img_base64


def word_network_view(request):
    query = request.GET.get("q", "")
    patents = search(query)

    img_base64 = keyword_network(patents)

    return render(request, "word_network.html", {"img_base64": img_base64})
