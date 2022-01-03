from typing import Dict, Tuple
from urllib.parse import urlencode
from urllib.request import urlopen
from socket import socket, AF_INET, SOCK_DGRAM
from sched import scheduler

import re
import sys
import json
import time
import logging


__url_login = 'http://192.168.200.2:801/eportal'

__operators = ('xyw', 'telecom', 'cmcc')


# Fuck OOP!
logger = logging.Logger('logger')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)-9s - %(filename)-8s : %(lineno)s line - %(message)s'))
logger.addHandler(handler)


def help():
    pass

def local_ip() -> str:
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def parse_args() -> Tuple[str, str, str]:
    args = sys.argv
    if len(args) != 4:
        op = input('输入账号类型:\n1. 电信\n2. 移动\n输入: ')
        account = input('输入账号: ')
        passwd = input('输入密码: ')
    else:
        op, account, passwd = args[1], args[2], args[3]
        
    return __operators[int(op)], account, passwd


def parse_raw_response(raw_rsp: str) -> Dict[str, str | int]:
    return json.loads(re.search('(?<=dr1003\().*?(?=\))', raw_rsp).group(0))


def login(operator: str, account: str, passwd: str):
    logger.info('正在连接...')
    try:
        query = {
            'c': 'Portal',
            'a': 'login',
            'callback': 'dr1003',
            'login_method': 1,
            'wlan_user_ip': local_ip(),
            'user_account': f',0,{account}@{operator}',
            'user_password': passwd,
            'jsVersion': '3.3.3',
            'v': '2550'
        }

        url = f'{__url_login}?{urlencode(query)}'
        rsp = urlopen(url)
        if rsp.status != 200:
            raise ValueError(rsp.status)
    except Exception as e:
        raise e  # fuck try..except(catch) !

    raw_rsp = rsp.read().decode('unicode-escape')
    dict_rsp = parse_raw_response(raw_rsp)
    
    # logger.info(f'received: {dict_rsp}')

    code = dict_rsp.get('ret_code')
    if code == 2:
        logger.info('连接成功!')
    elif code == 1:
        raise ValueError('账号不存在')


__schedulor = scheduler(time.time, time.sleep)
__scheduler_interval = 3600  # one hour

def go(*args):
    try:
        login(*args)
    except Exception as e:
        logger.error(e)

    __schedulor.enter(__scheduler_interval, 0, go, args)
    logger.info(f'{__scheduler_interval}s 后会再次自动连接...')

if __name__ == '__main__':
    # run at start
    args = parse_args()
    go(*args)

    __schedulor.run()

