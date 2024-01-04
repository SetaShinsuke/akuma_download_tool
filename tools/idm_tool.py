import os, sys

# sys.path.append('../')
from common import utils

from tools.downloader_meta import DownloaderMeta
from tools.downloader_meta import DOWNLOAD_DIR, FILE_NAME, URL

IDM_EXE = f'C:\\Program Files (x86)\\Internet Download Manager\\IDMan.exe'


class IdmTool(DownloaderMeta):
    def __init__(self, _settings):
        print(f'Idm tool init, no settings needed')
        self.settings = _settings

    def set_proxy(self, proxy_server):
        print(f'Skip proxy config in idm_tool')

    def set_headers(self, headers):
        print(f'Skip headers config in idm_tool')

    def download(self, task_list):
        print("----------- Start Download -----------")
        tasks = list(filter(self.filter_fun, task_list))
        cmds = []
        for task in tasks:
            dir = None
            file_url = task[URL]
            if DOWNLOAD_DIR in task.keys():
                dir = task[DOWNLOAD_DIR]
            if FILE_NAME in task.keys():
                file_name = task[FILE_NAME]
            else:
                file_name = file_url.split('/')[-1].split('?')[0]
                file_name = utils.verify_file_name(file_name)
            cmds.append(f'"{IDM_EXE}" /n /p "{dir}" /f "{file_name}" /d "{file_url}"')
        # 命令行启动 IDM, 防止命令行太长, 逐条运行
        # cmds_str = ' & '.join(cmds)
        total = len(cmds)
        i = 0
        for c in cmds:
            cmd = f'cmd /C "{c}"'
            i += 1
            print(f'IDM CMD: {i}/{total}')
            print(cmd)
            os.system(cmd)
        return []
