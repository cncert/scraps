# encoding=utf-8

import re
from urllib import robotparser,error,parse
import time
from datetime import datetime
import queue
import requests
from parse_html import GetContentVideo
from timeout import time_limit


def link_crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, headers=None, user_agent='wswp',
                 proxy=None, num_retries=1,scrape_callback=None):
    """Crawl from the given seed URL following links matched by link_regex
    """
    # the queue of URL's that still need to be crawled
    crawl_queue = queue.deque([seed_url])  #  deque是双向队列，将列表放入这个双向队列后，列表就变成了双向列表
                                           # ，可以从左右同时插入和删除元素，高性能
    # the URL's that have been seen and at what depth
    seen = {seed_url: 0}  # 存放已经遍历过得url和遍历次数
    # track how many URL's have been downloaded
    num_urls = 0
    rp = get_robots(seed_url)
    throttle = Throttle(delay)
    headers = headers or {}
    if user_agent:
        headers['User-agent'] = user_agent

    while crawl_queue:
        url = crawl_queue.pop()
        # check url passes robots.txt restrictions
        if rp.can_fetch(user_agent, url):
            throttle.wait(url)
            html = download(url, headers, proxy=proxy, num_retries=num_retries,scrape_callback=scrape_callback)
            links = []
            depth = seen[url]
            if depth != max_depth:
                # can still crawl further
                if link_regex:
                    # filter for links matching our regular expression
                    links.extend(link for link in get_links(html) if re.match(link_regex, link))

                for link in links:
                    link = normalize(seed_url, link)
                    # check whether already crawled this link
                    if link not in seen:
                        seen[link] = depth + 1 # 如果链接不在已遍历列表里，则深度加1
                        # check link is within same domain
                        if same_domain(seed_url, link):
                            # 检查两个url是否属于同一个域名，如果属于同一个域名则返回true
                            # success! add this new link to queue
                            crawl_queue.append(link)

            # check whether have reached downloaded maximum
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print('Blocked by robots.txt:', url)


class Throttle:
    """
    下载限速
    """
    def __init__(self, delay):
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}  #  存放域名上次访问的时间
        
    def wait(self, url):
        domain = parse.urlparse(url).netloc  # 解析url的域名
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                print('sleep:',url)
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()


def download(url, headers, proxy, num_retries, data=None,scrape_callback=None):
    """下载函数"""

    print('Downloading:', url)
    with open('urls111.txt','a+') as f:
        f.write(url+'\n')
    if proxy:
        response = requests.get(url, data=data, headers=headers,proxies=proxy)  # 请求一个web
                                                                   # 设置代理，如果有代理
    else:
        response = requests.get(url, data=data, headers=headers)  # 请求一个web
    try:
        html = response.text
        code = response.status_code
        print(code)
        if scrape_callback:
            scrape = scrape_callback(response)
            scrape()
            # scrape(response)

    except error.URLError as e:
        print('Download error:', e.reason)
        html = ''
        if hasattr(e, 'code'):
            code = e.code
            if num_retries > 0 and 500 <= code < 600:
                # retry 5XX HTTP errors
                return download(url, headers, proxy, num_retries-1, data,scrape_callback=scrape_callback)  # 如果返回5xx错误，说明是服务器
                                                                              # 错误，重试下载
        else:
            code = None
    return html


def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = parse.urldefrag(link) # remove hash to avoid duplicates
    return parse.urljoin(seed_url, link)


def same_domain(url1, url2):
    """Return True if both URL's belong to same domain
    检查两个url是否是属于同一个域名
    """
    return parse.urlparse(url1).netloc == parse.urlparse(url2).netloc


def get_robots(url):
    """Initialize robots parser for this domain
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(parse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp
        

def get_links(html):
    """Return a list of links from html 
    """
    # a regular expression to extract all links from the webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    # list of all links from the webpage
    return webpage_regex.findall(html)


if __name__ == '__main__':
    url = 'xxx%d'

    @time_limit
    def start(num):
        link_crawler(url % num, '/(video)', delay=0, num_retries=1, max_depth=1,
                     user_agent='GoodMan', scrape_callback=GetContentVideo)
    for num in range(2,100):
        start(num)
