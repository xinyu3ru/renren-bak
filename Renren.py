#!/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'rublog'


import requests
import re
import time
import random
import os
import math

import config
    
class Renren(object):
    def __init__(self):
        self.is_login = 0
        self.params = {'origURL':'http://www.renren.com', 'email':config.EMAIL, 'password':config.PASSWORD}
        self.get_symbol_code = re.compile('&failCode=(\d+)')
        self.user_id = 0
        self.login_url = config.LOGINURL
        self.localtime = time.localtime()
        self.bak_time = time.strftime('%Y-%m-%d  %H:%M:%S', self.localtime)
        self.this_year = self.localtime[0]
        self.cookies = {}
        self.s = requests.Session()
        self.icode_url = config.ICODEURL
        self.rtk = '1000'
        self.requestToken = '1000'
        self.user_name = 'No name!'
        self.tiny_photo_url = 'http://www.renren.com'
####登陆模块使用post来发送账号密码
    def post_data(self, login_url, params):
        header = {
            'Accept': 'text/html, application/xhtml+xml, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Accept-Encoding': 'gzip, deflate',
            'Cache-Control': 'no-cache'
        }
        o = self.s.post(login_url, data = header, params=params)
        return o
###登陆模块，查看是否有登陆验证码
    def login(self):
        while not self.is_login:
            try_login = self.post_data(self.login_url, self.params)
            is_success = re.search('ren\.com/\d+', try_login.url)
            if not is_success:
                symbol_code = self.get_symbol_code.search(try_login.url)
                symbol_code_num = symbol_code.group(1)
                if symbol_code_num == '512':
                    self.i_get_img()
                    img_content = input('打开文件夹查看并输入验证码：')
                    self.params['icode'] = img_content
                    return 0
                os.system('cls')
                print(config.FAILCODE[symbol_code_num])
            else:
                user_page = try_login.url
                #print(user_page)
                self.is_login = 1
                user_id = self.get_user_id(user_page)
                #print(user_id)
                self.user_id = user_id
                user_page = 'http://www.renren.com/'+user_id+'/profile'
                #print(user_page)
                index = self.open_url(user_page)
                #print(index.url)
                #print(index.request.headers)
                #print(index.headers)
                #print(index.content.decode())
                self.rtk = self.get_rtk(index.content.decode())
                #print(self.rtk)
                self.requestToken = self.get_requestToken(index.content.decode())
                self.get_user_tiny_photo_url(index.content.decode())
                self.get_user_name(index.content.decode())
                #print(self.requestToken)
                #return user_id
            #else:
                #symbol_code = self.get_symbol_code.search(try_login.url)
                #symbol_code_num = symbol_code.group(1)
                #print(config.FAILCODE[symbol_code_num])
                #if symbol_code_num == '512':
                #else:
            return 0
###获取登陆验证码
    def i_get_img(self):
        pic_data = self.open_url(self.icode_url)
        #print(pic_data.headers)
        #print(pic_data.request.headers)
        #print(type(pic_data.content))
        with open('icode.jpg', 'wb') as f:
            kk = f.read
            f.write(pic_data.content)
        return 0
###打开普通网页或者有组合数据的网页
    def open_url(self, url, params=0):
        #打开网址并返回解码后的页面（网页源码）
        header = {
            'Accept': 'text/html, application/xhtml+xml, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Accept-Encoding': 'gzip, deflate',
            'Cache-Control': 'no-cache'
        }
        if not params:
            o = self.s.get(url, headers = header)
            #print('直接打开')
        else:
            o = self.s.get(url, params=params, headers=header)
            #print('组合网址了')
        #o_content_decode = o.content.decode()
        #print(o.text)
        #print(o.url)
        #print(o.headers)
        #print(o.content)
        #print(o)
        return o#.text
###获取个人首页
    def get_user_page(self, shouye):
        user_page = re.findall('http://www.renren.com/\d*/profile', shouye)
        return user_page
    def get_user_tiny_photo_url(self, shouye):
        tiny_photo_url = re.findall('src="(http:[\w/\.\-_/]{10,200}\.[gbjp][gifbmpnje]{1,2}[fgp])"\s+id="userpic', shouye)
        #print(tiny_photo_url)
        if tiny_photo_url:
            self.tiny_photo_url = tiny_photo_url[0]
            return tiny_photo_url[0]
        return 1000
    def get_user_name(self, shouye):
        user_name = re.findall('name\s:\s"([\s\S]*?)"', shouye)
        if user_name:
            self.user_name = user_name[0]
            return user_name[0]
        return 1000    
