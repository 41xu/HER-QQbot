import requests
import json
import time

from cqhttp import CQHttp
from apscheduler.schedulers.blocking import BlockingScheduler

headers = {
    "Host": 'groupaccount.tenpay.com',
    "user-agent":
        'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.5(0x17000523) NetType/WIFI Language/zh_CN'
    ,
    "Accept": '*/*',
    'refer':
        "https://servicewechat.com/wxcf8e5b328359cb7a/194/page-frame.html",
    'Accept-Language': 'zh-ch',
}
cookies = {
    "grp_qlskey": "v0ae789cc105d750008677a70385d838",
    "grp_qluin": "c520c10eefc004798d4007a5341e0714"
}

comment_list = "https://groupaccount.tenpay.com/fcgi-bin/grp_commentlist_query.fcgi"
project_qry_info = "https://groupaccount.tenpay.com/fcgi-bin/grp_project_qry_info.fcgi"
group_info = "https://groupaccount.tenpay.com/fcgi-bin/grp_qry_group_info.fcgi"
group_account_id = "FUdRoTfJ0100009000037001"
jujubang="https://groupaccount.tenpay.com/fcgi-bin/grp_qry_pay_ranking.fcgi"

# 这里发现赵粤应援会的圈子ID是: f037001 🤔所以猜测如果其他家要投入使用这个脚本的话 只用该这个group_account_id即可


def timechange(t):
    stamp=time.mktime(time.strptime(t,'%Y-%m-%d %H:%M:%S'))
    return int(stamp)

def getProjectId(group_info, group_account_id):  # 默认选择播报列表中第一个集资链接情况 即最新的集资链接情况
    data = {
        "group_account_id": group_account_id,
    }
    response = requests.post(url=group_info, headers=headers, cookies=cookies, data=data, verify=False)
    content = response.content
    result = json.loads(content)
    balance_array = json.loads(result['balance_array'])
    proj = balance_array[0]  # 默认播报最上面的集资链接
    project_info = {
        "balance": proj["balance"],
        "name": proj["name"],
        "project_id": proj["project_id"],
        "type":proj["type"],
    }
    return project_info


def getProjectsIds(group_info, group_account_id):  # 如果想播报全部的项目..
    data = {
        "group_account_id": group_account_id,
    }
    response = requests.post(url=group_info, headers=headers, cookies=cookies, data=data, verify=False)
    content = response.content
    result = json.loads(content)
    balance_array = json.loads(result['balance_array'])
    projects = []
    for proj in balance_array:
        if "project_id" in proj.keys():
            project = {
                "balance": proj["balance"],
                "name": proj["name"],
                "project_id": proj["project_id"],
                "type":proj["type"],
            }
            projects.append(project)
    return projects


def getProjectInfo(project_info):
    data = project_info
    response = requests.post(url=project_qry_info, headers=headers, cookies=cookies, verify=False, data=data)
    content = response.content
    result = json.loads(content)
    project = {  # current project information
        "name": project_info["name"],
        "total_amount": result['total_amount'][:-2] + "." + result['total_amount'][-2:],
        "percent": result['percent'],
        "target_amount": result['target_amount'][:-2] + "." + result['target_amount'][-2:],
    }
    return project


def getProjectsInfos(projects):
    total_project_info = []
    for data in projects:
        proj = getProjectInfo(data)
        total_project_info.append(proj)
    return total_project_info


def projectInfoBroadcast(project):
    message=""
    pass


def JuJuTop10(project_info):  # 聚聚支持榜前10名
    data={
        "project_id_or_guid":project_info['project_id'],
        "type":project_info['type'],
        "offset":"0",
        "limit":"10", # top 10
    }
    response=requests.post(url=jujubang,headers=headers,cookies=cookies,data=data,verify=False)
    content=response.content
    result=json.loads(content)
    payranking=json.loads(result['payranking_array'])
    accounts=[]
    for account in payranking:
        account_info={
            "amount":account['amount'],
            "nickname":account['nickname'],
            'guid':account['guid'],
            "rank":account['rank'],
            "unionid":account['unionid'],
        }
        accounts.append(account_info)
    return accounts

def JuJuBroadcast(accounts):
    message="目前支持榜前10位的聚聚是：\n"
    for account in accounts:
        message+=str(account['rank'])+".¥"+str(account['amount'])+" "+account['nickname']+"\n"
    message+="非常感谢以上聚聚！!"
    return message

def moniter(project,comment_list,lasttime):
    data={
        "guid":project['project_id'],
        "offset":"0",
        "limit":"10",
        "flag":"1",
    }
    response = requests.post(url=comment_list, headers=headers,cookies=cookies, data=data,verify=False)
    try:
        content = response.content
        queue=[]

        results = json.loads(content)

        if timechange(lasttime)<timechange(results['list_json'][0]['create_time']):
        # 有人集资啦！更新上次集资时间再更新一下要播报出去的集资情况！
            for x in results['list_json']:
                if timechange(x['create_time'])>timechange(lasttime):
                    queue.append({
                        'nickname':x['nickname'],
                        'creagte_time':x['create_time'],
                        'msg_content':x['msg_content'],
                    })

            lasttime=results['list_json'][0]['create_time']
        return queue, lasttime
    except:
        return [],lasttime

def broadcast(queue,cur):
    res=""
    if queue==[]:
        return res
    for x in queue:
        res=res+"感谢: "+x['nickname']+" "+x['msg_content']+"\n"
    res+="当前金额： "+cur['total_amount']+" 目前的集资进度已达： "+cur['percent']+"%\n"
    res+="目标金额： "+cur['target_amount']+" 大家请多多支持赵粤的B50吧！\n"

    return res


def block():
    global lasttime
    project=getProjectId(group_info,group_account_id)
    queue,lasttime=moniter(project,comment_list,lasttime)
    accounts=JuJuTop10(project)
    project_info=getProjectInfo(project)
    message=broadcast(queue,project_info)
    message+=JuJuBroadcast(accounts)
    if queue!=[]:
        bot.send_group_msg(group_id=477218146,message=message)
        bot.send_group_msg(group_id=688346315,message=message)

# if __name__ == '__main__':
#     lasttime='2019-10-04 12:00:00'
#     block()
#     # projects = getProjectsIds(group_info, group_account_id)
#     # total_project_info = getProjectsInfos(projects)
#     # for project in projects:
#     #     accounts=JuJuTop10(project)
#     #     print(JuJuBroadcast(accounts))
if __name__=='__main__':
    lasttime = '2019-10-04 13:30:00' # initial lasttime
    bot = CQHttp(api_root='http://127.0.0.1:5700/',access_token='lovely|teemo',secret='lovely|teemo')
    second=60 # 60s扫一次集资情况
    # second=3600*2 # 2h扫一次
    schedule=BlockingScheduler()
    schedule.add_job(block,'interval',seconds=second)
    schedule.start()