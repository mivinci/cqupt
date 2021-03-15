import re
import json
from sys import argv
from urllib.parse import urlencode
from urllib.request import urlopen
from socket import socket, AF_INET, SOCK_DGRAM

URL_LOGIN = 'http://192.168.200.2:801/eportal/'
# URL_LOGOUT = 'http://192.168.200.2:801/eportal/?c=Portal&a=unbind_mac&callback=dr1002&user_account=1651733%40telecom&wlan_user_ip=10.20.73.51'

user_types = [
    ('telecom', '中国电信'),
    ('cmcc', '中国移动'),
    ('xyw', '教师账号')
]

def local_ip() -> str:
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def help() -> None:
    print('''使用方法:
    运行 python wifi.py 账户类型 账号 密码
账户类型:''')
    for i, v in enumerate(user_types):
        print(f'    {i}: {v[1]}')

def cmd_args() -> tuple:
    if len(argv) != 4:
        help()
        exit()
    return user_types[int(argv[1])], argv[2], argv[3]


def parse_raw_response(raw_rsp: str) -> dict:
    return json.loads(re.search('(?<=dr1003\().*?(?=\))', raw_rsp).group(0))


user_type, account, password = cmd_args()
print('账号:', account)
print('账号类型:', user_type[1])

ip = local_ip()
print('本机IP地址:', ip)

query = {
    'c': 'Portal',
    'a': 'login',
    'callback': 'dr1003',
    'login_method': 1,
    'wlan_user_ip': ip,
    'wlan_user_mac': '000000000000',
    'user_account': f',0,{account}@{user_type[0]}',
    'user_password': password
}

print('登录中...')

try:
    url = f'{URL_LOGIN}?{urlencode(query)}'
    resp = urlopen(url)
    if resp.status != 200:
        raise ValueError(resp.status)
except Exception as e:
    print('登录失败!', e)
    exit(1)


raw_rsp = resp.read().decode('unicode-escape')
dict_rsp = parse_raw_response(raw_rsp)

code = dict_rsp.get('ret_code')
if code == 2:
    print('你已登录!')
    exit(1)
elif code == 1:
    print('账号不存在')
    exit(1)
else:
    print(dict_rsp.get('msg'), '开始网上冲浪吧!')
