import logging
import os
import re
import datetime
import requests

from BiliLive import BiliLive
import utils

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BiliLiveRecorder(BiliLive):
    def __init__(self, config: dict, global_start: datetime.datetime):
        super().__init__(config)
        self.record_dir = utils.init_record_dir(
            self.room_id, global_start, config['root']['global_path']['data_path'])

    def record(self, record_url: str, output_filename: str) -> None:
        try:
            logging.info(self.generate_log('√ 正在录制...' + self.room_id))
            default_headers = {
                'Accept-Encoding': 'identity',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36 ',
                'Referer': re.findall(
                    r'(https://.*\/).*\.flv',
                    record_url)[0]
            }
            headers = {**default_headers, **
                       self.config['root']['request_header']}
            resp = requests.get(record_url, stream=True, headers=headers)
            with open(output_filename, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except Exception as e:
            logging.error(self.generate_log(
                'Error while recording:' + str(e)))

    def run(self) -> None:
        while True:
            try:
                if self.live_status:
                    urls = self.get_live_urls()
                    filename = utils.generate_filename(self.room_id)
                    c_filename = os.path.join(self.record_dir, filename)
                    self.record(urls[0], c_filename)
                    logging.info(self.generate_log('录制完成' + c_filename))
                else:
                    logging.info(self.generate_log('下播了'))
                    break
            except Exception as e:
                logging.error(self.generate_log(
                    'Error while checking or recording:' + str(e)))