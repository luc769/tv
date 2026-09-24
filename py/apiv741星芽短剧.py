# coding = utf-8
# !/usr/bin/python
"""短剧源，影视仓Python爬虫"""
from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
from urllib.parse import unquote
from Crypto.Cipher import ARC4
from urllib.parse import quote
from base.spider import Spider
from Crypto.Cipher import AES
from bs4 import BeautifulSoup
from base64 import b64decode
import requests
import base64
import json
import time
import sys
import re

sys.path.append('..')

class Spider(Spider):
    def __init__(self):
        self.xurl = "https://app.whjzjx.cn"
        self.headers = {
            'User-Agent': 'Linux; Android 12; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.101 Mobile Safari/537.36'
        }
        self.headerf = {
            "platform": "1",
            "user_agent": "Mozilla/5.0 (Linux; Android 9; V1938T Build/PQ3A.190705.08211809; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Safari/537.36",
            "content-type": "application/json; charset=utf-8"
        }
        self.headerx = {}

    def getName(self):
        return "首页"

    def init(self, extend):
        # 移入init：每次源初始化重新登录获取token，解决token过期失效问题
        times = int(time.time() * 1000)
        data = {
            "device": "2a50580e69d38388c94c93605241fb306",
            "package_name": "com.jz.xydj",
            "android_id": "ec1280db12795506",
            "install_first_open": True,
            "first_install_time": 1752505243345,
            "last_update_time": 1752505243345,
            "report_link_url": "",
            "authorization": "",
            "timestamp": times
        }
        plain_text = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        key = "B@ecf920Od8A4df7"
        key_bytes = key.encode('utf-8')
        plain_bytes = plain_text.encode('utf-8')
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        padded_data = pad(plain_bytes, AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        encrypted = base64.b64encode(ciphertext).decode('utf-8')
        try:
            response = requests.post("https://u.shytkjgs.com/user/v3/account/login", headers=self.headerf, data=encrypted, timeout=10)
            response_data = response.json()
            Authorization = response_data['data']['token']
            self.headerx = {
                'authorization': Authorization,
                'platform': '1',
                'version_name': '3.8.3.1'
            }
        except Exception as e:
            print("登录失败：", e)
            self.headerx = {}

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
                        if len(match) < 2:
                            continue
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
        result = {}
        result = {"class": [{"type_id": "1", "type_name": "剧场"},
                            {"type_id": "3", "type_name": "新剧"},
                            {"type_id": "2", "type_name": "热播"},
                            {"type_id": "7", "type_name": "星选"},
                            {"type_id": "5", "type_name": "阳光"}],
                  }
        return result

    def homeVideoContent(self):
        videos = []
        try:
            url = f'{self.xurl}/v1/theater/home_page?theater_class_id=1&class2_id=4&page_num=1&page_size=24'
            detail = requests.get(url=url, headers=self.headerx, timeout=10)
            detail.encoding = "utf-8"
            if detail.status_code == 200:
                data = detail.json()
                for vod in data['data']['list']:
                    name = vod['theater']['title']
                    id = vod['theater']['id']
                    pic = vod['theater']['cover_url']
                    remark = vod['theater']['play_amount_str']
                    video = {
                        "vod_id": id,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks": remark
                    }
                    videos.append(video)
        except Exception as e:
            print("首页列表异常", e)
        result = {'list': videos}
        return result

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []
        try:
            url = f'{self.xurl}/v1/theater/home_page?theater_class_id={cid}&page_num={pg}&page_size=24'
            detail = requests.get(url=url, headers=self.headerx, timeout=10)
            detail.encoding = "utf-8"
            if detail.status_code == 200:
                data = detail.json()
                for vod in data['data']['list']:
                    name = vod['theater']['title']
                    id = vod['theater']['id']
                    pic = vod['theater']['cover_url']
                    remark = vod['theater']['theme']
                    video = {
                        "vod_id": id,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks": remark
                    }
                    videos.append(video)
        except Exception as e:
            print("分类列表异常", e)
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
            url = f'{self.xurl}/v2/theater_parent/detail?theater_parent_id={did}'
            detail = requests.get(url=url, headers=self.headerx, timeout=10)
            detail.encoding = "utf-8"
            if detail.status_code == 200:
                data = detail.json()
            # ==========这里修改成真实远程地址==========
            txt_url = 'https://xxx/qyg6.txt'
            response = requests.get(txt_url, timeout=10)
            response.encoding = 'utf-8'
            code = response.text
            name = self.extract_middle_text(code, "s1='", "'", 0)
            Jumps = self.extract_middle_text(code, "s2='", "'", 0)
            content = '剧情：' + data['data']['introduction']
            area = data['data']['desc_tags'][0]
            remarks = data['data']['filing']
            if 'theaters' in data['data'] and data['data']['theaters']:
                for sou in data['data']['theaters']:
                    id = sou['son_video_url']
                    name = sou['num']
                    bofang = bofang + str(name) + '$' + id + '#'
                bofang = bofang[:-1] if bofang.endswith('#') else bofang
                xianlu = '星芽'
            else:
                if 'video_url' in data['data'] and data['data']['video_url']:
                    bofang = '1$' + data['data']['video_url']
                    xianlu = '星芽'
                else:
                    bofang = Jumps
                    xianlu = '1'
            videos.append({
                "vod_id": did,
                "vod_content": content,
                "vod_remarks": remarks,
                "vod_area": area,
                "vod_play_from": xianlu,
                "vod_play_url": bofang
            })
        except Exception as e:
            print("详情页异常", e)
        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = id
        result["header"] = self.headers
        return result

    def searchContentPage(self, key, quick, page):
        result = {}
        videos = []
        try:
            payload = {
                "text": key
            }
            url = f"{self.xurl}/v3/search"
            detail = requests.post(url=url, headers=self.headerx, json=payload, timeout=10)
            if detail.status_code == 200:
                detail.encoding = "utf-8"
                data = detail.json()
                for vod in data['data']['theater']['search_data']:
                    name = vod['title']
                    id = vod['id']
                    pic = vod['cover_url']
                    remark = vod['score_str']
                    video = {
                        "vod_id": id,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks": remark
                    }
                    videos.append(video)
        except Exception as e:
            print("搜索异常", e)
        result['list'] = videos
        result['page'] = page
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def searchContent(self, key, quick, pg="1"):
        # 修复：传递pg，支持搜索翻页
        return self.searchContentPage(key, quick, pg)

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None