###获取个人的人人id
    def get_user_id(self, user_page):
        user_id = re.findall('\d+', user_page)
        return user_id[0]
    def get_requestToken(self, shouye):
        find_requestToken = re.findall("requestToken\s:\s'(-*\d+)'", shouye)
        if find_requestToken:
            requestToken = find_requestToken[0]
            return requestToken
        else:
            return 1000
    def get_rtk(self, shouye):
        find_rtk = re.findall("_rtk\s:\s'(\w+)'", shouye)
        if find_rtk:
            rtk = find_rtk[0]
            return rtk
        else:
            return 1000

####在每个月的页面上截取每个微博的那段源代码
    def get_detailpage_in_monthly_page(self, monthly_page):
        detailpage_in_monthly_page = re.findall('<section id="newsfeed[\s|\S]+?</section>', monthly_page)
        return detailpage_in_monthly_page
###如果一条微博获取正常就进行保存一次，到html中
    def save_every_weibo(self, detailpage_list, file_name):
        for detailpage in detailpage_list:
            weibo_our_keep = self.join_weibo(detailpage)
            if weibo_our_keep == 0:
                continue
            self.save_html(weibo_our_keep, file_name)
        #print('ever been here!')
        return 0
###获取每条微博的发布时间，人人网没具体到时间点，只给到日期
    def get_weibo_time(self, detail_page):
        pre_first_time = re.findall('<input\stype="hidden"\svalue="\d{4}-\d{2}-\d{2}', detail_page)
        first_time = re.findall('\d{4}-\d{2}-\d{2}', pre_first_time[0])
        #print(pre_first_time)
        #print(first_time)    
        return first_time[0]
###获取每条微博的内容
    def get_weibo_content(self, detail_page):
        pre_content = re.findall('<div\sclass="content-main">[\S\s]+?</d', detail_page)
        if len(pre_content) == 0:
            return []
        content_pre = re.findall('>[\s\S]+?</|>[\s\S]+?</', pre_content[0])
        content = content_pre[0].lstrip('>')
        content = content.rstrip('</ d')
        content = re.sub('<a[\S\s]+?>', '', content)
        content = re.sub('http://52ust.com.cn|52ust.com.cn', '', content)
        #print(content)
        #print(pre_content)
        return content
###去除一个字符串中的某些字符
    def get_rid(self, all_string, wipe_string):
        all_string = all_string.lstrip(wipe_string)
        all_string = all_string.rstrip(wipe_string)
        return all_string
###获取每一条回复
    def get_replys(self, detail_page):
        pre_reply = re.findall('"\starget="_blank">[\s|\S]*?</a>:&nbsp;[\s|\S]*?</p>\s*<div\sclass="bottom-bar">\s*<span\sclass="time">\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}</span>', detail_page)
        #print(pre_reply)
        replys = []
        for reply in pre_reply:
            pre_man = re.findall('>[\s|\S]*?</a', reply)
            man = self.get_rid(pre_man[0], '<>/a')
            #print(man)
            pre_reply_content = re.findall('p;[\s|\S]*?</', reply)
            reply_content = self.get_rid(pre_reply_content[0], 'p;</ \n')
            reply_content = re.sub('<a[\S\s]+?>', '', reply_content)
            reply_time = re.findall('\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}', reply)
            full_reply = '    '+man+': '+reply_content+' @'+reply_time[0]
            replys.append(full_reply)
        #print(replys)
        return replys
###组合微博到特定的格式
    def join_weibo(self, detail_page):
        time1 = self.get_weibo_time(detail_page)
        content1 = self.get_weibo_content(detail_page)
        if len(content1) == 0:
            return 0
        reply1 = self.get_replys(detail_page)
        text1 = """<div class="content">
        <div class="time">
            <span>"""
        text2 = """</span>
        </div>
        <div class="weibo">
            <p class="weibo-text">"""
        text3 = """        </p>
        </div>\n"""
        text4 = """    <div class="reply">
            <p class="reply-text">"""
        text5 = """\n        </p>
        </div>\n"""
        text6 = """</div>"""
        weibo_one_html = text1+time1+text2+content1+text3
        for reply in reply1:
            weibo_one_html = weibo_one_html+text4+reply+text5
        weibo = weibo_one_html+text6+'\n'
        weibo = self.repl_img_url(weibo)
        return weibo
