import requests
import zlib
import json
import base64
import time
import copy
import random
from cqhttp import CQHttp
from apscheduler.schedulers.blocking import BlockingScheduler


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


# 读取配置文件
def config():
    with open("config.json", 'r', encoding='utf-8') as f:
        conf = json.load(f)
    proj_id = conf['project_id']
    page = conf['page']
    nick = conf['nick']
    text = conf['text']
    target = conf['target']
    return proj_id, page, nick, text, target


def getInfo(id, target):
    url = "https://www.tao-ba.club/idols/detail"
    data = '{{"id": "{}", "requestTime": {}, "pf": "h5"}}'.format(id, int(time.time() * 1000))
    data = encodeData(data)
    response = requests.post(url=url, headers=header, data=data, cookies=cookie)
    response = decodeData(response.text)
    cur_money = response['datas']['donation']
    t = float(cur_money / target * 100)
    res = response['datas']['title'] + " 目前已筹：¥" + str(cur_money) + "，目标金额：¥" + str(target) + "集资进度：" + str(
        '%.2f'% t) + "%\n"
    res += "集资链接：https://www.tao-ba.club/#/pages/idols/detail?id=" + str(id)
    return res, cur_money


page = 15
total = {}  # user id->money
dic = {}  # user info


def getList(id, page):
    url = "https://www.tao-ba.club/idols/join"
    base = '{{"ismore":{},"limit":{},"id":"{}","offset":{},"requestTime":{},"pf":"h5"}}'
    flag = False
    offset = 0
    global dic
    while True:
        if flag:
            f = "true"
        else:
            f = "false"
        data = encodeData(base.format(f, page, id, offset, int(time.time() * 1000)))
        response = decodeData(requests.post(url=url, headers=header, data=data).text)["list"]
        for x in response:
            dic[x['userid']] = [x['id'], float(x['money']), x['nick'], x['stime']]
        flag = len(response) == 15
        offset += page
        if flag == False:
            break
    return dic


def random_callback(text):
    i = random.randint(0, len(text) - 1)
    return text[i]


def process(dic, last, cur_money, nick, text):
    total_number = len(dic)
    ret=[]
    ave = cur_money / total_number
    tmp=str(total_number) + "人参与，人均¥" + str('%.2f' % ave) + "元\n"
    flag = 0
    for x in dic.keys():
        res=""
        if x not in last.keys():
            flag = 1
            res += "感谢 " + dic[x][2] + random_callback(nick) + "支持 ¥" + str(dic[x][1]) + "元！\n"
        elif dic[x][1] > last[x][1]:
            flag = 1
            res += "感谢 " + dic[x][2] + random_callback(nick) + "支持 ¥" + str(dic[x][1] - last[x][1]) + "元！\n"
        else:
            continue
        res += random_callback(text) + "\n"
        res += "【" + dic[x][2] + "】" + "目前支持的总金额为：¥" + str(dic[x][1]) + "元\n"
        res += tmp
        ret.append(res)

    if flag==0:
        ret=[]
    return ret


def block(proj_id, page, target, nick, text):
    dic = getList(proj_id, page)
    try:
        with open('last_data.json', 'r', encoding='utf-8') as f:
            last = json.load(f)
    except:
        last = {}

    info, cur_money = getInfo(proj_id, target)
    res = process(dic, last, cur_money, nick, text)

    if res != []:
        for x in res:
            bot.send_group_msg(group_id=109378220, message=x + info)

    with open('last_data.json', 'w') as f:
        json.dump(dic, f)
        f.write('\n')


if __name__ == '__main__':
    proj_id, page, nick, text, target = config()

    # last={}
    # dic=getList(proj_id,page) # initial dic,last

    bot = CQHttp(api_root='http://127.0.0.1:5700/', access_token='lovely|teemo', secret='lovely|teemo')
    second = 30
    schedule = BlockingScheduler()
    schedule.add_job(block, 'interval', seconds=second, args=[proj_id, page, target, nick, text])
    schedule.start()

    # res = getInfo(1322)
    # print(res)
    # last={}
    # while 1:
    #     dic=getList(1322,15)
    #     process(dic,last)
    #     last=copy.deepcopy(dic)
    #     with open('list_data.json','w') as f:
    #         json.dump(last,f)
    #         f.write('\n')
    #     # 这里注意=即直接赋值是浅拷贝，list这种可变对象拷贝的时候拷贝的是id，所以last和dic实际上是一样的，换成深拷贝就好了
    #     time.sleep(60)
