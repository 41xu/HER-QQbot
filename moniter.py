import requests
import json
import time
from cqhttp import CQHttp
from apscheduler.schedulers.blocking import BlockingScheduler

url = "https://groupaccount.tenpay.com/fcgi-bin/grp_commentlist_query.fcgi"

headers = {
    "Host": 'groupaccount.tenpay.com',
    "user-agent":
        "自己填一个你的用户代理，可以加代理池和IP池防止被ban但是我懒得加也没有那么多手机的用户代理可以用，暂时来讲问题不大"
    ,
    "Accept": '*/*',
    'refer':
        "https://servicewechat.com/wxcf8e5b328359cb7a/194/page-frame.html",
    'Accept-Language': 'zh-ch',
}
cookies = {
    'grp_qluin': '填入你的cookie',
    'grp_qlskey': '填入你的cookie',
}
# 使用cookies登陆，不登陆无法查看粉丝圈（所以还得先用这个账号手动加入粉丝圈）咱也不知道这个cookies的过期时间是多少...
data = {
    'guid': '填入目标集资项目的guid',  # 指向这个集资项目的集资情况页面
    'offset': '0',
    'limit': '10',  # response 的集资金额条数，limit可修改，默认10条
    'flag': '0',
}
u = "https://groupaccount.tenpay.com/fcgi-bin/grp_project_qry_info.fcgi"
datatotal = {
    "project_id": "填入集资项目的主页的project_id",
}


def timechange(t):
    stamp = time.mktime(time.strptime(t, '%Y-%m-%d %H:%M:%S'))
    return int(stamp)


def curent(u, headers, cookies, datatotal):
    response = requests.post(url=u, headers=headers, cookies=cookies, data=datatotal, verify=False)
    content = response.content
    result = json.loads(content)
    # print(result)
    cur = {
        "total_amount": result['total_amount'][:-2] + "." + result['total_amount'][-2:],
        "percent": result['percent'],
        "target_amount": result['target_amount'][:-2] + "." + result['target_amount'][-2:],
    }
    return cur


def moniter(url, headers, cookies, data, lasttime):
    response = requests.post(url=url, headers=headers, cookies=cookies, data=data, verify=False)
    try:
        content = response.content
        queue = []

        results = json.loads(content)

        if timechange(lasttime) < timechange(results['list_json'][0]['create_time']):
            # 有人集资啦！更新上次集资时间再更新一下要播报出去的集资情况！
            for x in results['list_json']:
                if timechange(x['create_time']) > timechange(lasttime):
                    queue.append({
                        'nickname': x['nickname'],
                        'creagte_time': x['create_time'],
                        'msg_content': x['msg_content'],
                    })

            lasttime = results['list_json'][0]['create_time']
        return queue, lasttime
    except:
        return [], lasttime


def broadcast(queue, cur):
    res = ""
    if queue == []:
        return res
    for x in queue:
        res = res + "感谢: " + x['nickname'] + " " + x['msg_content'] + "\n"
    res += "当前金额： " + cur['total_amount'] + " 目前的集资进度已达： " + cur['percent'] + "%\n"
    res += "目标金额： " + cur['target_amount'] + " 大家请多多支持茹茹的B50吧！"

    return res


def block():
    global lasttime
    queue, lasttime = moniter(url, headers, cookies, data, lasttime)
    cur = curent(u, headers, cookies, datatotal)
    message = broadcast(queue, cur)
    if queue != []:
        bot.send_group_msg(group_id=477218146, message=message) # BEJ-48 黄恩茹应援群：477218146！欢迎加入！👏🏻
        # group_id填上想要播报的应援群群号，挂在在酷Q上的机器人一定要先加群
        # 如果想播报给个人可以send_private_msg 更多用法参见CoolQHTTP的官网API说明

if __name__ == '__main__':
    lasttime = '2019-09-06 12:30:00'  # initial lasttime 
    bot = CQHttp(api_root='http://127.0.0.1:5700/', access_token='lovely|teemo', secret='lovely|teemo')
    second = 60  # 60s扫一次集资情况
    # second=3600*2 # 2h扫一次
    schedule = BlockingScheduler()
    schedule.add_job(block, 'interval', seconds=second)
    schedule.start()

#    queue,lasttime=moniter(url,headers,cookies,data,lasttime) # initial queue,lasttime
#    cur=curent(u,headers,cookies,datatotal)
#    message=broadcast(queue,cur)
#    print(message)