###保存特定格式的微博
    def save_html(self, weibo_our_keep, file_name):
        with open(file_name, 'a+', encoding="utf-8") as f:
            f.write(weibo_our_keep)
        return 0
###创建基本的html的头部
    def create_basic_html(self, file_name):
        header = """<html>
    <head>
    <meta name="Description" content="人人网 校内------曾经的一个朋友">
    <meta name="Keywords" content="Xiaonei,Renren,校内,大学,同学,人人,人人网">
    <title>人人网/校内网---曾经的一个朋友</title><meta charset="utf-8">
    </head>
    <body>
    <div class="body-head">
    <li class="daohang-item">
    <h2>人人网/校内网---曾经的一个朋友</h2>
    </li>
    <li class="daohang-item">
    <a href="./index.html">首页</a> | 
    <a href="./shuo.html" target="_blank">微博</a> | 
    <a href="./blog.html" target="_blank">博文</a> | 
    <a href="./album.html" target="_blank">相册</a>
    </li>
    </div>
    <div class="body-main">
    <br>
"""
        with open(file_name, 'w+', encoding="utf-8") as f:
            f.write(header)
            f.close
        return 0
    def create_sub_folder_basic_html(self, file_name):
        header = """<html>
    <head>
    <meta name="Description" content="人人网 校内------曾经的一个朋友">
    <meta name="Keywords" content="Xiaonei,Renren,校内,大学,同学,人人,人人网">
    <title>人人网/校内网---曾经的一个朋友</title><meta charset="utf-8">
    </head>
    <body>
    <div class="body-head">
    <li class="daohang-item">
    <h2>人人网/校内网---曾经的一个朋友</h2>
    </li>
    <li class="daohang-item">
    <a href="../index.html">首页</a> | 
    <a href="../shuo.html" target="_blank">微博</a> | 
    <a href="../blog.html" target="_blank">博文</a> | 
    <a href="../album.html" target="_blank">相册</a>
    </li>
    </div>
    <div class="body-main">
    <br>
"""
        with open(file_name, 'w+', encoding="utf-8") as f:
            f.write(header)
            f.close
        return 0    
    def create_weibo_page_head(self):
        blog_list_title = """    <h3>说说列表</h3>"""
        with open('shuo.html', 'a+', encoding='utf-8') as f:
            f.write(blog_list_title)
        return 0
    
