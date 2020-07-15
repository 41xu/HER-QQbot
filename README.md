# SNH48 Group's QQ bot
Some function based on CoolQ bot, for SNH48 Group.
**因目前暂时没有需求，项目暂时不维护了，如有问题欢迎提issue或者pull requests**

> BEJ48-黄恩茹的相关 👏🏾477218146👏🏾欢迎加入黄恩茹应援群！

一些针对SNH48Group写的QQ机器人的几个功能。

func list:

- [x] 腾讯小经费集资播报
- [x] 桃叭监控

## 桃叭监控

见`taoba/getList.py`

实现机器人播报

## moniter.py

绑定了BEJ48-黄恩茹应援群中的酷Q机器人，通过爬取腾讯小经费中的集资信息，进行集资情况的实时播报。使用cookie模拟登陆

## 更新 

restruct中解决了project_id的问题，重构了代码所以只需要输入圈子id 然后就可以爬到圈子里的project_id以及project相关了！

但还是有cookies的问题Orz

> 🤔昨晚别家开了新的项目 于是在手动改project_id的时候在想这个脚本能不能写的再好点..比如说能输入项目名称就绑定好这个项目这样子🤔
>
> 可是小打卡还是啥是根据cookie登陆的也不能输入微信账号密码登录，还要获取cookie才可以进行后续操作..获得cookie还是要开花瓶抓包Orz 而且post的时候得带上project_id不然啥反应都没有Orz...那么要怎么做的交互性好点🤔在大家新开链接的时候可以直接输入名字什么的就绑定好新的project了呢🤔
>
> 以及欢迎大家大家pull requests连上数据库加上总计集资功能再加上抽卡功能🌚

### requirement

environment: python3.6 + 酷Q Air/ Pro 

packages:

- requests

- json

- cqhttp

- apscheduler

其中cqhttp的详细介绍参见[项目的官方说明](https://github.com/richardchien/python-cqhttp)

cqhttp只是起到将爬到的消息转发到机器人中的作用，若使用其他机器人消息发送插件则可更换成对应package.

### get start


#### Spider Part

爬虫部分使用[Charles](https://www.charlesproxy.com/) 使用方法如下：(macOS+iPhone)

1. 电脑端下载好Charles后，将电脑与手机连接到一个局域网中，在电脑上打开软件，并在手机上点击连接上的Wi-Fi，(iphone用户`点击无线局域网->点击连接上的网络->拉到底点击HTTP代理->配置代理->手动`）HTTP代理中填入电脑IP，端口号填写为8888（默认的）

2. 在Charles的菜单栏中点击`Help -> SSL Proxying -> Install Charles Root Certificate` 在添加证书的弹出窗口中选择添加，此时证书被添加到钥匙串中，但还是不信任状态，因此点进电脑上的钥匙串，搜索到Charles Proxy CA，双击，选择始终信任即可。Mac上的配置完毕。

3. 保证手机和电脑连接到一个网络并且手机上设置好代理之后，在Mac上保持Charles的打开状态，iPhone中浏览器中打开网址`https://chls.pro.ssl.`，网页载入后会弹出添加描述文件的窗口，点击允许开始下载。后在手机`设置->关于本机->证书信任设置->找到Charles CA选择信任`即可。手机配置完毕。

4. 接下来要设置SSL代理。在Charles的菜单栏选择`Proxy -> SSL Proxying Settings -> add `进行要爬取网页的host设置。这里可以顺手把Proxy中的`macOS Proxy`关掉，这个走的是本机的代理，为了抓包的时候便于观察关掉没什么大问题。在添加主机和端口时这里选择add后输入的host为`groupaccount.tenpay.com`端口可以不填默认的是443

**注意⚠️**第四步一定要设置不然Charles看不见https的请求只能看见http请求。

设置好后手机进入微信腾讯小打卡的小程序

tbc

> 若想加入用户已集资数量显示功能请自己打开Charles找到排行榜对应URL自行抓取
>
> 若想加入抽卡功能请自己绑定数据库实现
>
> 声明：@41xu 作者我本人暂时不更新也不维护本项目233333

声明：项目基于Apache协议，如有问题作者免责2333如需使用版权在我需要标明出处（可以这么说吧？
