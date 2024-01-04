from abc import ABCMeta, abstractmethod

DOWNLOAD_DIR = 'dir'
FILE_NAME = 'file_name'
URL = 'url'
class DownloaderMeta(metaclass=ABCMeta):
    @abstractmethod
    def set_proxy(self, proxy_server):
        pass

    @abstractmethod
    def set_headers(self, headers):
        pass

    @abstractmethod
    def download(self, task_list):
        pass

    def filter_fun(_self, item):
        return type(item) is dict and URL in item.keys() and item[URL].startswith("http")
