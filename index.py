#!/usr/bin/env python3

from cProfile import run
from re import S
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from tabulate import tabulate
import time

# 環境設定
plt.rcParams['font.family'] = "MS Gothic"
pd.options.display.precision = 1

giants_2021 = pd.read_csv(
    "./player_data/2021/giants_2021.csv", encoding="cp932")

# 特徴量エンジニアリング
# 不要な列を削除
giants_2021.drop(["背番号", "打数", "打率", "試合", "得点", "塁打", "打点", "盗塁",
                 "盗塁刺", "犠打", "犠飛", "併殺打",  "出塁率", "長打率"], axis=1, inplace=True)

# 単打の列を追加
single = giants_2021['安打'] - (giants_2021['二塁打'] +
                              giants_2021['三塁打'] + giants_2021['本塁打'])
giants_2021.insert(3, "単打", single)

# 割合変換したデータフレームを作成
single_rate = giants_2021["単打"] / giants_2021["打席"]
double_rate = giants_2021["二塁打"] / giants_2021["打席"]
triple_rate = giants_2021["三塁打"] / giants_2021["打席"]
HR_rate = giants_2021["本塁打"] / giants_2021["打席"]
BB_IBB_HBP_rate = (
    giants_2021["四球"] + giants_2021["敬遠"] + giants_2021["死球"]) / giants_2021["打席"]
K_rate = giants_2021["三振"] / giants_2021["打席"]
out_rate = 1 - (single_rate + double_rate + triple_rate +
                HR_rate + BB_IBB_HBP_rate + K_rate)

giants_2021_rate = pd.DataFrame({"選手名": giants_2021["選手名"], "単打": single_rate, "二塁打": double_rate,
                                "三塁打": triple_rate, "本塁打": HR_rate, "四死球": BB_IBB_HBP_rate, "三振": K_rate, "アウト": out_rate})
# NPBの平均投手の推移確率を追加
pitcher = pd.Series(["投手", 0.076, 0.014, 0.001, 0.005, 0.0323,
                    0.436, 1-sum([0.076, 0.014, 0.001, 0.005, 0.0323, 0.436])], index=giants_2021_rate.columns.values)
giants_2021_rate = giants_2021_rate.append(pitcher, ignore_index=True)
giants_2021_rate = giants_2021_rate.set_index("選手名")

# 打順の作成
# -nf3_BaseBall_Data_Houseよりシーズンでその打順に座った回数が最も高い人を採用 (https://nf3.sakura.ne.jp/2021/Central/G/t/kiyou.htm)
A = ["松原　聖弥", "坂本　勇人", "丸　佳浩", "岡本　和真",
     "ウィーラー", "梶谷　隆幸", "中島　宏之", "大城　卓三", "投手"]
B = ["陽　岱鋼", "八百板　卓丸", "廣岡　大志",
     "中田　翔", "香月　一也", "石川　慎吾",  "立岡　宗一郎", "岸田　行倫", "投手"]
giants_2021_order = A
giants_2021_order_rate = pd.DataFrame(
    index=[], columns=giants_2021_rate.columns.values)
for order in giants_2021_order:
    giants_2021_order_rate = giants_2021_order_rate.append(
        giants_2021_rate.loc[order])
# giants_2021_order_rate.insert(0, "打順", list(range(1, 10)))

# 進塁規則(D’Esopo and Lefkowitzの進塁規則)


# 1試合を定義する関数


def game():
    game_end = False
    number = 1
    inning = 0
    outcount = 0
    runner = [0, 0, 0]
    score = 0

    col = giants_2021_order_rate.columns.values