###循环打开所有月份的人人网页
    def all_year_and_month(self):
        self.create_basic_html('shuo.html')
        self.create_weibo_page_head()
        weibo_urls = 'http://www.renren.com/timelinefeedretrieve.do'
        param = {"ownerid":"  ", "render":"0", "begin":"0", "limit":"100", "year":"2012", "month":"1", "isAdmin":"false"}
        #print(self.cookies)
        param['ownerid'] = self.user_id
        for year in range(2016,2007,-1):
            for month in range(12,0,-1):
                param['year'] = year
                param['month'] = month
                detailpage_in_monthly_page = self.open_url(weibo_urls, param)
                #print(detailpage_in_monthly_page.content.url)
                a_month_weibo_list = self.get_detailpage_in_monthly_page(
                                                                        detailpage_in_monthly_page.content.decode())
                #print(a_month_weibo_list)
                self.save_every_weibo(a_month_weibo_list, 'shuo.html')
                time.sleep(random.randint(1, 4))
        self.full_fill_html('shuo.html')
        return 0
    def repl_img_url(self, strings, blog=0):
        #print(strings)
        strings = re.sub('\?ver=\d', '', strings)
        img_url = re.findall('src=["\'](http:[\w/\.\-/]{10,200}\.[gbjp][gifbmpnje]{1,2}[fgp])', strings)
        #print(img_url)
        #print(len(img_url))
        for url in img_url:
            self.download_img(url)
            #print(url)
        if blog:
            strings = re.sub('src="http://[\s\S]+?/', 'src="../pic/', strings)
            strings = re.sub('src=\'http://[\s\S]+?/', 'src=\'../pic/', strings)
        else:
            strings = re.sub('src="http://[\s\S]+?/', 'src="./pic/', strings)
            strings = re.sub('src=\'http://[\s\S]+?/', 'src=\'./pic/', strings)
        strings = re.sub('thumbnail=["\'][\s\S]+?["\']', '', strings)
        return strings
    def download_img(self, img_url):
        if img_url.count('/')<4:
            return 0
        k = img_url.split('/')
        i = 3
        img_name = './pic'
        for x in range(3,len(k)-1):
            img_name = img_name+'/'+k[x]
            #print(img_name)
        if not os.path.exists(img_name):
            os.makedirs(img_name)
            #print(img_name)
        img_name = img_name+'/'+k[-1]
        #print(img_name)
        if os.path.isfile(img_name):
            return 0
        pic_data = self.open_url(img_url)
        with open(img_name, 'wb') as f:
            kk = f.read
            f.write(pic_data.content)
        return 0
    def join_commet(self, commet):
        commet_in_htmls = """        <div class="commet">
        """+commet[2]+': '+commet[0]+' @ '+commet[1]+"""
        </div>
"""
        commet_in_html = self.repl_img_url(commet_in_htmls, 1)
        return commet_in_html
    def get_commet(self, page_id, blog=0):
        param = {"limit":"20", "desc":"true", "offset":"0", "replaceUBBLarge":"true", "type":"blog", "entryId":page_id, "entryOwnerId":self.user_id, "requestToken":self.requestToken, "_rtk":self.rtk}
        commet_url = 'http://comment.renren.com/comment/xoa2'
        if blog:
            param["type"] = 'photo'
        commets_page = self.open_url(commet_url, param)
        commets_page = commets_page.content.decode()
        #print(commets_page)
        patten = 'content":"([\s\S]+?)",[\s\S]+?"time":"([\s\S]+?)"[\s\S]+?authorName":"([\s\S]+?)"'
        commets_list = re.findall(patten, commets_page)
        #print(commets_list)
        commets = ''
        if commets_list:
            for commet in commets_list:
                commets = commets+self.join_commet(commet)
        return commets
    def get_blog_content(self, blog_id):
        while int(blog_id)<99999999:
            blog_id = int(blog_id)*10
        blog_id = str(blog_id)
        blog_url = 'http://blog.renren.com/blog/'+self.user_id+'/'+blog_id
        blog_page = self.open_url(blog_url)
        blog_page = blog_page.content.decode()
        #print(blog_page)
        patten = '<div\sid="blogContent"\sclass="blogDetail-content"[\s\S]+?>([\s\S]+?)</div>'
        blog_content = re.findall(patten, blog_page)
        #print(blog_content)
        if len(blog_content) == 0:
            return 0
        else:
            blog_content = self.repl_img_url(blog_content[0], 1)
            return blog_content
    def save_single_blog_page(self, blog_id, blog_tuple):
        if not os.path.exists('./blog'):
            os.makedirs('./blog')
        file_name = './blog/'+blog_id+'.html'
        self.create_sub_folder_basic_html(file_name)
        blog_content = self.get_blog_content(blog_id)
        commets = self.get_commet(blog_id)
        text1="""        <div class="blog_discribe">
            <h3><a href="./blog/"""+blog_id+""".html">"""+blog_tuple[5]+"""</a></h3>
            </div>
            <div class="blog_discribe">
            发布：20"""+str(blog_tuple[1])+"""    阅读："""+str(blog_tuple[2])+"""    回复："""+str(blog_tuple[3])+"""
            </div>
            <div class="blog_content">"""+str(blog_content)+"""<br>
            <h4>评论、留言</h4>
"""+str(commets)+"""
</div>
            </body>
            </html>"""
        self.save_html(text1, file_name)
        return 0
    def save_a_single_blog(self, a_blog_url):
        if not os.path.exists('./blog'):
            os.makedirs('./blog')
        blog_id = re.findall('blog\.renren\.com/blog/\d+/(\d+)', a_blog_url)
        if blog_id:
            blog_id = blog_id[0]
        else:
            print('请输入正确的博客网址！')
            return 0
        file_name = './blog/'+blog_id+'.html'
        self.create_sub_folder_basic_html(file_name)
        commets = self.get_commet(blog_id)
        blog_tuple = self.get_blog_tuple(blog_id)
        text1="""        <div class="blog_discribe">
            <h3><a href="./blog/"""+blog_id+""".html">"""+blog_tuple[5]+"""</a></h3>
            </div>
            <div class="blog_discribe">
            发布："""+str(blog_tuple[1])+"""    阅读："""+str(blog_tuple[2])+"""    回复："""+str(blog_tuple[3])+"""
            </div>
            <div class="blog_content">"""+str(blog_tuple[0])+"""<br>
            <h4>评论、留言</h4>
"""+str(commets)+"""
</div>
            </body>
            </html>"""
        self.save_html(text1, file_name)
        os.system('cls')
        print('*************************************************************')
        print('   ****已保存人人网这篇博文，请继续保存其他或输入5退出****   ')
        print('*************************************************************')
        print(' ')
        print(' ')
        return 0
    def get_blog_tuple(self, blog_id):
        while int(blog_id)<99999999:
            blog_id = int(blog_id)*10
        blog_id = str(blog_id)
        blog_url = 'http://blog.renren.com/blog/'+self.user_id+'/'+blog_id
        blog_page = self.open_url(blog_url)
        blog_page = blog_page.content.decode()
        #print(blog_page)
        blog_title = re.findall('class="blogDetail-title">([\s\S]+?)<', blog_page)
        blog_time = re.findall('createTime":"(\d+)"', blog_page)
        blog_read_num = re.findall('blogDetail-readerNum-num">(\d+)<', blog_page)
        patten = '<div\sid="blogContent"\sclass="blogDetail-content"[\s\S]+?>([\s\S]+?)</div>'
        blog_content = re.findall(patten, blog_page)
        #print(blog_content)
        blog_tuple = ['none content', '2038-12-31  23:59:59', '0', '0', blog_id, 'fail']
        if len(blog_content) == 0:
            blog_tuple[0] = blog_url+'博文内容未正确获取'
        else:
            blog_tuple[0] = self.repl_img_url(blog_content[0], 1)
        if len(blog_title) == 0:
            fail = blog_url+'未正确获取'
            blog_tuple[5] = fail
        else:
            blog_tuple[5] = blog_title[0]
        if len(blog_time):
            blog_tuple[1] = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(int(blog_time[0])/1000))
        if len(blog_title):
            blog_tuple[2] = blog_read_num[0]
        return blog_tuple
    def join_blog_list(self, blog_tuple):
        if blog_tuple:
            blog_id = re.sub('\.', '', blog_tuple[4])
            self.save_single_blog_page(blog_id, blog_tuple)
            text1="""        <div class="blog_discribe">
            <a href="./blog/"""+blog_id+""".html">"""+blog_tuple[5]+"""</a>
            </div>
            <div class="blog_discribe">
            发布：20"""+blog_tuple[1]+"""    阅读："""+blog_tuple[2]+"""    回复："""+blog_tuple[3]+"""
            </div>
            <div class="blog_summary">"""+blog_tuple[0]+"""</div>
            <br><br>"""
            return text1
        return None
    def get_blog_list_page_num(self):
        blog_start_url = 'http://blog.renren.com/blog/'+str(self.user_id)+'/myBlogs'
        blog_start_page = self.open_url(blog_start_url)
        #print(blog_start_page.content.decode())
        blog_start_page_content_decode = blog_start_page.content.decode()
        all_blog_num = re.findall('itemCount="(\d+)"', blog_start_page_content_decode)
        #print(all_blog_num)
        if all_blog_num:
            all_blog_page_num = int(int(all_blog_num[0])/10)
            #print(all_blog_page_num)
            return all_blog_page_num
        return 0
    def create_blog_list_page_head(self):
        self.create_basic_html('blog.html')
        blog_list_title = """    <h3>博客文章列表</h3>
<br>
"""
        with open('blog.html', 'a+', encoding='utf-8') as f:
            f.write(blog_list_title)
        return 0
    def get_blog_content_list(self, blog_list_url, blog_param):
        blog_list = self.open_url(blog_list_url, blog_param)
        blog_list_content = blog_list.content.decode()
        #print(blog_list_content)
        patten = '"summary":"([\s\S]+?)","createTime":"([\s\S]+?)"[\s\S]+?"readCount":(\d+),[\s\S]+?"commentCount":(\d+),[\s\S]+?"id":([\d\.]+)E8,"title":"([\s\S]+?)"'
        blog_content_list = re.findall(patten, blog_list_content)
        #print(blog_content_list)
        return blog_content_list
    def save_blog_in_a_page(self, blog_content_list):
        blog_in_a_page = ""
        for blog in blog_content_list:
            a_blog = self.join_blog_list(blog)
            blog_in_a_page = blog_in_a_page + a_blog
        #print(blog_in_a_page)
        with open('blog.html', 'a+', encoding='utf-8') as f:
            f.write(blog_in_a_page)
        return 0
    def full_fill_html(self, file_name):
        blog_list_end_html = """    </body>
        </html>"""
        with open(file_name, 'a+', encoding='utf-8') as f:
            f.write(blog_list_end_html)
        return 0
    def all_blogs(self):
        self.create_blog_list_page_head()
        all_blog_page_num = self.get_blog_list_page_num()
        #print(all_blog_page_num)
        blog_list_url = 'http://blog.renren.com/blog/'+str(self.user_id)+'/blogs'
        #print(blog_list_url)
        blog_param = {"categoryId":" ", "curpage":"0", "requestToken":self.requestToken, "_rtk":self.rtk}
        #print(blog_param)
        for page_num in range(0,all_blog_page_num+1):
            blog_param["curpage"] = page_num
            #print(blog_param)
            blog_content_list = self.get_blog_content_list(blog_list_url, blog_param)
            #print(blog_content_list)
            self.save_blog_in_a_page(blog_content_list)
            #blog_list = self.open_url(blog_list_url, params=blog_param)
            #print(blog_list.request.headers)
            #print(blog_list.request.url)
            #print(blog_list.content.decode())
            time.sleep(random.randint(4, 8))
        self.full_fill_html('blog.html')
        return 0
    def create_album_list_page_head(self):
        self.create_basic_html('album.html')
        album_list_title = """    <h3>相册列表</h3>"""
        with open('album.html', 'a+', encoding='utf-8') as f:
            f.write(album_list_title)
        return 0
    def create_album_page_head(self, album_id, album_name):
        if not os.path.exists('./album'):
            os.makedirs('./album')
        self.create_sub_folder_basic_html('./album/album-'+album_id+'.html')
        album_list_title = '    <h3>'+album_name+'</h3>'
        with open('./album/album-'+album_id+'.html', 'a+', encoding='utf-8') as f:
            f.write(album_list_title)
        return 0
    def save_photo_in_html(self, album_id, photo_in_html):
        photo_in_html = self.repl_img_url(photo_in_html, 1)
        with open('./album/album-'+album_id+'.html', 'a+', encoding='utf-8') as f:
            f.write(photo_in_html)
        return 0
    
    def get_album_content_list(self, album_list_url):
        album_content_list_sourse = self.open_url(album_list_url)
        album_content_list_decode = album_content_list_sourse.content.decode()
        album_content_list = re.findall('albumName":"([\s\S]+?)","albumId":"(\d+)"[\s\S]+?photoCount":(\d+),', album_content_list_decode)
        #print(album_content_list)
        return album_content_list
    def get_photo_discribe(self, photo_id):
        photo_url = 'http://photo.renren.com/photo/'+self.user_id+'/photo-'+photo_id+'/v7'
        photo_sourse = self.open_url(photo_url)
        photo_sourse_decode = photo_sourse.content.decode()
        photo_discribe = re.findall('currentPhoto":{"position":\d+?,"originTitle":"([\s\S]*?)",', photo_sourse_decode)
        if photo_discribe:
            photo_discribe = photo_discribe[0]
            #print(photo_discribe)
            if photo_discribe.startswith('\\u'):
                #print(type(photo_discribe))
                photo_discribe = photo_discribe.encode('latin-1').decode('unicode_escape')
                
            return photo_discribe
        return '本图没有标题'
    def save_album(self, album_id, album_name):
        album_url = 'http://photo.renren.com/photo/'+self.user_id+'/album-'+album_id+'/v7'
        #print(album_url)
        album_sourse = self.open_url(album_url)
        album_sourse_decode = album_sourse.content.decode()
        #print(album_sourse_decode)
        photo_in_a_album = re.findall('photoId":"(\d+)"[\s\S]+?createTime\\\\":\\\\"(\d+)\\\\"[\s\S]+?url":"(http:[\\\\\\\\\w/\.-_]{10,200}\.[gbjp][gifbmpnje]{1,2}[fgp])"', album_sourse_decode)
        #print(photo_in_a_album)
        for photo in photo_in_a_album:
            photo_id = photo[0]
            photo_discribe = self.get_photo_discribe(photo_id)
            photo_commets = self.get_commet(photo_id, 1)
            create_time = photo[1]
            l = int(create_time)/1000
            k = time.localtime(l)
            create_time = time.strftime('%Y-%m-%d  %H:%M:%S', k)
            photo_url = photo[2]
            #print(photo_url)
            #print(type(photo_url))
            photo_url = photo_url.replace('\\', '')
            photo_in_html = """        <div class="photo">
        <p><img """+'src="'+photo_url+'" alt="'+photo_discribe+'" /><br><a>'+photo_discribe+"""</a>
        </p>
        </div>
        <br>"""+photo_commets+"""
        <br>
        <br>"""
            self.save_photo_in_html(album_id, photo_in_html)
            self.full_fill_html('./album/album-'+album_id+'.html')
            time.sleep(random.randint(0, 3))
        return 0
    def save_album_list(self, album_content_list):
        album_list_in_html = ""
        if album_content_list:
            for album_name in album_content_list:
                album_name = list(album_name)
                if album_name[0].startswith('\\u'):
                    album_name[0] = album_name[0].encode('latin-1').decode('unicode_escape')
                self.create_album_page_head(album_name[1], album_name[0])
                self.save_album(album_name[1], album_name[0])
                time
                album_list_in_html = album_list_in_html+ """        <div class="album_name">
        <p><a href="./album/album-"""+album_name[1]+""".html">"""+album_name[0]+'</a>     共'+album_name[2]+'张 </p>'+"""
                </div>
        """
        with open('album.html', 'a+', encoding='utf-8') as f:
            f.write(album_list_in_html)
        return 0
    def all_album(self):
        self.create_album_list_page_head()
        album_list_url = 'http://photo.renren.com/photo/'+str(self.user_id)+'/albumlist/v7'
        #print(album_list_url)
        album_content_list = self.get_album_content_list(album_list_url)
        #print(blog_content_list)
        self.save_album_list(album_content_list)
        self.full_fill_html('album.html')
        return 0
    def get_user_account_and_pw(self):
        print("人人网、校内备份脚本write by rublog")
        account_tips = "请输入人人网账号并按回车："
        pw_tips = "请输入人人网密码并回车:"
        account = input(account_tips)
        pw = input(pw_tips)
        self.params['email'] = account
        self.params['password'] = pw
        return 0
    def make_index(self):
        self.create_basic_html('index.html')
        index_content = """
    <h3>"""+self.user_name+'的人人网备份'+"""</h3>
    <div class="index_content">
        <div class="bak_time">
            <span>"""+self.user_name+'备份于'+self.bak_time+"""</span>
        </div>
        <div class="tiny_photo">
            <p class="tiny_photo">
        <img src=\""""+self.tiny_photo_url+"""\" alt=\""""+self.user_name+"""\"  />        </p>
        </div>
    </div>
    <div class="index_content">
    <li class="daohang-item">
    <a href="./index.html">首页</a> | 
    <a href="./shuo.html" target="_blank">微博</a> | 
    <a href="./blog.html" target="_blank">博文</a> | 
    <a href="./album.html" target="_blank">相册</a>
    </li>
    </div>
</body>
</html>"""
        index_content = self.repl_img_url(index_content)
        with open('index.html', 'a+', encoding='utf-8') as f:
            f.write(index_content)
        return 0
