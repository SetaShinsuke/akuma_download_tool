# -*- coding: utf-8 -*-
import re
import urllib.parse
import pyperclip
import sys
import requests.utils

def verify_file_name(file_name):
    file_name = file_name.replace('\\', '_').replace('/', '_')
    file_name = re.sub('[\/:*?"<>|]', '-', file_name)
    file_name = file_name.replace('（', '(').replace('）', ')').replace(' ', '_').replace('：', ':')
    if (len(file_name) > 150):  # 文件名超长
        file_name = file_name[-149:]
    return file_name


def url_encode(string):
    # return urllib.parse.quote(string, encoding)
    return requests.utils.requote_uri(string)

def url_decode(string, encoding='utf-8'):
    return urllib.parse.unquote(string, encoding)

def copy_to_clipboard(string):
    pyperclip.copy(string)

# notNull = False: 允许不输入
def requireInt(msg, notNull = False):
    while 1:
        userInput = input(msg)
        try:
            if len(userInput) == 0 and (not notNull):
                return None
            return int(userInput)
        except ValueError:
            print('请输入数字...')

def flush(content):
    sys.stdout.write(f'\r>>{content}')
    sys.stdout.flush()
    # time.sleep(1)
    # flush_reset()

def flush_reset():
    sys.stdout.write(f'\n')
    sys.stdout.flush()