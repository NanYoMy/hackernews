# -*- coding: utf-8 -*- 
import hashlib, urllib, urllib2, re, time, json
import cookielib,string
import xml.etree.ElementTree as ET
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8') 


def makeURL(startPosition):
    front='http://movie.douban.com/top250?start='
    end='&filter=&format='
    return front+str(startPosition)+end

def downloadBestMovie(opener):
    sql = 'truncate bestMovie'
    print sql

    for i in range(0,10):
       url=makeURL(i*25)
       downloadOnePageBestMovie(url,opener,i*25)

def downloadOnePageBestMovie(web,opener,shift):
    #访问网页
    raw_html =opener.open(web).read()
    #print raw_html
    
    divClass1=re.compile(r'(<div class="grid-16-8 clearfix">)(.+?)(</div>)',re.DOTALL)

    titleAndurlAndImage=re.compile(r'(<a href=")(.+?)("><img alt=")(.+?)(" src=")(.+?)("></a>)')
    
    i=shift
    imageDatabase=""
    titleDatabase=""
    urlDatabase=""  
    
    for titleAndurlAndImageData in titleAndurlAndImage.findall(raw_html):
        urlDatabase=titleAndurlAndImageData[1]
        titleDatabase=titleAndurlAndImageData[3]
        imageDatabase=titleAndurlAndImageData[5]
        sql = "insert into bestMovie values('%s','%s','%s','%s','%s')"%(i,titleDatabase,"",urlDatabase,imageDatabase)
        print sql
        i=i+1
        
            
def downloadBestMovieReview(web,opener):
    
    raw_html =opener.open(web).read()
    ul=re.compile(r'(<ul class="tlst clearfix" style="clear:both">)(.+?)(</ul>)',re.DOTALL)

    urlAndtitle=re.compile(r'(<a title=")(.+?)(" href=")(.+?)(" onclick="moreurl)')
    image=re.compile(r'(<img class="fil" src=")(.+?)(" alt=")')    
    
    sql = 'truncate bestMovieReview'
    print sql

    i=1    
    for source in ul.findall(raw_html,re.MULTILINE):
        result=source[1]

        urlDatabase=""
        titleDatabase=""
        imageDatabase=""
        for urlAndtitleData in urlAndtitle.findall(result,re.MULTILINE):
            titleDatabase=urlAndtitleData[1]
            urlDatabase=urlAndtitleData[3]
        for imageData in image.findall(result,re.MULTILINE):
            imageDatabase=imageData[1]
            
            sql = "insert into bestMovieReview values('%s','%s','%s','%s','%s')"%(i,titleDatabase,"",urlDatabase,imageDatabase)
            print sql
            i=i+1

def downloadLatestMovieReview(web,opener):
    
    raw_html =opener.open(web).read()
    ul=re.compile(r'(<ul class="tlst clearfix" style="clear:both">)(.+?)(</ul>)',re.DOTALL)

    urlAndtitle=re.compile(r'(<a title=")(.+?)(" href=")(.+?)(" onclick="moreurl)')
    image=re.compile(r'(<img class="fil" src=")(.+?)(" alt=")')    
    
    sql = 'truncate latestMovieReview'
    print sql

    i=1    
    for source in ul.findall(raw_html,re.MULTILINE):
        result=source[1]

        urlDatabase=""
        titleDatabase=""
        imageDatabase=""
        for urlAndtitleData in urlAndtitle.findall(result,re.MULTILINE):
            titleDatabase=urlAndtitleData[1]
            urlDatabase=urlAndtitleData[3]
        for imageData in image.findall(result,re.MULTILINE):
            imageDatabase=imageData[1]
            sql = "insert into latestMovieReview values('%s','%s','%s','%s','%s')"%(i,titleDatabase,"",urlDatabase,imageDatabase)
            print sql
            i=i+1


def downloadComingMovie(web,opener):
    #访问网页
    raw_html =opener.open(web).read()
    #print raw_html
    #pattern1 = re.compile(r"(<div class=\"cover\"><a href=\")(.+?)(\"><img src=\")(.+?)(\" /></a></div>)")
    divClass1=re.compile(r'(<div class="item mod ">)(.+?)(</div>)',re.DOTALL)
    divClass2=re.compile(r'(<div class="item mod odd">)(.+?)(</div>)',re.DOTALL)

    urlAndImage=re.compile(r'(<a class="thumb" href=")(.+?)("><img src=")(.+?)(" alt="" /></a>)')
    title=re.compile(r'(<h3><a href=")(.+?)(">)(.+?)(</a><span class="icon">)')    
        
    sql = 'truncate comingMovie'
    print sql

    i=1    
    for source in divClass1.findall(raw_html,re.MULTILINE):
        result=source[1]
        
        urlDatabase=""
        imageDatabase=""
        titleDatabase=""

        for urlImageData in urlAndImage.findall(result):
            
            urlDatabase=urlImageData[1]
            imageDatabase=urlImageData[3]

        for titleData in title.findall(result):
            titleDatabase=titleData[3]
            sql = "insert into comingMovie values('%s','%s','%s','%s','%s')"%(i,titleDatabase,"",urlDatabase,imageDatabase)
            print sql
            i=i+1
        
        
    j=i
    for source in divClass2.findall(raw_html,re.MULTILINE):
        result=source[1]    
        urlDatabase=""
        imageDatabase=""
        titleDatabase=""

        for urlImageData in urlAndImage.findall(result):
            
            urlDatabase=urlImageData[1]
            imageDatabase=urlImageData[3]

        for titleData in title.findall(result):
            titleDatabase=titleData[3]

            sql = "insert into comingMovie values('%s','%s','%s','%s','%s')"%(j,titleDatabase,"",urlDatabase,imageDatabase)
            print sql
            j=j+1
    
