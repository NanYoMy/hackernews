# -*- coding: utf-8 -*-
import hashlib, urllib, urllib2, re, time, json
import cookielib,string
import xml.etree.ElementTree as ET
from flask import Flask, request, render_template
import MySQLdb
from hackernews import HackerNews
import sae.const
import pylibmc
import datetime
import sys
import logging
tmp=""
reload(sys)
sys.setdefaultencoding('utf-8')
app = Flask(__name__)
app.debug =True
HELP_INFO = \
u"""
你好我是大喜，欢迎使用骇客头条^_^，回复任何内容，我们会给您提供实时骇客头条新闻，每小时都更新。
"""
#回复文本消息
TEXT_MSG_TPL = \
u"""
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
<FuncFlag>0</FuncFlag>
</xml>
"""
#回复图文消息
NEWS_MSG_HEADER_TPL = \
u"""
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<Content><![CDATA[]]></Content>
<ArticleCount>%d</ArticleCount>
<Articles>
"""

NEWS_MSG_TAIL = \
u"""
</Articles>
<FuncFlag>1</FuncFlag>
</xml>
"""
NEWS_MSG_ITEM_TPL = \
u"""
<item>
    <Title><![CDATA[%s]]></Title>
    <Description><![CDATA[%s]]></Description>
    <PicUrl><![CDATA[%s]]></PicUrl>
    <Url><![CDATA[%s]]></Url>
</item>
"""
#initial the log handle
'''
logLevel=logging.DEBUG
logFormat=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fileHandler=logging.FileHandler('hacknews.log')
stdHandler=logging.StreamHandler(sys.stderr)

fileHandler.setFormatter(logFormat)
stdHandler.setFormatter(logFormat)

logging.getLogger('FileLog').setLevel(logLevel)
logging.getLogger('StdLog').setLevel(logLevel)

logging.getLogger('FileLog').addHandler(fileHandler)
logging.getLogger('StdLog').addHandler(stdHandler)

#FL=logging.getLogger('FileLog')
SL=logging.getLogger('StdLog')
'''
#定时更新数据库
@app.route('/updateHackerNews',methods=['GET','POST'])
def updateHackerNews():
    sql = 'truncate discussion'
    database_execute(sql)
    hn = HackerNews()
    id=1
    stories=hn.top_stories(limit=30)
    for story_id in stories:
        item=hn.get_item(story_id)
        id=story_id
        url="https://news.ycombinator.com/item?id="+str(story_id)
        title=item.title.replace("'","")
        score=item.score
        sql = "insert into discussion values('%s','%s','%s','%s')"%(id,title,url,score)
        #FL.debug(sql)
        database_execute(sql)
    return "success"

@app.route('/')
def home():
    '''
    sql = 'create table discussion(id int primary key , title varchar(1024),url varchar(1024),score varchar(1024) )'
    database_execute(sql)
    sql = 'create table topic(id int primary key , title varchar(1024),url varchar(1024),score varchar(1024))'
    database_execute(sql)
    '''

    return render_template('index.html')

#接受微信消息
@app.route('/', methods=['POST'])
def weixin_msg():


    if verification(request):
        data = request.data
        msg = parse_msg(data)
        if user_subscribe_event(msg):
            return help_info(msg)
        elif is_text_msg(msg):
            content = msg['Content']
            if content == u'?':
                return help_info(msg)
            else:
                return getDiscussion(msg,'骇客头条')
        else:
            pass
    return "failed"

def verification(request):
    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    token = '1234' #注意要与微信公众帐号平台上填写一致
    tmplist = [token, timestamp, nonce]
    tmplist.sort()
    tmpstr = ''.join(tmplist)
    hashstr = hashlib.sha1(tmpstr).hexdigest()
    if hashstr == signature:
        return True
    return False

#消息解析
def parse_msg(rawmsgstr):
    root = ET.fromstring(rawmsgstr)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg

def is_text_msg(msg):
    return msg['MsgType'] == 'text'

def user_subscribe_event(msg):
    return msg['MsgType'] == 'event' and msg['Event'] == 'subscribe'

#数据库连接
def database_execute(sql):
    try:
        conn=MySQLdb.connect(host=sae.const.MYSQL_HOST,user=sae.const.MYSQL_USER,passwd=sae.const.MYSQL_PASS,db =sae.const.MYSQL_DB,port=int(sae.const.MYSQL_PORT),charset="utf8")
        conn.select_db(sae.const.MYSQL_DB)
        cur=conn.cursor()
        cur.execute('SET NAMES utf8;')
        cur.execute('SET CHARACTER SET utf8;')
        cur.execute('SET character_set_connection=utf8;')
        cur.execute(sql)
        result = cur.fetchall()
        #这里一定要commit
        conn.commit()
        cur.close()
        conn.close()
        return result
    except MySQLdb.Error,e:
        print 'mysql error %d:%s'%(e.args[0],e.args[1])
def help_info(msg):
    return response_text_msg(msg, HELP_INFO)

def response_text_msg(msg, content):
    s = TEXT_MSG_TPL % (msg['FromUserName'], msg['ToUserName'],str(int(time.time())), content)
    return s
def response_news_msg(recvmsg, result, label):
    msgHeader = NEWS_MSG_HEADER_TPL % (recvmsg['FromUserName'], recvmsg['ToUserName'],str(int(time.time())), len(result))
    msg = ''
    msg += msgHeader
    msg += make_top(label)
    msg += make_items(result)
    msg += NEWS_MSG_TAIL
    return msg
def make_top(label):
    msg = ''
    title = label
    description = ''
    Url = 'https://news.ycombinator.com/'
    picUrl = 'http://weihacker.sinaapp.com/static/top.png'
    msg += NEWS_MSG_ITEM_TPL %(title,description,picUrl,Url)
    return msg

def make_items(result):
    msg = ''
    for record in result:
        title =record[1]
        description = record[3]
        Url = record[2]
        picUrl = 'http://weihacker.sinaapp.com/static/y.png'
        msg += NEWS_MSG_ITEM_TPL %(title,description,picUrl,Url)
    return msg

def getDiscussion(recvmsg,label):
    sql = 'select * from discussion order by score desc limit 0,9;'
    result = database_execute(sql)
    msgHeader = NEWS_MSG_HEADER_TPL % (recvmsg['FromUserName'], recvmsg['ToUserName'],str(int(time.time())), len(result))
    msg = ''
    msg += msgHeader
    msg += getDiscussionTop(label)
    #这里有问题
    msg += getDiscussionItem(result)
    msg += NEWS_MSG_TAIL
    return msg

def getDiscussionTop(label):
    msg = ''
    title = label
    description = ''
    Url = 'https://news.ycombinator.com/'
    picUrl = 'http://weihacker.sinaapp.com/static/top.jpg'
    msg +=NEWS_MSG_ITEM_TPL %(title,description,picUrl,Url)
    return msg

def getDiscussionItem(result):
    msg = ''
    for record in result:
        '''
        title = record[1]
        #这里字符转换有问题
        description = "score"+str(record[3])
        Url = record[2]
        '''
        title = record[1]
        #这里字符转换有问题
        description = "score:"+record[3]
        Url =record[2]
        picUrl = 'http://weihacker.sinaapp.com/static/y.jpg'
        msg += NEWS_MSG_ITEM_TPL %(title,description,picUrl,Url)
    return msg

if __name__ == '__main__':
    app.run()
