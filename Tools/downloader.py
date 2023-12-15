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
HEADERS_KEYS = ['user-agent', 'sec-ch-ua', 'referer', 'cookie']

DOWNLOAD_DIR = 'dir'
FILE_NAME = 'file_name'
URL = 'url'

CH_UA_DEFAULT = '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"'


class downloader:

    def __init__(self, config):
        self.init_opener(config)
        self.downloading_filename = 'None'
        self.timeout = TIMEOUT_DEFAULT
        self.max_retry = MAX_RETRY_DEFAULT
        self.sleep = 0
        self.url_quote = None
        if CONFIG_MAX_RETRY in config:
            self.max_retry = config[CONFIG_MAX_RETRY]
        if CONFIG_TIMEOUT in config:
            self.timeout = config[CONFIG_TIMEOUT]
        if CONFIG_SLEEP in config:
            self.sleep = config[CONFIG_SLEEP]
        if CONFIG_URL_QUOTE in config:
            self.url_quote = config[CONFIG_URL_QUOTE]

    def init_opener(self, _config):
        self.opener = urllib.request.build_opener()
        if _config is None:
            return
        if CONFIG_PROXY in _config and len(_config[CONFIG_PROXY]) > 0:
            # 添加 http 代理
            proxy_server = _config[CONFIG_PROXY]
            proxy = urllib.request.ProxyHandler({'http': proxy_server})
            self.opener = urllib.request.build_opener(proxy)
            print(f'使用代理: {proxy_server}')
        # HTTP HEADERS 配置项
        self.opener.addheaders = []
        # 默认 UA
        if 'user-agent' not in _config:
            _config['user-agent'] = CH_UA_DEFAULT
        if 'sec-ch-ua' not in _config:
            _config['sec-ch-ua'] = CH_UA_DEFAULT
        for header_key in HEADERS_KEYS:
            if header_key in _config:
                print(f'配置 {header_key}: {_config[header_key]}')
                self.opener.addheaders.append((header_key, _config[header_key]))
        print("Opener addheaders: ", self.opener.addheaders)

    '''
    ----------------- 下载 ----------------------------
    '''

    def download(self, task_list, dir_path=None):
        '''
        :param tasks: 下载任务信息[{'url': url, 'file_name': file_name}, {...}, ...]
        :param dir_path: 下载目录
        :param config: 下载配置, proxy 与 referer 等
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

        for task in tasks:
            sys.stdout.write('\r')
            sys.stdout.flush()
            # 优先下载到任务配置的目录
            if DOWNLOAD_DIR in task.keys():
                dir_path = task[DOWNLOAD_DIR]
            elif dir_path == None:
                dir_path = "download_undefined"
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
        print(f'Download finished {downloaded}/{total}!\nSaved at \\{dir_path}')
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
