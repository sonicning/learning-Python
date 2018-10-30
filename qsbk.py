# !/usr/bin/env python
# coding:utf-8
import re
import requests
from bs4 import BeautifulSoup


# 糗事百科爬虫类
class QSBK:

    # 初始化方法，定义一些变量
    def __init__(self):
        self.pageIndex = 1
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        # 初始化headers
        self.headers = {'User-Agent': self.user_agent}
        # 存放段子的变量，每一个元素是每一页的段子们
        self.stories = []
        # 存放程序是否继续运行的变量
        self.enable = False
        # 如果需要代理，可以在这里配置
        # self.proxies = {'http': 'http://yourURL:yourPort', 'https': 'http://yourURL:yourPort'}

    # 传入某一页的索引获得页面代码
    def get_page(self, page_index):
        try:
            url = 'http://www.qiushibaike.com/hot/page/' + str(page_index)
            # 构建请求的request
            s = requests.session()
            s.keep_alive = False
            req = requests.get(url, headers=self.headers, proxies=self.proxies)
            html = req.text
            div_bf = BeautifulSoup(html, features="lxml")
            div1 = div_bf.find_all('div', class_='article block untagged mb15 typs_long')
            div2 = div_bf.find_all('div', class_='article block untagged mb15 typs_hot')
            div3 = div_bf.find_all('div', class_='article block untagged mb15 typs_old')
            page_code = div1 + div2 + div3
            return page_code

        except requests.exceptions as e:
            if hasattr(e, "reason"):
                print(u"连接糗事百科失败,错误原因", e.reason)
                return None

    # 传入某一页代码，返回本页带图片或者文字列表
    def get_page_items(self, page_index):
        # 用来存储每页的段子们
        page_stories = []
        page_code = self.get_page(page_index)
        if not page_code:
            print("页面加载失败....")
            return None
        for each in page_code:
            link_div = each.find_all('a', class_='contentHerf')
            url_link = "https://www.qiushibaike.com" + link_div[0].get('href')
            content_div = each.find_all('div', class_='content')
            content = BeautifulSoup(str(content_div[0]), features="lxml").find('span').text.replace('\n', '')
            story = content  # 如果不含有图片，则仅仅显示文字
            thumb = each.find_all('div', class_='thumb')
            if thumb:  # 如果含有图片，则显示文字和图片
                # 只有一个结果，故只取第一个
                pic = re.compile('src=\".*jpg\"|src=\".*jpeg\"').findall(str(thumb[0]))[0]
                pic_url = pic.replace('src=', 'https:').replace('\"', '')
                story = content + "\n" + pic_url
            page_stories.append([url_link, story])
        return page_stories

    # 加载并提取页面的内容，加入到列表中
    def load_page(self):
        # 如果当前未看的页数少于2页，则加载新一页
        if self.enable:
            if len(self.stories) < 2:
                # 获取新一页
                page_stories = self.get_page_items(self.pageIndex)
                # 将该页的段子存放到全局list中
                if page_stories:
                    self.stories.append(page_stories)
                    # 获取完之后页码索引加一，表示下次读取下一页
                    self.pageIndex += 1

    # 调用该方法，每次敲回车打印输出一个段子
    def get_one_story(self, page_stories, page):
        # 遍历一页的段子
        for story in page_stories:
            # 等待用户输入
            user_input = input()
            # 每当输入回车一次，判断一下是否要加载新页面
            self.load_page()
            # 如果输入Q则程序结束
            if user_input == "Q":
                self.enable = False
                return
            print(u"第%d页\t原帖地址:%s\n帖子内容:\n%s\n" % (page, story[0], story[1]))

    # 开始方法
    def start(self):
        print("正在读取糗事百科,按回车查看新段子，Q退出")
        # 使变量为True，程序可以正常运行
        self.enable = True
        # 先加载一页内容
        self.load_page()
        # 局部变量，控制当前读到了第几页
        now_page = 0
        while self.enable:
            if len(self.stories) > 0:
                # 从全局list中获取一页的段子
                page_stories = self.stories[0]
                # 当前读到的页数加一
                now_page += 1
                # 将全局list中第一个元素删除，因为已经取出
                del self.stories[0]
                # 输出该页的段子
                self.get_one_story(page_stories, now_page)


spider = QSBK()
spider.start()
