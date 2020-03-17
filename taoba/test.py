import requests
import zlib
import json
import base64
import time


def AddSalt(ori: bytearray):
    # 从网页JS当中提取到的混淆盐值，每隔一位做一次异或运算
    Salt = '%#54$^%&SDF^A*52#@7'
    i = 0
    for ch in ori:
        if i % 2 == 0:
            ch = ch ^ ord(Salt[(i // 2) % len(Salt)])
        ori[i] = ch
        i += 1
    return ori


def EncodeData(ori: str):
    # 开头的数字是原始报文长度
    Length = len(ori)
    Message = str.encode(ori)
    # 首先用zlib进行压缩
    Compressed = bytearray(zlib.compress(Message))
    # 然后加盐混淆
    Salted = AddSalt(Compressed)
    # 最后将结果转化为base64编码
    Result = base64.b64encode(Salted).decode('utf-8')
    # 将长度头和base64编码的报文组合起来
    return str(Length) + '$' + Result


def DecodeData(ori: str):
    # 分离报文长度头
    # TODO: 增加报文头长度的验证
    Source = ori.split('$')[1]
    # base64解码
    B64back = bytearray(base64.b64decode(Source))
    # 重新进行加盐计算，恢复原始结果
    Decompressed = AddSalt(B64back)
    # zlib解压
    Result = zlib.decompress(Decompressed).decode('utf-8')
    # 提取json
    return json.loads(Result)


def SendRequest(url: str, data: str):
    Headers = {
        'Content-Type': 'application/json',
        'Origin': 'https://www.tao-ba.club',
        'Cookie': 'l10n=zh-cn',
        'Accept-Language': 'zh-cn',
        'Host': 'www.tao-ba.club',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15',
        'Referer': 'https://www.tao-ba.club/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    Data = EncodeData(data)
    Res = requests.post(url=url, data=Data, headers=Headers)
    ResText = Res.text
    print(DecodeData(ResText))
    return DecodeData(ResText)


def GetDetail(pro_id: int):
    # 获得项目基本信息
    Data ="{{'id': '{}','requestTime': {},'pf': 'h5''}}".format(pro_id, int(time.time() * 1000))
    # Data="{{'ismore': True, 'limit': 15, 'id': '{}', 'offset': 45, 'requestTime': {}, 'pf': 'h5'}}".format(pro_id, int(time.time() * 1000))
    Response = SendRequest('https://www.tao-ba.club/idols/detail', Data)
    print(Response)


def GetPurchaseList(pro_id: int):
    # 获得所有人购买的数据，以list形式返回
    Data = '{{"ismore":False,"limit":15,"id":"{}","offset":0,"requestTime":{},"pf":"h5"}}'.format(pro_id, int(
        time.time() * 1000))
    Response = SendRequest('https://www.tao-ba.club/idols/join', Data)
    Founderlist = []
    Cleared = False
    pages = 0
    while not Cleared:
        if len(Response['list']) == 15:
            pages += 1
            Data = '{{"ismore":True,"limit":15,"id":"{}","offset":{},"requestTime":{},"pf":"h5"}}'.format(pro_id,
                                                                                                             int(
                                                                                                                 time.time() * 1000),
                                                                                                             pages * 15)
            Response = SendRequest('https://www.tao-ba.club/idols/join', Data)
        else:
            Cleared = True
    return Founderlist

if __name__ =='__main__':
    # """
    # post内容
    # 站子的id:10049468
    # url=https://www.tao-ba.club/idols/index/station
    # """
    # test=DecodeData("59$XZyIVh8tei3uTA+ydzISMGOxcDH1UIxRa0oHLHgtHAnqzA1VhTIRtRMxB7UAtJA0abf1UQxIUKqJMBOqWwC/1zpF")
    # print(test)
    # test=DecodeData("105$XZwujHQK9zAoBKGyQh1C112Jm5FJFHQTAEw4ywyU4L9ktyWG7h/x2vIFkL5DE+ZR9cllYeSuHn3BiTbdjL9pAMs23PpDzL+WdM2zLottj9rJJtA54bwa5jVeorMptSH8WcziHpk=")
    # print(test)
    test=DecodeData("88$XZw2y/4NtCA0RY9e+3owgN8hkGFPDi8SSMpNZdld7p7/+wBbGVU1ez5CDTVfR5BMjh00dlcO15IWk69+JJU6SMGbU/nx4B4bo1YsDMRK0Dkt7zOo8RkP")
    print(test)
    response=GetDetail(1322)
