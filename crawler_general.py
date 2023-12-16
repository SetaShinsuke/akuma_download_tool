import os.path
import re
import sys, json
from datetime import datetime
import shutil

from Tools import download_tool
from Common import utils

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"

BOOK_NAME = 'book_name'
VOL_NO = 'vol_no'
PROXY = 'proxy'
REFERER = 'referer'  # 可以单独配置也可以在 headers 里
HEADERS = 'headers'  # config['headers']
DIR = 'dir'

# 下载器设置: max_retry, timeout, sleep, url_quote
DOWNLOAD_SETTINGS = 'download_settings'

# todo: 测试数量
TEST_AMOUNT = 1


class CrawlerGeneral:

    def __init__(self, _task_files, _download_root):
        self.task_files = _task_files
        self.download_root = _download_root

    def start_download(self, _do_zip):
        print(f'开始下载, do_zip: ${_do_zip}')
        result = []
        for f in self.task_files:
            if not re.search('task.*.json', os.path.basename(f)):
                print(f'不是 task.json 文件, 跳过: {f}')
                continue
            if not os.path.exists(f):
                print(f'文件不存在, 跳过: {f}')
            result += self.handle_task(f, _do_zip)
        return result

    # 每个 task.json 下载完打包一次
    def handle_task(self, task_file, do_zip):
        print(f'Handle task: {task_file}')
        try:
            raw_str = open(task_file, 'r', encoding='utf-8').read()
            task_json = json.loads(raw_str)
        except Exception as e:
            print("读取任务文件失败!")
            print(e)
            input("按任意键退出")
            sys.exit(0)

        settings = {}
        config = {}
        download_path = os.path.join(self.download_root, f'book_unknown_{datetime.now().microsecond}')
        if 'config' in task_json:
            config = task_json['config']
        # 下载器配置项
        if DOWNLOAD_SETTINGS in config:
            settings = config[DOWNLOAD_SETTINGS]
        # 新建下载器
        downloader = download_tool.Downloader(settings)
        # 设置下载代理与headers
        if PROXY in config:
            downloader.set_proxy(config[PROXY])
        headers = {'user-agent': UA}
        if REFERER in config:
            headers['referer'] = config[REFERER]
        if HEADERS in config:
            headers.update(config[HEADERS])
        downloader.set_headers(headers)
        # 下载路径
        book_name = f'book_unknown'
        vol_no = f'{datetime.now().microsecond}'
        if BOOK_NAME in config:  # /download/火影忍者
            book_name = config[BOOK_NAME]
        if VOL_NO in config:  # /download/火影忍者/火影忍者Vol001
            vol_no = f'_Vol{config[VOL_NO]}'
        download_path = os.path.join(self.download_root, f'{book_name}{vol_no}')

        tasks = []
        for k in task_json:
            if k == 'config':
                continue
            chapter_name = utils.verify_file_name(k)
            dir = os.path.join(download_path, chapter_name)
            page_details = task_json[k]
            # todo: 获取 token，更新 url
            i = 0
            for p in page_details:
                if TEST_AMOUNT > 0 and i >= TEST_AMOUNT:
                    break
                task = p.copy()
                task[DIR] = dir
                tasks.append(task)
                i = i + 1
            print("添加书目: ", chapter_name, "(", i, " pages)")
        # 开始下载
        print(f'下载任务已录入, 准备开始: {len(tasks)} 个任务')
        result = downloader.download(tasks)
        failed_pages = []
        if len(result) > 0:
            log_file = os.path.join(download_path, f'crawler_log_{datetime.now().microsecond}.txt')
            f = open(log_file, "w+")
            for item in result:
                f.write(f'{item}\n')
                failed_pages.append(item)
                # if ('page' in item):
                #     failed_pages.append(item['page'])
                # else:
                #     failed_pages.append(item)
            f.write(f'Failed pages: \n{failed_pages}\n')
            f.close()
        else:  # 没有失败任务
            base_name = os.path.basename(task_file)
            task_file_finish = f'finished_{book_name}_{base_name}'
            task_file_finish = task_file.replace(base_name, task_file_finish)
            try:
                os.rename(task_file, task_file_finish)
                if do_zip:
                    zip_name = download_path
                    print(f'正在打包 Zip...[{download_path}]')
                    # base_name: 文件名称; format: 格式; root_dir: 要打包的文件夹
                    shutil.make_archive(zip_name, 'zip', download_path)
                    print((f'Zip 已打包!'))
            except BaseException as e:
                print("Something went wrong: ", type(e), str(e))
        return failed_pages