def downloadHotestMovie(web,opener):
     #访问网页
    raw_html =opener.open(web).read()
    divClass=re.compile(r'(<ul id="hotplayRegion">)(.+?)(</ul>)',re.DOTALL)
    divRing=re.compile(r'(<div class="i_ringimg" style="margin:0;">)(.+?)(</div>)')
    for source in divClass.findall(raw_html,re.MULTILINE):
        result=source[1]

    conten=re.compile(r'(<a href=")(.+?)(</a>)')
    urlandtitle=re.compile(r'(<a href=")(.+?)(" target="_blank" title=")(.+?)("><img width="96" height="128" src=")(.+?)(" alt=)')

    sql = 'truncate hotestMovie'
    print sql    

    i=1
    for href in divRing.findall(result):
        result1= href[1]
        for data in conten.findall(result1):
            result2=data[0]+data[1]
            for data2  in urlandtitle.findall(result2):
                sql = "insert into hotestMovie values('%s','%s','%s','%s','%s')"%(i,data2[3],"",data2[1],data2[5])
                print sql
                i=i+1

def getOpener():

    try:
        #获得一个cookieJar实例
        cj = cookielib.CookieJar()
        #cookieJar作为参数，获得一个opener的实例
        opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        #伪装成一个正常的浏览器，避免有些web服务器拒绝访问。
        opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]
        return opener
    except Exception,e:
        print str(e)
          
def downloadLatestMovie(web,opener):

    #访问网页
    raw_html =opener.open(web).read()
    #print raw_html
    #pattern1 = re.compile(r"(<div class=\"cover\"><a href=\")(.+?)(\"><img src=\")(.+?)(\" /></a></div>)")
    divClass=re.compile(r"(<ul class=\"showing_list\")(.+?)(</ul>)")
    
    for source in divClass.findall(raw_html):
        result=source[1]
    titleANDurl=re.compile(r'(<div class="item_l"> <p><a href=")(.+?)(/" target="_blank" title=")(.+?)("> <img class="img_box" src=")(.+?)(" width="96" height="128")')
  
    sql = 'truncate lastestMovie'
    print sql
    
    i = 1
    for source in titleANDurl.findall(result):

        value = [i,source[3],'des',source[1],source[5]]
        sql = "insert into lastestMovie values('%s','%s','%s','%s','%s')"%(value[0],value[1],value[2],value[3],value[4])
        print sql
        i = i+1
        
def downloadcinema(web,opener):

    raw_html =opener.open(web).read()
    dd=re.compile(r"(<dd districtid)(.+?)(</dd>)")
    districs=re.compile(r'(<a class=\\")(.+?)(href=\\")(.+?)(\\")(.+?)(title=\\")(.+?)(\\"><img src=\\")(.+?)(\\" alt=)(.+?)(</a>)')

    sql = 'truncate cinema'
    print sql

    i = 1
    for data in dd.findall(raw_html):
        subdata=data[1]
        #print "getdata"
        for source in districs.findall(subdata):
            value = [i,source[7],'des',source[3],source[9]]
            sql = "insert into cinema values('%s','%s','%s','%s','%s')"%(value[0],value[1],value[2],value[3],value[4])
            print sql
            i = i+1

            

def home():

    '''
    sql = 'create table bestMovieReview(id int primary key , title varchar(1024),description varchar(1024),url varchar(1024),img varchar(1024))'
    print sql
    
    sql = 'create table latestMovieReview(id int primary key, title varchar(1024),description varchar(1024),url varchar(1024),img varchar(1024))'
    print sql
    sql = 'create table comingMovie(id int primary key, title varchar(1024),description varchar(1024),url varchar(1024),img varchar(1024))'
    print sql
    sql = 'create table hotestMovie(id int primary key, title varchar(1024),description varchar(1024),url varchar(1024),img varchar(1024))'
    print sql
    sql = 'create table lastestMovie(id int primary key, title varchar(1024),description varchar(1024),url varchar(1024),img varchar(1024))'
    print sql
    sql = 'create table bestMovie(id int primary key, title varchar(1024),description varchar(1024),url varchar(1024),img varchar(1024))'
    print sql
    sql = 'create table cinema (id int primary key, title varchar(1024),description varchar(1024),url varchar(1024),img varchar(1024))'
    print sql
    '''

    '''
    sql = 'select * from bestMovieReview order by rand() limit 0,9'
    result = database_execute(sql)
    message = ''
    for record in result:
        temp = record[3]
        a=temp.decode('UTF-8').encode('GBK')
        temp=a.decode('GBK').encode('UTF-8')
        if len(temp) > 100:
            temp = temp[0:100]
        message =  message + str(len(temp)) + temp + "! "
        #message =  message+record[3]
    '''
    opener = getOpener()
    downloadLatestMovie(r"http://movie.mtime.com/new/",opener)
    downloadHotestMovie(r"http://theater.mtime.com/China_Shanxi_Province_Xian/movie/",opener)
    downloadBestMovieReview(r"http://movie.douban.com/review/best/",opener)
    downloadLatestMovieReview(r"http://movie.douban.com/review/latest/",opener)
    downloadComingMovie(r"http://movie.douban.com/later/xian/",opener)
    downloadBestMovie(opener)
    downloadcinema(r"http://theater.mtime.com/China_Shanxi_Province_Xian/movie/149778/",opener)

home()