# 1イニングのプレイ
    while((outcount < 3) and (inning < 9)):
        result = np.random.choice(
            col, 1, p=giants_2021_order_rate.loc[giants_2021_order[number-1]])
        # print(number, ":",
        #       giants_2021_order[number-1], ':', result[0])
        if((result[0] == "三振") or (result[0] == "アウト")):
            outcount += 1
        else:
            if runner == [0, 0, 0]:
                if((result[0] == "単打") or (result[0] == "四死球")):
                    runner = [1, 0, 0]
                elif result[0] == "二塁打":
                    runner = [0, 1, 0]
                elif result[0] == "三塁打":
                    runner = [0, 0, 1]
                else:
                    runner = [0, 0, 0]
                    score += 1
            elif runner == [1, 0, 0]:
                if((result[0] == "単打") or (result[0] == "四死球")):
                    runner = [1, 1, 0]
                elif result[0] == "二塁打":
                    runner = [0, 1, 1]
                elif result[0] == "三塁打":
                    runner = [0, 0, 1]
                    score += 1
                else:
                    runner = [0, 0, 0]
                    score += 2
            elif runner == [0, 1, 0]:
                if result[0] == "単打":
                    runner = [1, 0, 0]
                    score += 1
                elif result[0] == "四死球":
                    runner = [1, 1, 0]
                elif result[0] == "二塁打":
                    runner = [0, 1, 0]
                    score += 1
                elif result[0] == "三塁打":
                    runner = [0, 0, 1]
                    score += 1
                else:
                    runner = [0, 0, 0]
                    score += 2
            elif runner == [0, 0, 1]:
                if result[0] == "単打":
                    runner = [1, 0, 0]
                    score += 1
                elif result[0] == "四死球":
                    runner = [1, 0, 1]
                elif result[0] == "二塁打":
                    runner = [0, 1, 0]
                    score += 1
                elif result[0] == "三塁打":
                    runner = [0, 0, 1]
                    score += 1
                else:
                    runner = [0, 0, 0]
                    score += 2
            elif runner == [1, 1, 0]:
                if result[0] == "単打":
                    runner = [1, 1, 0]
                    score += 1
                elif result[0] == "四死球":
                    runner = [1, 1, 1]
                elif result[0] == "二塁打":
                    runner = [0, 1, 1]
                    score += 1
                elif result[0] == "三塁打":
                    runner = [0, 0, 1]
                    score += 2
                else:
                    runner = [0, 0, 0]
                    score += 3
            elif runner == [1, 0, 1]:
                if result[0] == "単打":
                    runner = [1, 1, 0]
                    score += 1
                elif result[0] == "四死球":
                    runner = [1, 1, 1]
                elif result[0] == "二塁打":
                    runner = [0, 1, 1]
                    score += 1
                elif result[0] == "三塁打":
                    runner = [0, 0, 1]
                    score += 2
                else:
                    runner = [0, 0, 0]
                    score += 3
            elif runner == [0, 1, 1]:
                if result[0] == "単打":
                    runner = [1, 0, 0]
                    score += 2
                elif result[0] == "四死球":
                    runner = [1, 1, 1]
                elif result[0] == "二塁打":
                    runner = [0, 1, 0]
                    score += 2
                elif result[0] == "三塁打":
                    runner = [0, 0, 1]
                    score += 2
                else:
                    runner = [0, 0, 0]
                    score += 3
            else:
                if result[0] == "単打":
                    runner = [1, 1, 0]
                    score += 2
                elif result[0] == "四死球":
                    runner = [1, 1, 1]
                    score += 1
                elif result[0] == "二塁打":
                    runner = [0, 1, 1]
                    score += 2
                elif result[0] == "三塁打":
                    runner = [0, 0, 1]
                    score += 3
                else:
                    runner = [0, 0, 0]
                    score += 3
        # if outcount != 3:
            # print('ランナー:', runner)
            # print('アウトカウント:', outcount)
            # print('-------------------------------------------------------------------')
        if outcount == 3:
            outcount = 0
            inning += 1
            runner = [0, 0, 0]
            # print(inning, '回終了。現在の得点は、', score)
            # print('-------------------------------------------------------------------')
        number += 1
        if(number == 10):
            number = 1
    return score


# 試合を複数回シミュレーション
n = 0
scores = []
while n < 10000:
    scores.append(game())
    n += 1
print('平均：', np.mean(scores), '標準偏差：', np.std(scores),
      '最大値：', np.max(scores), '最小値：', np.min(scores))

plt.hist(scores, bins=15)
plt.title('2021年読売ジャイアンツのシミュレーション結果')
plt.xlabel('得点')
plt.ylabel('頻度')
plt.show()


# colnames = giants_2021_rate.columns.values
# print(tabulate(giants_2021_order_rate, colnames,
#       tablefmt='fancy_grid', showindex=True))
