from apiclient.discovery import build
import time
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import re
import datetime
from dateutil import tz

import os
import pprint
import time
import urllib.error
import urllib.request

API_KEY = 'your api key'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=API_KEY
    )

"""description of function.
Args:
    param1 (type): description.
    param2...

Returns:
    type: description.
"""

def getChannelId(url):
    """From a url of channel, get channel Id.
    Args:
        url (str): str of url.

    Retruns:
        str: channelId
    """
    return url.split('/')[-1]

def download_file(url, dst_path):
        try:
            with urllib.request.urlopen(url) as web_file:
                data = web_file.read()
                with open(dst_path, mode='wb') as local_file:
                    local_file.write(data)
        except urllib.error.URLError as e:
            print(e)

def writeChannelInfo(url):
    def getChannelItems(url, youtube=youtube):
        channelId = getChannelId(url)
        response = youtube.channels().list(
            part = 'snippet, statistics',
            id = channelId,
            maxResults = 1
            ).execute()
        return response['items'][0]

    channel = getChannelItems(url)
    name = channel['snippet']['title']

    dir_c = f'res/youtuber/{name}/json/channel'
    if not os.path.isdir(dir_c):
        os.makedirs(dir_c)

    #iconのダウンロード
    icon_url = channel["snippet"]["thumbnails"]["high"]["url"]
    dir_i = f'res/Youtuber/{name}/icon.jpg'
    if not os.path.isfile(dir_i): download_file(icon_url, dir_i)

    #jsonのダウンロード
    if not os.path.isfile(f'{dir_c}/{name}_channel.json'):
        with open(f'{dir_c}/{name}_channel.json', 'w', encoding="utf-8") as f:
            json.dump(channel, f, ensure_ascii=False, indent=4)

    return

def getPlaylistIdOfUploadedVideos(channelId, youtube=youtube):
    """From a channelId, get playlistId of uploaded videos.
    Args:
        channelId (str): str of channelId.
        youtube (googleapiclient.discovery.Resource): resource of googleapiclient.discovery.

    Returns:
        str: playlistId of uploaded videos.
    """
    response = youtube.channels().list(
        part = 'contentDetails',
        id = channelId,
        maxResults = 1
        ).execute()

    contentDetails = response["items"][0]["contentDetails"]
    playlistIdOfUploadedVideos = contentDetails["relatedPlaylists"]["uploads"]

    return playlistIdOfUploadedVideos

def getVideoIdsFromPlaylist(plId, li, pagetoken=None, youtube=youtube):
    """From playlistId, get all videoIds in the playlist
    Args:
        plId (str): str of playlistId.
        li (list): list of videoIds. videoId will be appended in this.
            !!!ATTENTION!!! SET EMPTY LIST TO li, OR VIDEOS ID WILL BE APPENDED ORIGINAL LIST.
        pagetoken (str): pagetoken which shows which page to search.
        youtube (googleapiclient.discovery.Resource): resource of googleapiclient.discovery.

    Returns:
        list: list of videoIds.
    """
    response = youtube.playlistItems().list(
        part = 'snippet',
        playlistId = plId,
        maxResults = 50,
        pageToken = pagetoken
        ).execute()

    for i in range(len(response['items'])):
        snippet = response['items'][i]['snippet']
        v_id = snippet['resourceId']['videoId']
        li.append(v_id)

    try:
        nextPagetoken = response['nextPageToken']
        getVideoIdsFromPlaylist(plId, li, nextPagetoken)
    except:
        return li

    return li


def make_50xn_li(li):
    """Convert from 1d list to 2d list whose each row has 50 item.
    Because googleapiclient.discovery.Resource can search at most 50 items at once,
    you need convert list, for example list of videoIds, by using this to search more than 50 items.

    Args:
        li (list): 1d list.

    Return:
        list: 2d list whose each row has at most 50 item.
    """
    n = len(li)//50 + 1
    processed_li = [[0 for _ in range(50)] for __ in range(n)]
    k = 0

    for l in processed_li:
        for i in range(len(l)):
            if k < len(li):
                l[i] = li[k]
                k += 1

    #アイテム数が50件に満たない場合の処理
    processed_li[-1] = [a for a in processed_li[-1] if a != 0]

    return processed_li



