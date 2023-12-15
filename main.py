import os
from pathlib import Path
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo, showwarning, askquestion
import crawler_general

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
    if use_tasks_dir:
        selected_files = map(lambda file_name: os.path.join(tasks_dir, file_name), os.listdir(tasks_dir))
    else:
        selected_files = []

crawler_general = crawler_general.CrawlerGeneral(selected_files, download_dir)

do_zip = askquestion('提示', '已选择任务文件\n是否按 tasks.json 打包?')

result = crawler_general.start_download(do_zip)
len = len(result)
if len > 0:
    showwarning('警告', f'有{len}任务下载失败!')

if len > 0 or askquestion('提示', '任务结束\n是否查看?'):
    os.startfile(download_dir)
