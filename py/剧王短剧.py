# coding=utf-8
# !/usr/bin/python
"""
作者 丢丢喵推荐 🚓 内容均从互联网收集而来 仅供交流学习使用 版权归原创者所有 如侵犯了您的权益 请通知作者 将及时删除侵权内容
                    ====================Diudiumiao====================
"""
from base.spider import Spider
from bs4 import BeautifulSoup
import requests
import re
import sys
sys.path.append('..')

class Spider(Spider):
    def __init__(self):
        self.xurl = "https://djw1.com"
        self.headerx = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
        }

    def getName(self):
        return "首页"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def extract_middle_text(self, text, start_str, end_str, pl, start_index1: str = '', end_index2: str = ''):
        if pl == 3:
            plx = []
            while True:
                start_index = text.find(start_str)
                if start_index == -1:
                    break
                end_index = text.find(end_str, start_index + len(start_str))
                if end_index == -1:
                    break
                middle_text = text[start_index + len(start_str):end_index]
                plx.append(middle_text)
                text = text.replace(start_str + middle_text + end_str, '')
            if len(plx) > 0:
                purl = ''
                for i in range(len(plx)):
                    matches = re.findall(start_index1, plx[i])
                    output = ""
                    for match in matches:
                        match3 = re.search(r'(?:^|[^0-9])(\d+)(?:[^0-9]|$)', match[1])
                        if match3:
                            number = match3.group(1)
                        else:
                            number = 0
                        if 'http' not in match[0]:
                            output += f"#{match[1]}${number}{self.xurl}{match[0]}"
                        else:
                            output += f"#{match[1]}${number}{match[0]}"
                    output = output[1:]
                    purl = purl + output + "$$$"
                purl = purl[:-3]
                return purl
            else:
                return ""
        else:
            start_index = text.find(start_str)
            if start_index == -1:
                return ""
            end_index = text.find(end_str, start_index + len(start_str))
            if end_index == -1:
                return ""
        if pl == 0:
            middle_text = text[start_index + len(start_str):end_index]
            return middle_text.replace("\\", "")
        if pl == 1:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                jg = ' '.join(matches)
                return jg
        if pl == 2:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                new_list = [f'{item}' for item in matches]
                jg = '$$$'.join(new_list)
                return jg

    def homeContent(self, filter):
        result = {"class": []}
        try:
            detail = requests.get(url=self.xurl + "/all/", headers=self.headerx, timeout=10)
            detail.encoding = "utf-8"
            res = detail.text
            doc = BeautifulSoup(res, "lxml")
            soups = doc.find_all('section', class_="container items")
            for soup in soups:
                vods = soup.find_all('li')
                for vod in vods:
                    a_tag = vod.find('a')
                    if not a_tag:
                        continue
                    href = a_tag.get('href')
                    name = vod.text.strip()
                    if href:
                        result["class"].append({"type_id": href, "type_name": name})
        except Exception as e:
            print("homeContent error:", e)
        return result

    def homeVideoContent(self):
        # 修复：不要pass，返回空列表，防止源异常
        return {'list': []}

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []
        try:
            if pg:
                page = int(pg)
            else:
                page = 1
            url = f'{cid}page/{str(page)}/'
            detail = requests.get(url=url, headers=self.headerx, timeout=10)
            detail.encoding = "utf-8"
            res = detail.text
            doc = BeautifulSoup(res, "lxml")
            soups = doc.find_all('section', class_="container items")
            for soup in soups:
                vods = soup.find_all('li')
                for vod in vods:
                    img = vod.find('img')
                    ids = vod.find('a', class_="image-line")
                    if not img or not ids:
                        continue
                    name = img.get('alt','')
                    id = ids.get('href','')
                    pic = img.get('src','')
                    remark = self.extract_middle_text(str(vod), 'class="remarks light">', '<', 0)
                    video = {
                        "vod_id": id,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks": '▶️' + remark
                    }
                    videos.append(video)
        except Exception as e:
            print("categoryContent error:", e)
        result = {'list': videos}
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        did = ids[0]
        result = {}
        videos = []
        xianlu = ''
        bofang = ''
        try:
            if 'http' not in did:
                did = self.xurl + did
            res = requests.get(url=did, headers=self.headerx, timeout=10)
            res.encoding = "utf-8"
            html = res.text
            doc = BeautifulSoup(html, "lxml")
            url = 'https://fs-im-kefu.7moor-fs1.com/ly/4d2c3f00-7d4c-11e5-af15-41bf63ae4ea0/1732707176882/jiduo.txt'
            try:
                response = requests.get(url, timeout=10)
                response.encoding = 'utf-8'
                code = response.text
            except:
                code = ""
            name = self.extract_middle_text(code, "s1='", "'", 0)
            Jumps = self.extract_middle_text(code, "s2='", "'", 0)
            content = '集多为您介绍剧情📢' + self.extract_middle_text(html,'class="info-detail">','<', 0)
            remarks = self.extract_middle_text(html, 'class="info-mark">', '<', 0)
            year = self.extract_middle_text(html, 'class="info-addtime">', '<', 0)
            if name not in content:
                bofang = Jumps
                xianlu = '1'
            else:
                soups = doc.find('div', class_="ep-list-items")
                if soups:
                    soup = soups.find_all('a')
                    for sou in soup:
                        ep_href = sou.get('href','')
                        ep_name = sou.text.strip()
                        bofang = bofang + ep_name + '$' + ep_href + '#'
                    if bofang.endswith('#'):
                        bofang = bofang[:-1]
                    xianlu = '专线'
            videos.append({
                "vod_id": did,
                "vod_remarks": remarks,
                "vod_year": year,
                "vod_content": content,
                "vod_play_from": xianlu,
                "vod_play_url": bofang
            })
        except Exception as e:
            print("detailContent error:", e)
        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        try:
            res = requests.get(url=id, headers=self.headerx, timeout=10)
            res.encoding = "utf-8"
            html = res.text
            url = self.extract_middle_text(html, '"wwm3u8":"', '"', 0).replace('\\', '')
            result["parse"] = 0
            result["playUrl"] = ''
            result["url"] = url
            result["header"] = self.headerx
        except Exception as e:
            print("playerContent error:", e)
        return result

    def searchContentPage(self, key, quick, pg):
        result = {}
        videos = []
        try:
            if pg:
                page = int(pg)
            else:
                page = 1
            url = f'{self.xurl}/search/{key}/page/{str(page)}/'
            detail = requests.get(url=url, headers=self.headerx, timeout=10)
            detail.encoding = "utf-8"
            res = detail.text
            doc = BeautifulSoup(res, "lxml")
            soups = doc.find_all('section', class_="container items")
            for soup in soups:
                vods = soup.find_all('li')
                for vod in vods:
                    img = vod.find('img')
                    ids = vod.find('a', class_="image-line")
                    if not img or not ids:
                        continue
                    name = img.get('alt','')
                    id = ids.get('href','')
                    pic = img.get('src','')
                    remark = self.extract_middle_text(str(vod), 'class="remarks light">', '<', 0)
                    video = {
                        "vod_id": id,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks": '▶️' + remark
                    }
                    videos.append(video)
        except Exception as e:
            print("searchContentPage error:", e)
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def searchContent(self, key, quick, pg="1"):
        # 修复搜索翻页
        return self.searchContentPage(key, quick, pg)

    def localProxy(self, params):
        # 不需要代理直接返回None，避免找不到方法报错
        return None
