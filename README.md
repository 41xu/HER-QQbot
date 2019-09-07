# Her-Code
BEJ48-黄恩茹的相关

## moniter.py

绑定了BEJ48-黄恩茹应援群中的酷Q机器人，通过爬取腾讯小打卡中的集资信息，进行集资情况的实时播报。使用cookie模拟登陆

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