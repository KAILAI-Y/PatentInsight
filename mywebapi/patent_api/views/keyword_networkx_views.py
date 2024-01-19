from matplotlib import pyplot as plt
from django.http import JsonResponse
from django.shortcuts import render
from collections import defaultdict
from itertools import combinations
from networkx import community
from io import BytesIO
from re import search
import networkx as nx
import matplotlib
import base64
import heapq

from ..models import Patent, UserSearch


def search(query):
    if query:
        return Patent.objects.filter(title__icontains=query)
    else:
        return Patent.objects.none()


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

    user = request.user

    user_search, created = UserSearch.objects.get_or_create(
        user=user, search_word=query
    )

    if user_search and user_search.word_network_base64:
        img_base64 = user_search.word_network_base64
    else:
        img_base64 = keyword_network(patents)

        if not img_base64.startswith("data:image/png;base64,"):
            img_base64 = "data:image/png;base64," + img_base64

    user_search.word_network_base64 = img_base64
    user_search.save()

    return render(request, "word_network.html", {"img_base64": img_base64})
