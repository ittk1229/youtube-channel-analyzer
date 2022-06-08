import YTtoDF as ytd
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import datetime
from PIL import Image
import os

def getCol(df,col):
    """特定の列を抜き出してid付きのdataframeを作成。
    Args:
        df (DataFrame): as it is.
        col (str): name of col.

    Returns:
        DataFrame: 上記のdataframe。
    """
    df_col = pd.DataFrame({"v_id":df.v_id, f'{col}':df[col]})
    df_col.set_index('v_id', inplace=True)
    return df_col

def getDetailsOfActualStartTime(df):
    """Get DataFrame of details of published at.
    Args:
        df (DataFrame): as it is.

    Returns:
        DataFrame: the same dataframe as description.
    """
    df_ast = getCol(df, 'actualStartTime').dropna()
    df_ast['date'] = '-'
    df_ast['year'] = '-'
    df_ast['month'] = '-'
    df_ast['dayOfTheWeek'] = '-'
    df_ast['hour'] = '-'

    for i, row in df_ast.iterrows():
        df_ast.at[i, 'date'] = row.actualStartTime.strftime('%Y-%m-%d')
        df_ast.at[i, 'year'] = row.actualStartTime.strftime('%Y')
        df_ast.at[i, 'month'] = row.actualStartTime.strftime('%b')
        df_ast.at[i, 'dayOfTheWeek'] = row.actualStartTime.strftime('%a')
        df_ast.at[i, 'hour'] = row.actualStartTime.strftime('%H:%M:%S')

    return df_ast

def getDetailsOfLiveStream(df):
    """配信情報、動画の開始時間の詳細等必要な情報を統合したDataFrameを作成
    df: DataFrame -> DataFrame
    """
    df_ls = df.dropna(subset=['actualStartTime']).set_index('v_id')
    df_ast = getDetailsOfActualStartTime(df).drop('actualStartTime', axis=1)
    return pd.merge(df_ls, df_ast, on='v_id')

#棒グラフに使えるよ編
def autolabel(graph):
    for rect in graph:
        height = rect.get_height()
        plt.annotate('{}'.format(height),
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha='center', va='bottom')

def makeCt(ct, key):
    if key in ct.index:
        return eval(f'ct.{key}')
    else:
        return 0

def myMax(ct):
    return 0 if ct.empty else max(ct)

def setFig(width=15.0, height=12.0, title='title', edgecolor='#eeeeee'):
    plt.rcParams['font.family'] = 'MS Gothic'
    plt.rcParams['font.size'] = 16
    fig = plt.figure(figsize=(width, height), facecolor="#eeeeee", linewidth=7, edgecolor=edgecolor)
    plt.subplots_adjust(wspace=0.3, hspace=0.45)
    fig.suptitle(title, size=36, weight=2)
    fig.tight_layout()
    return fig

###StreamCountPerDotW編###
def setStreamCountPerDotW(fig, position, df_ls, title, color='#f38181', maxi=0, isGetMax=False):
    """DotW means Day of the Week
    """
    left = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    ct = df_ls.groupby('dayOfTheWeek').count().actualStartTime
    height = [makeCt(ct, left[i]) for i in range(len(left))]
    if maxi == 0: maxi = max(height) + 30

    if isGetMax: return maxi

    ax = fig.add_subplot(position)
    autolabel(ax.bar(left, height, color=color, edgecolor='#393e46'))
    ax.set_ylim(top=maxi)
    ax.set_title(title)
    ax.set_xlabel('曜日（曜日）')
    ax.set_ylabel('配信回数（回）')
    ax.set_facecolor('white')

def showStreamCountPerDotW(dfs, name, edgecolor="#eeeeee"):
    fig = setFig(title=name)
    df_ls = dfs[0]
    setStreamCountPerDotW(fig, 111, df_ls,'2018-2021', edgecolor)


