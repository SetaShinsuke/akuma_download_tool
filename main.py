import os, sys
from pathlib import Path
from tkinter import filedialog as fd
from tkinter.messagebox import showwarning, askquestion
from crawlers.crawler_general import CrawlerGeneral

# 额外参数
use_idm = False
args = sys.argv
if len(args) > 1:
    if '--use-idm' in args:
        use_idm = True
        print(f'Use idm: True')

tasks_dir = os.path.join(os.getcwd(), 'tasks')
download_dir = os.path.join(os.getcwd(), 'download')

if not os.path.exists(tasks_dir):
    os.makedirs(tasks_dir)
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# 系统默认下载目录
sys_downloads_path = str(Path.home() / "Downloads")
print(f'Download dir: {sys_downloads_path}')
filetypes = (
    ('JSON files', '*.json'),
    ('All files', '*.*')
)
selected_files = fd.askopenfilenames(
    title='选择文件',
    initialdir=sys_downloads_path,
    filetypes=filetypes
)

if not selected_files:
    use_tasks_dir = askquestion('提示', '未选择文件\n自动检查.\\tasks目录?')
    # 不自动检测 input 目录
    if use_tasks_dir == 'yes':
        selected_files = map(lambda file_name: os.path.join(tasks_dir, file_name), os.listdir(tasks_dir))
    else:
        selected_files = []

crawler_general = CrawlerGeneral(selected_files, download_dir)
crawler_general.set_use_idm(use_idm)
do_zip = False
# <map>对象转成list
if len(list(selected_files)) > 0 and not use_idm:
    do_zip = askquestion('提示', '已选择任务文件\n是否按 tasks.json 打包?')
    do_zip = do_zip == 'yes'
result = crawler_general.start_download(do_zip)

if use_idm:
    print('已添加任务至IDM!')
else:
    len = len(result)
    if len > 0:
        showwarning('警告', f'有{len}任务下载失败!')

    if len > 0 or askquestion('提示', '任务结束\n是否查看?') == 'yes':
        os.startfile(download_dir)