if __name__=='__main__':
    tips = """人人网、校内备份脚本 write by rublog
    
因人人网改版及个人精力原因无法保证本脚本一直能
正常使用，本人亦未收取您的任何费用，恕无力保持
脚本能正常使用。

本人保证原版脚本不存在任何上传个人账号行为，请在
本人网站或者本人github上下载使用，其他不做任何
保证。
    """
    print(tips)
    ren = Renren()
    #u_id = ren.login()
    #ren.save_album('1134407597', '用了太多的js')
    #print(ren.tiny_photo_url)
    #print(ren.user_name)
    #ren.make_index()
    #lol = input('stop here!')
    while not ren.is_login:
        ren.get_user_account_and_pw()
        u_id = ren.login()
    ren.make_index()
    os.system('cls')
    choice_tips = """人人网、校内备份脚本 write by rublog

本脚本部分控制网页请求速度但未使用多线程，
人人网说说可能保存有点慢，像是假死，但是它一直在工作。

(0)、备份人人网说说、博客、相册
(1)、备份人人网说说
(2)、备份人人网博客
(3)、备份人人网相册
(4)、备份人人网单篇博客
(5)、退出

请输入选项数字1~5并按回车："""
    #a_month_page = ren.all_year_and_month()
    #上面一行是下载所有的人人说说/微博
    #ren.all_blogs()
    #上面一行是下载所有的人人日志、博客
    #tuple1 = ("不小心脸蛋碰到键盘，在键盘上滚了一会儿","16-02-09 17:37:05","1","0","966057641","god has gone away!")
    #co = ren.save_single_blog_page('966057641', tuple1)
    #上面两行测试保存单片日志
    #co = ren.all_album()
    #print(co)
    end = 1
    while end:
        kk = input(choice_tips)
        print(kk)
        try:
            kk = int(kk)
        except:
            kk = 9
        if kk == 0:
            os.system('cls')
            print('*************************************************************')
            print('   *****正在保存人人网说说、博客和相册，请稍候.......*****   ')
            print('*************************************************************')
            print(' ')
            print(' ')
            a_month_page = ren.all_year_and_month()
            hh = ren.all_blogs()
            co = ren.all_album()
            os.system('cls')
            print('*************************************************************')
            print('   *******已保存人人网说说、博客和相册，请输入5退出*******   ')
            print('*************************************************************')
            print(' ')
            print(' ')        
        elif kk == 1:
            os.system('cls')
            print('***********************************************************')
            print('   **********正在保存人人网说说，请稍候.......**********   ')
            print('***********************************************************')
            print(' ')
            print(' ')
            a_month_page = ren.all_year_and_month()
            os.system('cls')
            print('*************************************************************')
            print('   ******已保存人人网说说，请继续保存其他或输入5退出******   ')
            print('*************************************************************')
            print(' ')
            print(' ')            
        elif kk == 2:
            os.system('cls')
            print('***********************************************************')
            print('   **********正在保存人人网博客，请稍候.......**********   ')
            print('***********************************************************')
            print(' ')
            print(' ')
            hh = ren.all_blogs()
            os.system('cls')
            print('*************************************************************')
            print('   ******已保存人人网博客，请继续保存其他或输入5退出******   ')
            print('*************************************************************')
            print(' ')
            print(' ')            
        elif kk == 3:
            os.system('cls')
            print('***********************************************************')
            print('   **********正在保存人人网相册，请稍候.......**********   ')
            print('***********************************************************')
            print(' ')
            print(' ')
            co = ren.all_album()
            os.system('cls')
            print('*************************************************************')
            print('   ******已保存人人网相册，请继续保存其他或输入5退出******   ')
            print('*************************************************************')
            print(' ')
            print(' ')
        elif kk == 4:
            os.system('cls')
            print('*************************************************************')
            print('   *****正在保存人人网单篇博客，请输入博客网址.......*****   ')
            print('*************************************************************')
            print(' ')
            print(' ')
            a_blog_url = input('请输入博客网址:')
            a_month_page = ren.save_a_single_blog(a_blog_url)
        elif kk == 5:
            print('正在退出，请稍候.......')
            end = 0
        else:
            os.system('cls')
            print('************************************************')
            print('   **********输入有误，请重新输入！**********   ')
            print('************************************************')
            print(' ')
            print(' ')
            continue
        
