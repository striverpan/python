# encoding=utf-8
import math
import sys

import os
# train为训练集合，test为验证集合，给每个用户推荐N个物品
# 召回率和准确率
import pandas


def RecallAndPrecision(self, train=None, test=None, K=3, N=10):
    train = train or self.train
    test = test or self.test
    hit = 0
    recall = 0
    precision = 0
    for user in train.keys():
        tu = test.get(user, {})
        rank = self.Recommend(user, K=K, N=N)
        for i, _ in rank.items():
            if i in tu:
                hit += 1
        recall += len(tu)
        precision += K
    recall = hit / (recall * 1.0)
    precision = hit / (precision * 1.0)
    return (recall, precision)


# 覆盖率
def Coverage(self, train=None, test=None, K=3, N=10):
    train = train or self.train
    recommend_items = set()
    all_items = set()
    for user, items in train.items():
        for i in items.keys():
            all_items.add(i)
        rank = self.Recommend(user, K)
        for i, _ in rank.items():
            recommend_items.add(i)
    return len(recommend_items) / (len(all_items) * 1.0)


# 新颖度
def Popularity(self, train=None, test=None, K=3, N=10):
    train = train or self.train
    item_popularity = dict()
    # 计算物品流行度
    for user, items in train.items():
        for i in items.keys():
            item_popularity.setdefault(i, 0)
            item_popularity[i] += 1
    ret = 0  # 新颖度结果
    n = 0  # 推荐的总个数
    for user in train.keys():
        rank = self.Recommend(user, K=K, N=N)  # 获得推荐结果
        for item, _ in rank.items():
            ret += math.log(1 + item_popularity[item])
            n += 1
    ret /= n * 1.0
    return ret


# 获取当前路径
def current_path():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


class ItemBasedCF:
    def __init__(self, train_file, test_file):
        self.train_file = train_file
        self.test_file = test_file
        self.W = dict()
        self.readData()

    def readData(self):
        # 读取文件，并生成用户-物品的评分表和测试集
        self.train = dict()  # 用户-物品的评分表
        for line in open(self.train_file):
            # user,item,score = line.strip().split(",")
            sline = line.strip()
            user = sline.split("")[0].strip()
            item = sline.split("")[1].strip()
            score = 1.0
            # user, item, score = sline[2:len(sline) - 1].split(",")
            self.train.setdefault(user, {})
            self.train[user][item] = int(score)
            # self.test = dict()  # 测试集
            # for line in open(self.test_file):
            #     # user,item,score = line.strip().split(",")
            #     sline = line.strip()
            #     user, item, score = sline[2:len(sline) - 1].split(",")
            #     self.test.setdefault(user, {})
            #     self.test[user][item] = int(score)

    def getUserItems(self):
        return self.train

    def ItemSimilarity(self):
        # 建立物品-物品的共现矩阵
        C = dict()  # 物品-物品的共现矩阵
        N = dict()  # 物品被多少个不同用户购买
        for user, items in self.train.items():
            for i in items.keys():
                N.setdefault(i, 0)
                N[i] += 1
                C.setdefault(i, {})
                for j in items.keys():
                    if i == j: continue
                    C[i].setdefault(j, 0)
                    C[i][j] += 1
        # 计算相似度矩阵
        for i, related_items in C.items():
            self.W.setdefault(i, {})
            for j, cij in related_items.items():
                self.W[i][j] = cij / (math.sqrt(N[i] * N[j]))
        return self.W

    # 给用户user推荐，前K个相关物品
    def Recommend(self, user, K=3, N=10):
        rank = dict()
        if self.train.get(user, -1) == -1:
            return
        action_item = self.train[user]  # 用户user产生过行为的item和评分
        for item, score in action_item.items():
            if self.W.get(item, -1) == -1:
                continue
            for j, wj in sorted(self.W[item].items(), key=lambda x: x[1], reverse=True)[0:K]:
                if j in action_item.keys():
                    continue
                rank.setdefault(j, 0)
                rank[j] += score * wj
        return dict(sorted(rank.items(), key=lambda x: x[1], reverse=True)[0:N])

    # train为训练集合，test为验证集合，给每个用户推荐N个物品
    # 召回率和准确率
    def RecallAndPrecision(self, train=None, test=None, K=3, N=10):
        train = train or self.train
        test = test or self.test
        hit = 0
        recall = 0
        precision = 0
        for user in train.keys():
            tu = test.get(user, {})
            rank = self.Recommend(user, K=K, N=N)
            for i, _ in rank.items():
                if i in tu:
                    hit += 1
            recall += len(tu)
            precision += N
        recall = hit / (recall * 1.0)
        precision = hit / (precision * 1.0)
        return (recall, precision)


if __name__ == '__main__':
    re = ItemBasedCF(current_path() + "//000000_0.txt", None)
    re.ItemSimilarity()
    # for i in range(1, 200):
    #     res = re.Recommend(str(i), 3, 2)
    #     if res != None:
    #         print(str(i) + ":" + ";".join(res.keys()))
    # rp = re.RecallAndPrecision()
    # print(rp)

    data = pandas.read_excel('partsclassfication20161108.xlsx')
    des_list = data['desc'].astype(str).tolist()

    partno_list = data['partno'].astype(str).tolist()
    print(len(partno_list))
    with open(current_path() + "//000000_0.txt") as f:
        lines = f.readlines()
        users = set()
        for line in lines:
            users.add(line.split("")[0])

        for user in users:
            res = re.Recommend(user, 3, 2)
            if res != None:
                buy_res = []
                for k in re.getUserItems()[user].keys():
                    try:
                        buy_res.append(des_list[partno_list.index(k)])
                    except:
                        pass
                recommend_res = []
                for j in res.keys():
                    try:
                        recommend_res.append(des_list[partno_list.index(j)])
                    except:
                        pass
                try:
                    if len(buy_res) >= 1 and len(recommend_res) >= 2:
                        print("用户:" + user + "已购买:" + "，".join(buy_res) + "；推荐:"+",".join(recommend_res))
                except:
                    pass