from typing import Dict, Tuple, Union, List
from urllib.parse import urlencode
from urllib.request import urlopen
from socket import socket, AF_INET, SOCK_DGRAM
from sched import scheduler
from getpass import getpass

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
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)-5s - %(filename)-8s : %(lineno)s line - %(message)s'))
logger.addHandler(handler)


def help(args: List[str]):
    print(f"参数不完整, 提示:\n python {args[0]} 运营商 账号 密码")


def local_ip() -> str:
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(('223.5.5.5', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def parse_args() -> Tuple[str, str, str, int]:
    args = sys.argv
    if len(args) == 1:  # no args provided
        op = input('输入账号类型:\n1. 电信\n2. 移动\n输入: ')
        account = input('输入账号: ')
        passwd = getpass('输入密码: ')
        interval = input('重连周期(秒): ')
    elif len(args) == 5:
        op, account, passwd, interval = args[1], args[2], args[3], args[4]
    else:
        help(args)
        exit(1)

    return __operators[int(op)], account, passwd, int(interval)


def parse_raw_response(raw_rsp: str) -> Dict[str, Union[str, int]]:
    return json.loads(re.search('(?<=dr1003\().*?(?=\))', raw_rsp).group(0))


def connect(operator: str, account: str, passwd: str, _: int):
    logger.info('正在连接...')
    query = {
        'c': 'Portal',
        'a': 'login',
        'callback': 'dr1003',
        'login_method': 1,
        'wlan_user_ip': local_ip(),
        'wlan_user_mac': '000000000000',
        'user_account': f',0,{account}@{operator}',
        'user_password': passwd,
        'jsVersion': '3.3.3'
    }

    url = f'{__url_login}?{urlencode(query)}'
    rsp = urlopen(url)
    if rsp.status != 200:
        raise ValueError(rsp.status)

    raw_rsp = rsp.read().decode('unicode-escape')
    dict_rsp = parse_raw_response(raw_rsp)

    logger.info(f'received: {dict_rsp}')

    result = dict_rsp.get('result')
    if result == '1':
        logger.info('连接成功')
        return

    code = dict_rsp.get('ret_code')
    if code == 2:
        logger.info('连接成功!')
        return

    raise ValueError('连接失败! 可能原因: 账号密码错误或未关闭代理软件')


__schedulor = scheduler(time.time, time.sleep)


def go(*args):
    try:
        connect(*args)
    except Exception as e:
        logger.error(e)
        return

    interval = args[3]
    if interval == 0:
        return

    __schedulor.enter(interval, 0, go, args)
    logger.info(f'{interval}s 后会再次自动连接...')


if __name__ == '__main__':
    args = parse_args()

    go(*args)

    __schedulor.run()