def showStreamCountPerDotWFrom18To21(dfs, name, edgecolor="#eeeeeee"):
    fig = setFig(title=f'Total stream hours per day of the week of {name}')
    df_ls = dfs[0]
    li_for_maxi = []
    for i in range(4):
        year = 2018 + i
        df_ls_x = df_ls[df_ls.year == str(year)]
        local_maxi = setStreamTimePerDotW(fig, 111, df_ls_x, '', isGetMax=True)
        li_for_maxi.append(local_maxi)
    maxi = max(li_for_maxi)


    colors = ['#f38181', '#fce38a', '#eaffd0', '#95e1d3']
    for i in range(4):
        year = 2018 + i
        df_ls_x = df_ls[df_ls.year == str(year)]
        setStreamTimePerDotW(fig, int(f'22{i+1}'), df_ls_x, str(year), maxi=maxi, color=colors[i])



###StreamCountPerST編###
def setStreamCountPerST(fig, position, df_ls, title, color='#f38181'):
    dates_list = [date.hour for date in df_ls.actualStartTime]
    ax = fig.add_subplot(position)
    ax.hist(dates_list, 24, range=(0,23), color=color, ec='#393e46')
    ax.set_title(title)
    ax.set_xlabel('配信開始時間（時）')
    ax.set_ylabel('配信回数（回）')
    ax.set_facecolor('white')


def showStreamCountPerST(dfs, name, edgecolor="#eeeeeee"):
    """ST means Start Time"""
    fig = setFig(title=f'Stream count per start time of {name}')
    df_ls = dfs[0]
    setStreamCountPerST(fig, 111, df_ls, '2018-2021', edgecolor)


def showStreamCountPerSTFrom18To21(dfs, name, edgecolor="#eeeeee"):
    fig = setFig(title=f'Stream count per start time of {name}')
    df_ls = dfs[0]

    colors = ['#f38181', '#fce38a', '#eaffd0', '#95e1d3']
    for i in range(4):
        year = 2018 + i
        df_ls_x = df_ls[df_ls.year == str(year)]
        setStreamCountPerST(fig, int(f'22{i+1}'), df_ls_x, str(year), colors[i])


###streamCountPerMonth編###
def setStreamCountPerM(fig, position, df_ls, title, color='#20aaff', maxi=0, isGetMax=False):
    """DotW means Day of the Week
    """
    left = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ct = df_ls.groupby('month').count().actualStartTime
    height = [makeCt(ct, left[i]) for i in range(len(left))]
    if maxi == 0: maxi = max(height) + 5

    if isGetMax: return maxi

    ax = fig.add_subplot(position)
    autolabel(ax.bar(left, height, color=color, edgecolor='#393e46'))
    ax.set_ylim(top=maxi)
    ax.set_title(title)
    ax.set_xlabel('月（月）')
    ax.set_ylabel('配信回数（回）')
    ax.set_facecolor('white')


def showStreamCountPerM(dfs, name, edgecolor="#eeeeee"):
    fig = setFig(title=f'Stream count per month of {name}')
    df_ls = dfs[0]
    setStreamCountPerM(fig, 111, df_ls,'2018-2021', edgecolor)


def showStreamCountPerMonthFrom18To21(dfs, name, edgecolor="#eeeeeee"):
    fig = setFig(title=f'Stream count per month of {name}')
    df_ls = dfs[0]

    li_for_maxi = []
    for i in range(4):
        year = 2018 + i
        df_ls_x = df_ls[df_ls.year == str(year)]
        local_maxi = setStreamCountPerDotW(fig, 111, df_ls_x, '', isGetMax=True)
        li_for_maxi.append(local_maxi)
    maxi = max(li_for_maxi)

    colors = ['#f38181', '#fce38a', '#eaffd0', '#95e1d3']
    for i in range(4):
        year = 2018 + i
        df_ls_x = df_ls[df_ls.year == str(year)]
        setStreamCountPerDotW(fig, f'22{i+1}', df_ls_x, str(year), maxi=maxi, color=colors[i])


#streamtimeDotw編
def getTotalHours(ser_timedelta):
    total = datetime.timedelta(seconds=0)
    for i in ser_timedelta:
        total += i
    totalHours = total/datetime.timedelta(hours=1)
    return np.round(totalHours, decimals=1)

