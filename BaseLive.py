import abc
import datetime
import logging

import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BaseLive(metaclass=abc.ABCMeta):
    __last_check_time = datetime.datetime.now(
    )+datetime.timedelta(seconds=-60)
    __allowed_check_interval = datetime.timedelta(
        seconds=60)
    __live_status = False

    def __init__(self, config: dict):
        default_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-TW;q=0.2',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36 '
        }
        self.headers = {**default_headers, **config['root']['request_header']}
        self.session = requests.session()
        self.room_id = ''
        self.site_name = ''
        self.site_domain = ''
        self.config = config
        BaseLive.__allowed_check_interval = datetime.timedelta(
            seconds=config['root']['check_interval'])

    def common_request(self, method: str, url: str, params: dict = None, data: dict = None) -> requests.Response:
        connection = None
        if method == 'GET':
            connection = self.session.get(
                url, headers=self.headers, params=params, verify=False)
        if method == 'POST':
            connection = self.session.post(
                url, headers=self.headers, params=params, data=data, verify=False)
        return connection

    @abc.abstractmethod
    def get_room_info(self):
        pass

    @abc.abstractmethod
    def get_live_urls(self):
        pass

    def __check_live_status(self) -> bool:
        room_info = self.get_room_info()
        if room_info['status']:
            logging.info(self.generate_log(
                "直播间标题："+room_info['roomname']))
            return True
        else:
            logging.info(self.generate_log("等待开播"))
        return False

    @property
    def live_status(self) -> bool:
        if datetime.datetime.now()-BaseLive.__last_check_time >= BaseLive.__allowed_check_interval:
            logging.debug(self.generate_log("允许检查"))
            BaseLive.__live_status = self.__check_live_status()
            BaseLive.__last_check_time = datetime.datetime.now()
        else:
            logging.debug(self.generate_log("间隔不足，使用过去状态"))
        return BaseLive.__live_status

    @live_status.setter
    def live_status(self, status: bool):
        BaseLive.__live_status = status

    def generate_log(self, content: str = '') -> str:
        return f"[Site:{self.site_name} Room:{self.room_id}] {content}"
