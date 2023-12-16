# -*- coding: utf-8 -*-
import urllib.request
import sys
import os
import socket
import urllib.parse
import time

sys.path.append('../')
from Common import utils

MAX_RETRY_DEFAULT = 4
TIMEOUT_DEFAULT = 30

CONFIG_MAX_RETRY = 'max_retry'
CONFIG_TIMEOUT = 'timeout'
CONFIG_SLEEP = 'sleep'
CONFIG_URL_QUOTE = 'url_quote'  # {'url_quote': ':/='} 表示不转义这三个字符

CONFIG_PROXY = "proxy"
# HEADERS_KEYS = ['user-agent', 'sec-ch-ua', 'referer', 'cookie']

# [{'url': url, 'file_name': file_name, 'dir': 'C://xxxx/xxx/xxx', 'page': 1}, {...}, ...]
DOWNLOAD_DIR = 'dir'
FILE_NAME = 'file_name'
URL = 'url'

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
CH_UA_DEFAULT = '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"'


class Downloader:

    def __init__(self, settings):
        self.opener = urllib.request.build_opener()
        self.downloading_filename = 'None'
        self.timeout = TIMEOUT_DEFAULT
        self.max_retry = MAX_RETRY_DEFAULT
        self.sleep = 0
        self.url_quote = None
        if CONFIG_MAX_RETRY in settings:
            self.max_retry = settings[CONFIG_MAX_RETRY]
        if CONFIG_TIMEOUT in settings:
            self.timeout = settings[CONFIG_TIMEOUT]
        if CONFIG_SLEEP in settings:
            self.sleep = settings[CONFIG_SLEEP]
        if CONFIG_URL_QUOTE in settings:
            self.url_quote = settings[CONFIG_URL_QUOTE]

    def set_proxy(self, proxy_server):
        proxy = urllib.request.ProxyHandler({'http': proxy_server})
        self.opener = urllib.request.build_opener(proxy)
        print(f'使用代理: {proxy_server}')

    def set_headers(self, headers=None):
        self.opener.addheaders = []
        if not headers:
            headers = {}
        if 'user-agent' not in headers:
            headers['user-agent'] = UA
            print(f'默认使用  user-agent: {UA}')
        if 'sec-ch-ua' not in headers:
            headers['sec-ch-ua'] = CH_UA_DEFAULT
            print(f'默认使用 sec-ch-ua: {CH_UA_DEFAULT}')
        for header_key in headers:
            print(f'配置 {header_key}: {headers[header_key]}')
            self.opener.addheaders.append((header_key, headers[header_key]))
        print("Opener addheaders: ", self.opener.addheaders)

    def download(self, task_list):
        '''
        :param task_list: 下载任务信息[{'url': url, 'file_name': file_name, 'dir': 'C://xxx/xx', 'page': 1}, {...}, ...]
        :param dir_path: 下载目录, 如果 json 里单独设置了 dir，
        :return:
        '''
        print("----------- Start Download -----------")
        tasks = list(filter(self.filter_fun, task_list))
        total = len(tasks)
        downloaded = 0
        failed = []
        max_amount = total
        sleep = self.sleep
        # max_amount = 1
        print(f'max_amount: {max_amount}')
        urllib.request.install_opener(self.opener)
        print(f'Opener installed')

        for task in tasks:
            sys.stdout.write('\r')
            sys.stdout.flush()
            # 优先下载到任务配置的目录
            dir_path = "download_undefined"
            if DOWNLOAD_DIR in task.keys():
                dir_path = task[DOWNLOAD_DIR]
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            if downloaded >= max_amount:
                break
            file_url = task[URL]
            # 检查文件名与url
            if self.url_quote:
                file_url = urllib.parse.quote(file_url, safe=self.url_quote)
            if FILE_NAME in task.keys():
                file_name = task[FILE_NAME]
            else:
                file_name = file_url.split('/')[-1].split('?')[0]
                file_name = utils.verify_file_name(file_name)
            if os.path.exists(f'{dir_path}\\{file_name}'):  # 检查重名
                name = file_name.split(".")[0]
                file_name = file_name.replace(name, f'{name}_{downloaded}')
            # 开始下载
            retry = 0
            while (retry <= self.max_retry):
                try:
                    print(f'url: {file_url}')
                    print(f'file_name: {file_name}')
                    if retry > 0:
                        print("retry: ", retry)
                    # global downloading_filename
                    self.downloading_filename = file_name
                    socket.setdefaulttimeout(self.timeout)
                    filepath, _ = urllib.request.urlretrieve(file_url, f'{dir_path}\\{file_name}', self._progress)
                    if (sleep and sleep > 0):
                        time.sleep(sleep)
                    break
                except Exception as err:
                    print("----\nSomething wrong happened!")
                    print(f'file_name: {file_name}')
                    print("retry: ", retry)
                    retry += 1
                    print(type(err))
                    print(err.args)
                    print(err)
                    print("----")
                    if retry > self.max_retry:
                        failed.append(task)
                        print("重试无效!\n----")
                        break
                    pass
            downloaded += 1
        # 下载任务结束
        sys.stdout.write('\r')
        sys.stdout.flush()
        print(f'Download finished {downloaded}/{total}!')
        if len(failed) > 0:
            print(f'{len(failed)}\\{total} download failed!!')
            print("failed tasks: ")
            for t in failed:
                print(t)
        return failed

    def filter_fun(_self, item):
        return type(item) is dict and URL in item.keys() and item[URL].startswith("http")

    def _progress(_self, block_num, block_size, total_size):
        '''回调函数
           :param block_num: 已经下载的数据块
           :param block_size: 数据块的大小
           :param total_size: 远程文件的大小
        '''
        sys.stdout.write('\r>> Downloading %s %.1f%%' % (_self.downloading_filename,
                                                         float(block_num * block_size) / float(
                                                             total_size) * 100.0))
        sys.stdout.flush()
