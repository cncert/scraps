# encoding=utf-8
#
#
import requests
import time
from bs4 import BeautifulSoup as bp


class EncodeTransfer:
    def __init__(self):
        pass

    @staticmethod
    def encode_transfer_html(req):
        """转换网页的编码"""
        encode_content = ''
        if req.encoding == 'ISO-8859-1':
            encodings = requests.utils.get_encodings_from_content(req.text)
            if encodings:
                encoding = encodings[0]
            else:
                encoding = req.apparent_encoding
            encode_content = req.content.decode(encoding, 'replace')
        return encode_content

    @staticmethod
    def encode_transfer_str(string):
        """转换字符串的编码"""
        string = string.encode('utf-8').decode()
        return string


class GetContentVideo:
    def __init__(self, req):
        self.req = req
        self.encode_transfer = EncodeTransfer()
        self.ori_content = self.encode_transfer.encode_transfer_html(self.req)
        self.soup = bp(self.ori_content, 'lxml')

    def get_content_video_url(self):
        video_url = ''
        video_content = self.soup.find_all('script')
        for i in video_content:
            text = self.encode_transfer.encode_transfer_str(i.text)
            if 'video' in text:
                try:
                    video = text.split(';')[2].strip()
                    if video.startswith('video'):
                        video_url = video.split('=')[1].replace('[','').replace(']','').replace('"','')
                except Exception as e:
                    pass
                return video_url

    def get_content_video_name(self):
        video_name = ''
        try:
            name_content = self.soup.find(class_='cat_pos_l').text.split('>>')[-1]
            name_content_encode = self.encode_transfer.encode_transfer_str(name_content)
            video_name = name_content_encode.split('  »  ')[-1]
        except Exception as e:
            pass
        return video_name

    def __call__(self):
        video_url = self.get_content_video_url()
        video_name = self.get_content_video_name()
        with open('video_urls.txt', 'a+',encoding='utf8') as fv:
            if video_url:
                fv.write(video_name+':'+video_url+'\n')


def save_url(obj,delay=0.1):
    with open('urls.txt','r') as f,open('video_url.txt','a+') as fv:
        for count, line in enumerate(f, 1):
            url = line.strip()
            time.sleep(delay)
            g = obj(url)
            video_name = g.get_content_video_name()
            video_url= g.get_content_video_url()
            if video_url:
                fv.write(video_name+'   '+video_url+'\n')
            print(count, '  ' + video_name + '  ' + str(video_url))

if __name__ == '__main__':
    save_url(GetContentVideo)