def writeVideosInfo(v_ids, f_name='hoge', youtube=youtube):
    """Write data of videos as it is to new json files.
    Args:
        v_ids (list): 2d list of video_id whose each row has at most 50 item.
        f_name (str): file name to create new file and new json files.
        youtube (googleapiclient.discovery.Resource): resource of googleapiclient.discovery.

    Returns:
        None: (create new file and json files in it.)
    """
    #一度に50件までしか検索できないため
    #for i in range(1):

    dir = f'res/YouTuber/{f_name}/json/videos'
    if not os.path.isdir(dir):
        os.makedirs(dir)

    for i in range(len(v_ids)):
        if not os.path.isfile(f'{dir}/{f_name}_videos_{i}.json'):
            attr = ','.join(v_ids[i])
            v = youtube.videos().list(
                part = "snippet, contentDetails, statistics, player, liveStreamingDetails",
                id = attr
            ).execute()

            with open(f'{dir}/{f_name}_videos_{i}.json', 'w', encoding="utf-8") as f:
                json.dump(v, f, ensure_ascii=False, indent=4)

            #YouTube君に優しくしようね^^;
            time.sleep(1.5)
    return

def get_p_v_ids(url, youtube=youtube):
    """execute series of function to get proccessed list of video ids from url.
    Args:
        url (str): url of a channel.
    Returns:
        list: 2d list of video ids whose each row has at most 50 item.
    """
    channelId = getChannelId(url)
    playlistIdOfUploadedVideos = getPlaylistIdOfUploadedVideos(channelId)
    v_ids = getVideoIdsFromPlaylist(playlistIdOfUploadedVideos, li=[])
    p_v_ids = make_50xn_li(v_ids)

    return p_v_ids

###dictいじる編

def makeDictFromJsons(f_name):
    """make a list of python dictionaries from series json files whose name are f_name_n.json.
    Args:
        f_name (str): Original json file name which created by writeVideosInfo().

    Return:
        list: list of dictionaries of items.
    """

    dicts = []
    dir = f'res/YouTuber/{f_name}/json/videos'
    n = sum(os.path.isfile(os.path.join(dir, name)) for name in os.listdir(dir))
    for i in range(n):
        with open(f'{dir}/{f_name}_videos_{i}.json', 'r', encoding='utf-8') as f:
            di = json.load(f)
        dicts.extend(di['items'])
    return dicts

def getAll(items):
    """Get necessary items from original json.
    Args:
        items (list): list of dictionalies of items.

    Returns:
        list: list of dictionalies of necessary items.
    """
    li = []
    for item in items:
        dict = {}
        dict['v_id'] = item['id']
        dict['title'] = item['snippet']['title']
        dict['duration'] =  item['contentDetails']['duration']
        dict['publishedAt'] = item['snippet']['publishedAt']

        if 'viewCount' in item['statistics']:
            dict['viewCount'] = item['statistics']['viewCount']

        if 'likeCount' in item['statistics']:
            dict['likeCount'] = item['statistics']['likeCount']

        if  'commentCount' in item['statistics']:
            dict['commentCount'] = item['statistics']['commentCount']

        if 'embedHtml' in item['player']:
            dict['embedHtml'] = item['player']['embedHtml']

        if 'liveStreamingDetails' in item:
            if 'scheduledStartTime' in item['liveStreamingDetails']:
                dict['scheduledStartTime'] = item['liveStreamingDetails']['scheduledStartTime']

            if 'actualStartTime' in item['liveStreamingDetails']:
                dict['actualStartTime'] = item['liveStreamingDetails']['actualStartTime']

        li.append(dict)

    return li

def convertDurations(pt='PT30S'):
    """Convert duration from PTxxHxxMxxS to xxS.
    Args:
        pt (str): PTxxHxxMxxS.

    Returns:
        str: xxs.
    """
    m = re.findall(r'[0-9]+[A-Z]', pt)
    duration_s = 0
    for str in m:
        if 'H' in str:
            duration_s += int(str.split('H')[0]) * 60 * 60
        elif 'M' in str:
            duration_s += int(str.split('M')[0]) * 60
        elif 'S' in str:
            duration_s += int(str.split('S')[0])

    return datetime.timedelta(seconds=duration_s)