def setStreamTimePerDotW(fig, position, df_ls, title, color='#f38181'):
    """DotW means Day of the Week
    """
    def myFunc(df_ls , dayOfTheWeek):
        ser_timedelta = df_ls[df_ls.dayOfTheWeek == dayOfTheWeek].duration
        return [np.round(i/datetime.timedelta(hours=1), decimals=1) for i in ser_timedelta]

    left = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    height = tuple([myFunc(df_ls, left[i]) for i in range(len(left))])

    ax = fig.add_subplot(position)
    ax.boxplot(height, patch_artist=True, boxprops=dict(facecolor=color), sym='')
    ax.set_xticklabels(left)
    ax.set_title(title)
    ax.set_xlabel('曜日（曜日）')
    ax.set_ylabel('配信時間（時間）')

def showStreamTimePerDotW(dfs, name, edgecolor="#eeeeee"):
    fig = setFig(f'Total stream hours per day of the week of {name}')
    df_ls = dfs[0]
    setStreamTimePerDotW(fig, 111, df_ls,'2018-2021', color=edgecolor)


def showStreamTimePerDotWFrom18To21(dfs, name, edgecolor="#eeeeeee"):
    fig = setFig(title=f'Total stream hours per day of the week of {name}')
    df_ls = dfs[0]

    li_for_maxi = []
    for i in range(4):
        year = 2018 + i
        df_ls_x = df_ls[df_ls.year == str(year)]
        local_maxi = setStreamTimePerDotW(fig, 111, df_ls_x, '', isGetMax=True)
        li_for_maxi.append(local_maxi)
    maxi = max(li_for_maxi)


    colors = ['#f38181', '#fce38a', '#eaffd0', '#95e1d3']
    for i in range(4):
        year = 2018 + i
        df_ls_x = df_ls[df_ls.year == str(year)]
        setStreamTimePerDotW(fig, int(f'22{i+1}'), df_ls_x, str(year), maxi=maxi, color=colors[i])



###median　of above編
def setMedianStreamTimePerDotW(fig, position, df_ls, title, color='#f38181', maxi=0, isGetMax=False):
    """DotW means Day of the Week
    """
    def myFunc(df_ls , dayOfTheWeek):
        ser_timedelta = df_ls[df_ls.dayOfTheWeek == dayOfTheWeek].duration
        np.set_printoptions(precision=2)
        ser_float = pd.Series([i/datetime.timedelta(hours=1) for i in ser_timedelta])
        return ser_float.median()

    left = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    height = [myFunc(df_ls, left[i]) for i in range(len(left))]
    if maxi == 0: maxi = max(height) + 0.5

    if isGetMax: return maxi

    ax = fig.add_subplot(position)
    ax.bar(left, height, color=color, edgecolor='#393e46')
    ax.set_ylim(top=maxi)
    ax.set_title(title)
    ax.set_xlabel('曜日（曜日）')
    ax.set_ylabel('配信時間の中央値（時間）')
    ax.set_facecolor('white')
    return

def showMedianStreamTimePerDotW(dfs, name, edgecolor="#eeeeee"):
    fig = setFig(title=f'Median stream hours per day of the week of {name}')
    df_ls = dfs[0]
    setMedianStreamTimePerDotW(fig, 111, df_ls,'2018-2021', color=edgecolor)


def showMedianStreamTimePerDotWFrom18To21(dfs, name, edgecolor="#eeeeeee"):
    fig = setFig(title=f'Total stream hours per day of the week of {name}')
    df_ls = dfs[0]

    li_for_maxi = []
    for i in range(4):
        year = 2018 + i
        df_ls_x = df_ls[df_ls.year == str(year)]
        local_maxi = setMedianStreamTimePerDotW(fig, 111, df_ls_x, '', isGetMax=True)
        li_for_maxi.append(local_maxi)
    maxi = max(li_for_maxi)


    colors = ['#f38181', '#fce38a', '#eaffd0', '#95e1d3']
    for i in range(4):
        year = 2018 + i
        df_ls_x = df_ls[df_ls.year == str(year)]
        setMedianStreamTimePerDotW(fig, int(f'22{i+1}'), df_ls_x, str(year), maxi=maxi, color=colors[i])



