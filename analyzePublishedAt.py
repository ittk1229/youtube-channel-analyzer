import YTtoDF as ytd
import pandas as pd
import json
import matplotlib.pyplot as plt

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

def getDetailsOfPublishedAt(df):
    """Get DataFrame of details of published at.
    Args:
        df (DataFrame): as it is.
    
    Returns:
        DataFrame: the same dataframe as description. 
    """
    df_pa = getCol(df, 'publishedAt')
    df_pa['date'] = '-'
    df_pa['year'] = '-'
    df_pa['month'] = '-'
    df_pa['dayOfTheWeek'] = '-'
    df_pa['hour'] = '-'

    for i, row in df_pa.iterrows():
        df_pa.at[i, 'date'] = row.publishedAt.strftime('%Y-%m-%d')
        df_pa.at[i, 'year'] = row.publishedAt.strftime('%Y')
        df_pa.at[i, 'month'] = row.publishedAt.strftime('%m')
        df_pa.at[i, 'dayOfTheWeek'] = row.publishedAt.strftime('%a')
        df_pa.at[i, 'hour'] = row.publishedAt.strftime('%H:%M:%S')
    
    return df_pa


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

###StreamCountPerDotW編###
def makeAx_DotW(fig, position, ct, year, maxi=0, color='#f38181'):
    """DotW means Day of the Week
    """
    left = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    ax = fig.add_subplot(position)
    height = [makeCt(ct, left[i]) for i in range(len(left))]
    autolabel(ax.bar(left, height, color=color, edgecolor='#393e46'))
    if maxi == 0: maxi = max(height) + 5
    ax.set_ylim(top=maxi)
    ax.set_title(year)
    ax.set_xlabel('Day of the Week')
    ax.set_ylabel('Stream count')
    ax.set_facecolor('white')
    return

def setStreamCountPerDotW(fig, position, df_pa, title, color='#20aaff', maxi=0):
    ct = df_pa.groupby('dayOfTheWeek').count().publishedAt
    makeAx_DotW(fig, position, ct, title, maxi, color)

def showStreamCountPerDotW(df_pa, name, edgecolor="#eeeeee"):
    fig = plt.figure(figsize=(13.0, 10.0), facecolor="#eeeeee", linewidth=7, edgecolor=edgecolor)

    setStreamCountPerDotW(fig, 111, df_pa,'2018-2021', '#20aaff')

    plt.subplots_adjust(wspace=0.2, hspace=0.3)
    fig.suptitle(f'Stream count per day of the week of {name}', size=24, weight=2)

    plt.show()

def showStreamCountPerDotWFrom18To21(df_pa, name, edgecolor="#eeeeeee"):
    fig = plt.figure(figsize=(13.0, 10.0), facecolor="#eeeeee", linewidth=7, edgecolor=edgecolor)
    def myFunc(df_pa, year):
        df_pa_x = df_pa[df_pa.year == year]
        ct_x = df_pa_x.groupby('dayOfTheWeek').count().publishedAt
        return ct_x

    li_for_maxi = []
    for i in range(4):
        year = 2018 + i
        ct_x = myFunc(df_pa, str(year))
        li_for_maxi.append(myMax(ct_x))
    maxi = max(li_for_maxi) + 5

    colors = ['#f38181', '#fce38a', '#eaffd0', '#95e1d3']
    for i in range(4):
        year = 2018 + i
        df_pa_x = df_pa[df_pa.year == str(year)]
        setStreamCountPerDotW(fig, int(f'22{i+1}'), df_pa_x, str(year), maxi=maxi, color=colors[i])

    plt.subplots_adjust(wspace=0.2, hspace=0.3)
    fig.suptitle(f'Stream count per day of the week of {name}', size=24, weight=2)

    plt.show()

###StreamCountPerST編###
def makeAx_ST(fig, position, dates_list, year, color='#f38181'):
    ax = fig.add_subplot(position)
    ax.hist(dates_list, 24, range=(0,23), color=color, ec='#393e46')
    ax.set_title(year)
    ax.set_xlabel('Hour')
    ax.set_ylabel('Stream count')
    ax.set_facecolor('white')
    return

def setStreamCountPerST(fig, position, df_pa, title, color='#20aaff'):
    dates_list = [date.hour for date in df_pa.publishedAt]
    makeAx_ST(fig, position, dates_list, title, color)


def showStreamCountPerSTFrom18To21(df_pa, name, edgecolor="#eeeeee"):
    fig = plt.figure(figsize=(13.0, 10.0), facecolor="#eeeeee", linewidth=7, edgecolor=edgecolor)

    colors = ['#f38181', '#fce38a', '#eaffd0', '#95e1d3']
    for i in range(4):
        year = 2018 + i
        df_pa_x = df_pa[df_pa.year == str(year)]
        setStreamCountPerST(fig, int(f'22{i+1}'), df_pa_x, str(year), colors[i])

    plt.subplots_adjust(wspace=0.2, hspace=0.3)
    fig.suptitle(f'Stream count per start time of {name}', size=24, weight=2)

    plt.show()

def showStreamCountPerST(df_pa, name, edgecolor="#eeeeeee"):
    """ST means Start Time"""
    fig = plt.figure(figsize=(13.0, 10.0), facecolor="#eeeeee", linewidth=7, edgecolor=edgecolor)

    setStreamCountPerST(fig, 111, df_pa, '2018-2021')

    plt.subplots_adjust(wspace=0.2, hspace=0.3)
    fig.suptitle(f'Stream count per start time of {name}', size=24, weight=2)

    plt.show()

def getDictOfLiverColor():
    with open('res/liverColors.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def executeShowGraph(url, name, func, color='#eeeeee'):
    """すべてのshowXX関数は引数にurlとnameをもつので
    関数を指定すればどの関数でも見られるようにしたよ"""
    df = ytd.getDf(url, name)
    df_pa = getDetailsOfPublishedAt(df)
    dict_liverColor = getDictOfLiverColor()
    if name in dict_liverColor: color = dict_liverColor[name]
    func(df_pa, name, color)

def showAllGraph(df_pa, name, edgecolor="#eeeeee"):
    fig = plt.figure(figsize=(13.0, 10.0), facecolor="#eeeeee", linewidth=7, edgecolor=edgecolor)

    setStreamCountPerDotW(fig, 121, df_pa, 'Stream count per day of the week')
    setStreamCountPerST(fig, 122, df_pa, 'Stream count per start time')

    plt.subplots_adjust(wspace=0.2, hspace=0.3)
    fig.suptitle(f'Figures of {name}', size=24, weight=2)

    plt.show()