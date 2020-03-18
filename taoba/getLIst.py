import requests
import zlib
import json
import base64
import time

"""
post出错时的response
{'code': 'id', 'msg': '参数id应该大于1.'}
"""

"""
config:{'requestTime': 1584453397313, 'pf': 'h5'}, url: https://www.tao-ba.club/config -> response null
detail:{'id': '1322', 'requestTime': 1584453397381, 'pf': 'h5'}, url: https://www.tao-ba.club/idols/detail
buystates:{'yyaid': '1322', 'requestTime': 1584453397489, 'pf': 'h5'}, url: https://www.tao-ba.club/idols/join/buystats -> resoponse null
join:{'ismore': False, 'limit': 15, 'id': '1322', 'offset': 0, 'requestTime': 1584457188679, 'pf': 'h5'}, url: https://www.tao-ba.club/idols/join
"""


def addSalt(ori: bytearray):
    # 从网页JS当中提取到的混淆盐值，每隔一位做一次异或运算
    Salt = '%#54$^%&SDF^A*52#@7'
    i = 0
    for ch in ori:
        if i % 2 == 0:
            ch = ch ^ ord(Salt[(i // 2) % len(Salt)])
        ori[i] = ch
        i += 1
    return ori


def encodeData(ori: str):
    # 开头的数字是原始报文长度
    Length = len(ori)
    Message = str.encode(ori)
    # 首先用zlib进行压缩
    Compressed = bytearray(zlib.compress(Message))
    # 然后加盐混淆
    Salted = addSalt(Compressed)
    # 最后将结果转化为base64编码
    Result = base64.b64encode(Salted).decode('utf-8')
    # 将长度头和base64编码的报文组合起来
    return str(Length) + '$' + Result


def decodeData(ori: str):
    # 分离报文长度头
    # tbc: 增加报文头长度的验证
    Source = ori.split('$')[1]
    # base64解码
    B64back = bytearray(base64.b64decode(Source))
    # 重新进行加盐计算，恢复原始结果
    Decompressed = addSalt(B64back)
    # zlib解压
    Result = zlib.decompress(Decompressed).decode('utf-8')
    # 提取json
    return json.loads(Result)


header = {
    'Content-Type': 'application/json',
    'Origin': 'https://www.tao-ba.club',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Host': 'www.tao-ba.club',
    'Cookie': 'l10n=zh-cn',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15',
    'Referer': 'https://www.tao-ba.club/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}
cookie = {
    'l10n': 'zh-cn',
}

"""
detail: return project info
data:{'id': '1322', 'requestTime': 1584453397381, 'pf': 'h5'}, url: https://www.tao-ba.club/idols/detail
response.content -> byte type
"""


def getInfo(id):
    url = "https://www.tao-ba.club/idols/detail"
    data = '{{"id": "{}", "requestTime": {}, "pf": "h5"}}'.format(id, int(time.time() * 1000))
    data = encodeData(data)
    response = requests.post(url=url, headers=header, data=data, cookies=cookie)
    response = decodeData(response.text)
    # res+=response['datas']['title']+str(response['datas']['sellstats'])+str(response['datas']['donation'])
    res = response['datas']['title'] + " 当前集资金额：¥" + str(response['datas']['donation']) + "\n"
    return res


"""
join:{'ismore': False, 'limit': 15, 'id': '1322', 'offset': 0, 'requestTime': 1584457188679, 'pf': 'h5'}
url: https://www.tao-ba.club/idols/join
page: limit num in per page
"""
page = 20
total = {}  # user id->money
dic = {}  # user info

def getList(id, page):
    url = "https://www.tao-ba.club/idols/join"
    base = '{{"ismore":{},"limit":{},"id":"{}","offset":{},"requestTime":{},"pf":"h5"}}'
    flag = False
    offset = 0
    while True:
        if flag:
            f = "true"
        else:
            f = "false"
        data = encodeData(base.format(f, page, id, offset, int(time.time() * 1000)))
        response = decodeData(requests.post(url=url, headers=header, data=data).text)["list"]
        for x in response:
            dic[x['userid']] = [x['id'], x['money'], x['nick'], x['stime']]
        flag = len(response) == 15
        offset += page
        if flag == False:
            break
    return dic


def process(dic,last):
    print(dic)
    print(last)
    text=""
    for x in dic.keys():
        if x not in last.keys():
            text+="感谢"+dic[x][2]+"支持¥"+str(dic[x][1])+"元！\n"
        elif dic[x][1]>last[x][1]:
            text+="感谢"+dic[x][2]+"支持¥"+str(dic[x][1]-last[x][1])+"元！\n"
    print(text)
    return text


if __name__ == '__main__':
    res = getInfo(1322)
    print(res)
    last={}
    while 1:
        dic=getList(1322,15)
        process(dic,last)
        last=dic
        time.sleep(60)