#img編
def setImg(fig, position, name, title, isQ=False):
    if isQ:
        im = Image.open(f'res/q.jpg')
    else:
        im = Image.open(f'res/YouTuber/{name}/icon.jpg')

    im_list = np.array(im)
    ax = fig.add_subplot(position)
    ax.imshow(im_list)
    ax.set_title(title)
    ax.axis('off')


def showImg(dfs, name, color='#ffffff'):
    fig = setFig(title=name)
    setImg(fig, 111, name, name)

def showAllGraph(dfs, name, edgecolor="#eeeeee"):
    fig = setFig(title=f'{name}のグラフ')
    df_ls = dfs[0]
    df_c = dfs[1]
    colors = ['#f38181', '#fce38a', '#eaffd0', '#95e1d3']
    setStreamCountPerDotW(fig, 231, df_ls, '曜日ごとの配信回数', colors[0])
    setStreamCountPerST(fig, 232, df_ls, '配信開始時間のヒストグラム', colors[1])
    setStreamTimePerDotW(fig, 233, df_ls, '曜日ごとの配信時間の箱ひげ図', colors[2])
    setImg(fig, 236, name, name)
    setTable(fig, 235, df_c, 'チャンネル情報')

    fig.savefig(f'output/{name}.png')

#表編
def setTable(fig, position, df_c, title):
    ax = fig.add_subplot(position)
    row = df_c.iloc[0]
    data = [[row[0].strftime("%Y/%m/%d")], [f'{row[1]:,} 回'], [f'{row[2]:,} 人'], [f'{row[3]:,} 本']]
    axis1 = ["チャンネル設立日", "総再生回数", "登録者数", "総動画数"]

    the_table = ax.table(cellText=data, rowLabels=axis1, loc='center')
    ax.axis('off')

    the_table.set_fontsize(24)
    for pos, cell in the_table.get_celld().items():
        cell.set_width(1)
        cell.set_height(1/len(data))


def showTable(dfs, name, edgecolor='#eeeeee'):
    fig = setFig(title='table')
    df_c = dfs[1]
    setTable(fig, 111, df_c, title='')

#出力編
def getDictOfLiverColor():
    with open('res/liverColors.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def executeShowGraph(url, func, color='#eeeeee'):
    """すべてのshowXX関数は引数にurlとnameをもつので
    関数を指定すればどの関数でも見られるようにしたよ"""
    name = ytd.getChannelTitle(url)
    df = ytd.getDf(url)
    df_ls = getDetailsOfLiveStream(df)
    df_c = ytd.getDf_c(url)
    dfs = [df_ls, df_c]
    func(dfs, name, color)



#クイズ編
def showQuestion(dfs, name, edgecolor='#eeeeee'):
    fig = setFig(title='だ～～～～れだ？？')
    df_ls = dfs[0]
    df_c = dfs[1]
    colors = ['#f38181', '#fce38a', '#eaffd0', '#95e1d3']
    setStreamCountPerDotW(fig, 231, df_ls, '曜日ごとの配信回数', colors[0])
    setStreamCountPerST(fig, 232, df_ls, '配信開始時間のヒストグラム', colors[1])
    setStreamTimePerDotW(fig, 233, df_ls, '曜日ごとの配信時間の箱ひげ図', colors[2])
    setImg(fig, 236, '???', '???', isQ=True)
    setTable(fig, 235, df_c, 'チャンネル情報')


def showAnswer(dfs, name, edgecolor="#eeeeee"):
    fig = setFig(title=f'正解は {name}')

    df_ls = dfs[0]
    df_c = dfs[1]
    colors = ['#f38181', '#fce38a', '#eaffd0', '#95e1d3']
    setStreamCountPerDotW(fig, 231, df_ls, '曜日ごとの配信回数', colors[0])
    setStreamCountPerST(fig, 232, df_ls, '配信開始時間のヒストグラム', colors[1])
    setStreamTimePerDotW(fig, 233, df_ls, '曜日ごとの配信時間の箱ひげ図', colors[2])
    setImg(fig, 236, name, name)
    setTable(fig, 235, df_c, 'チャンネル情報')


def question():
    url = input('Please input channel url')
    executeShowGraph(url, showQuestion)
    executeShowGraph(url, showAnswer)