def convertISO8601(time='2018-09-23T13:43:00Z'):
    """Convert ISO8602 from yyyy-mm-ddTHH:MM:SSZ to datetime(%Y-%m-%d %H:%M)
    !!!ATTENTION!!!
        ISO8601 is shown in UCT. not jst.
    Args:
        time (str): str of time(yyyy-mm-ddTHH:MM:SSZ)

    Returns:
        datetime: datetime('%Y-%m-%d %H:%M)
    """
    JST = tz.gettz('Asia/Tokyo')
    UTC = tz.gettz('UTC')

    date_s = time[0:10]
    time_s = time[11:16]
    elem = date_s + ' ' + time_s
    date = datetime.datetime.strptime(elem, '%Y-%m-%d %H:%M')
    date_utc = date.replace(tzinfo=UTC)
    date_jst = date_utc.astimezone(JST)
    return date_jst.replace(tzinfo=None)

def convertDict(item):
    """Convert all item into proper form.
    Args:
        item (dict): item which is in list created by getAll().

    Returns:
        dict: dict which has proper-form items.
    """
    item['duration'] = convertDurations(item['duration'])
    item['publishedAt'] = convertISO8601(item['publishedAt'])
    if 'viewCount' in item:
        item['viewCount'] = int(item['viewCount'])
    if 'likeCount' in item:
        item['likeCount'] = int(item['likeCount'])
    if 'commentCount' in item:
        item['commentCount'] = int(item['commentCount'])
    if 'scheduledStartTime' in item:
        item['scheduledStartTime'] = convertISO8601(item['scheduledStartTime'])
    if 'actualStartTime' in item:
        item['actualStartTime'] = convertISO8601(item['actualStartTime'])

    return item

def getConvertedItems(items):
    """Execute convertion and get converted items.
    Args:
        items (list): list of items.
    Returns:
        list: list of proper-form items.
    """
    li = []
    for item in items:
        li.append(convertDict(item))
    return li

def s_to_hms(s):
    """Convert time from s to hms
    Args:
        s(int): seconds.

    Returns:
        str: HH:MM:SS.
    """
    h, m = 0, 0
    if s > 3600:
        h = s // 3600
        s -= h*3600
    if s > 60:
        m = (s-h) // 60
        s -= m*60

    return f'{h:02}:{m:02}:{s:02}'

def getChannelDict(name):
    dir = f'res/YouTuber/{name}/json/channel'
    with open(f'{dir}/{name}_channel.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def getConvertedChannelDict(originalDict):
    dict = {}
    snippet = originalDict["snippet"]
    statistics = originalDict["statistics"]
    dict["publishedAt"] = convertISO8601(snippet["publishedAt"])
    dict["viewCount"] = int(statistics["viewCount"])
    dict["subscriberCount"] = int(statistics["subscriberCount"])
    dict["videoCount"] = int(statistics["videoCount"])
    return dict

def getChannelTitle(url):
    channelId = getChannelId(url)
    response = youtube.channels().list(
        part = 'snippet',
        id = channelId,
        maxResults = 1
        ).execute()
    return response['items'][0]['snippet']['title']

def getDf_c(url):
    name = getChannelTitle(url)
    writeChannelInfo(url)
    originalDict = getChannelDict(name)
    convertedDict = getConvertedChannelDict(originalDict)
    df_c = pd.DataFrame.from_dict(convertedDict, orient='index').T
    return df_c

def getDf(url):
    """Get youtuber's DataFrame.
    !!!ATTENTION!!!:
        This df's id is default. not v_id.
    Args:
        url (str): url of Channel.
        name: name to make file and folder.
    Returns:
        DataFrame: dataframe of a youtuber.
    """
    p_v_ids = get_p_v_ids(url)
    #jsonへ書き込み
    name = getChannelTitle(url)
    writeChannelInfo(url)
    writeVideosInfo(p_v_ids, name)
    #これがあると、50件までの制約がなくなる
    originalDict = makeDictFromJsons(name)
    convertedDict = getConvertedItems(getAll(originalDict))
    df = pd.DataFrame.from_dict(convertedDict)
    return df