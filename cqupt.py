from argparse import ArgumentParser
from base64 import b64decode
from getpass import getpass
from urllib.request import urlopen, Request
from socket import socket, AF_INET, SOCK_DGRAM

import os
import sys
import json
import time
import logging

HOST = '192.168.200.2:801'
REFERER = 'http://192.168.200.2/'
PORTAL = 'http://192.168.200.2:801/eportal'

AGENTS = {
    'android-chrome': 'Mozilla/5.0 (Linux; Android 12; Pixel 6 Build/SD1A.210817.023; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.71 Mobile Safari/537.36',
    'ios-safari': 'Mozilla/5.0 (iPhone13,2; U; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/15E148 Safari/602.1',
    'windows-edge': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    'macos-safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
    'linux-firefox': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
}

ISP = ('cmcc', 'telecom', 'unicom', 'xyw')


def get_uac_passwd(args) -> str:
    passwd = os.getenv('CQUPT_UAC_PASSWORD')
    if passwd:
        return passwd

    if not sys.stdin.isatty():
        return sys.stdin.readline().strip('\n')

    if 'passwd' in args:
        return args.passwd

    return getpass(f'[cqupt] password for {args.account}: ')


def get_ipv4a(args) -> str:
    if args.ipv4 != 'auto':
        return args.ipv4
    with socket(AF_INET, SOCK_DGRAM) as sock:
        sock.connect(('223.5.5.5', 80))
        return sock.getsockname()[0]


def get_maca(args) -> str:
    return args.mac.replace(':', '')


def get_ua(args) -> str:
    if not args.ua in AGENTS:
        raise KeyError(f'invalid user agent: {args.ua}')
    return AGENTS[args.ua]


def get_isp(args) -> str:
    if not args.isp in ISP:
        raise KeyError(f'invalid ISP name: {args.isp}')
    return args.isp


def try_base64(s: str) -> str:
    try:
        return b64decode(s).decode()
    except:
        return s


def connect(args, attempt = 3) -> bool:
    account = args.account
    passwd = get_uac_passwd(args)
    isp = get_isp(args)
    ipv4a = get_ipv4a(args)
    maca = get_maca(args)
    agent = get_ua(args)

    logging.info(f'Sign in as {account}@{isp} {ipv4a}({maca}) {args.ua} ...')

    url = f'{PORTAL}?c=Portal&a=login&callback=dr1003&login_method=1&wlan_user_ip={ipv4a}&wlan_user_mac={maca}&user_account=,0,{account}@{isp}&user_password={passwd}&jsVersion=3.3.3'
    req = Request(url)
    req.add_header('Host', HOST)
    req.add_header('Referer', REFERER)
    req.add_header('User-Agent', agent)
    
    possible_cause = 'unknown'
    for i in range(attempt):
        with urlopen(req) as res:
            res_raw = res.read().decode()[7:-1]
            res_dict = json.loads(res_raw)

            logging.info(f'Attempt ({i+1}/{attempt}): {res_raw}')
        
            if res_dict['result'] == "0" and res_dict['ret_code'] == 2:
                logging.info('Succeed. Have fun :)')
                return True

            cause = res_dict['msg']
            if cause:
                possible_cause = try_base64(cause)

            time.sleep(1.0)
    
    logging.error(f'Failed to sign in, reason: {possible_cause}')
    return False





if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = ArgumentParser()
    parser.add_argument('account', help='Specify your unified authentication code')
    parser.add_argument('--isp', dest='isp', default='cmcc', help='Specify your ISP, choose `cmcc` for China Mobile, `telecom` for China Telecom, `unicom` for Chine Unicom and `xyw` if you are a teacher (default: cmcc)')
    parser.add_argument('--ipv4-addr', dest='ipv4', default='auto', help='Specify a local IPv4 address (default: auto)')
    parser.add_argument('--mac-addr', dest='mac', default='00:00:00:00:00:00', help='Specify a mac address (default: 00:00:00:00:00:00)')
    parser.add_argument('--user-agent', dest='ua', default='linux-firefox', help='Specify a user agent, available options are: android-chrome, ios-safari, macos-safari, windows-edge, linux-firefox (default: linux-firefox)')
    parser.add_argument('--force-password', dest='passwd', help='Specify your UAC password implicitly (not recommended)')
    args = parser.parse_args()
    
    connect(args)
    