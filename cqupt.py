from argparse import ArgumentParser
from base64 import b64decode
from getpass import getpass
import re
from urllib.request import urlopen, Request
import socket
import os
import sys
import json
import time
import logging

HOST = "192.168.200.2:801"
REFERER = "http://192.168.200.2/"
PORTAL = "http://192.168.200.2:801/eportal"

AGENTS = {
    "android-chrome": "Mozilla/5.0 (Linux; Android 12; Pixel 6 Build/SD1A.210817.023; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.71 Mobile Safari/537.36",
    "ios-safari": "Mozilla/5.0 (iPhone13,2; U; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/15E148 Safari/602.1",
    "windows-edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "macos-safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
    "linux-firefox": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
}

ISP = ("cmcc", "telecom", "unicom", "xyw")


def get_uac_passwd(args) -> str:
    passwd = os.getenv("CQUPT_UAC_PASSWORD")
    if passwd:
        return passwd

    if not sys.stdin.isatty():
        return sys.stdin.readline().strip("\n")

    if args.passwd:
        return args.passwd

    return getpass(f"[cqupt] password for {args.account}: ")


def get_ipv4a(args) -> list[str]:
    if args.ipv4 != "auto":
        return [args.ipv4]
    return socket.gethostbyname_ex(socket.gethostname())[2]


def get_maca(args) -> str:
    return args.mac.replace(":", "").replace("-", "").lower()


def get_ua(args) -> str:
    if not args.ua in AGENTS:
        raise KeyError(f"invalid user agent: {args.ua}")
    return AGENTS[args.ua]


def get_isp(args) -> str:
    if not args.isp in ISP:
        raise KeyError(f"invalid ISP name: {args.isp}")
    return args.isp


def try_decode(s: str) -> str:
    try:
        if s.startswith("\\u"):
            return bytes(s, "utf-8").decode("unicode_escape")
        else:
            return b64decode(s).decode()
    except:
        return s

def extract(varname, html: str) -> str:
    m = re.search(rf"{varname}\s*=\s*['\"]([^'\"]+)['\"]", html)
    return m.group(1) if m else None

def get_wlan_ip(login_url: str) -> str:
    req = Request(login_url)
    with urlopen(req, timeout=5) as resp:
        raw = resp.read()
        charset = resp.headers.get_content_charset() or "gb2312"
        html = raw.decode(charset, errors="ignore")
    for name in ("v46ip", "ss5", "v4ip"):
        val = extract(name, html)
        if val:
            return val
    hex3 = extract("ss3")
    if hex3:
        if len(hex3) % 2:
            hex3 = "0" + hex3
        parts = [str(int(hex3[i : i + 2], 16)) for i in range(0, len(hex3), 2)]
        return ".".join(parts)

    return None


def connect(
    args,
    ipv4a,
    attempt=2,
) -> bool:
    account = args.account
    passwd = get_uac_passwd(args)
    isp = get_isp(args)
    maca = get_maca(args)
    agent = get_ua(args)

    logging.info(f"正在尝试以 {account}@{isp} {ipv4a}({maca}) {args.ua} 登录...")

    url = f"{PORTAL}?c=Portal&a=login&callback=dr1003&login_method=1&wlan_user_ip={ipv4a}&wlan_user_mac={maca}&user_account=,0,{account}@{isp}&user_password={passwd}&jsVersion=3.3.3"
    req = Request(url)
    req.add_header("Host", HOST)
    req.add_header("Referer", REFERER)
    req.add_header("User-Agent", agent)

    for i in range(attempt):
        with urlopen(req) as res:
            res_raw = res.read().decode()[7:-1]
            res_dict = json.loads(res_raw)
            logging.info(f"Attempt ({i+1}/{attempt})")
            if res_dict["result"] == "1" and try_decode(res_dict["msg"] == "认证成功"):
                logging.info(f"Succeed. Have fun :)")
                return True
            elif res_dict["result"] == "0":
                code = res_dict["ret_code"]
                msg_raw = res_dict["msg"]
                if code == 1:
                    msg = "错误的内网ip" if msg_raw == "" else try_decode(msg_raw)
                    logging.info(msg)
                    logging.info("切换内网ip，再次尝试登录")
                    return False
                elif code == 2:
                    logging.info("您已经登录")
                    return True
                else:
                    logging.info("未知错误")
            time.sleep(1.0)
    return False


def run(args) -> bool:
    ipv4a_list = get_ipv4a(args)
    wlan_ip = get_wlan_ip(REFERER)
    if wlan_ip:
        ipv4a_list.insert(0, wlan_ip)
    for ipv4a in ipv4a_list:
        if connect(args, ipv4a):
            return True
    return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)-5s] %(message)s")

    parser = ArgumentParser(description="[cqupt] 0.0.1")
    parser.add_argument("account", help="specify your unified authentication code")
    parser.add_argument(
        "--isp",
        dest="isp",
        default="cmcc",
        help="specify your ISP, choose `cmcc` for China Mobile, `telecom` for China Telecom, `unicom` for Chine Unicom and `xyw` if you are a teacher (default: cmcc)",
    )
    parser.add_argument(
        "--ipv4-addr",
        dest="ipv4",
        default="auto",
        help="specify a local IPv4 address (default: auto)",
    )
    parser.add_argument(
        "--mac-addr",
        dest="mac",
        default="00:00:00:00:00:00",
        help="specify a physical address (default: 00:00:00:00:00:00)",
    )
    parser.add_argument(
        "--user-agent",
        dest="ua",
        default="linux-firefox",
        help="specify a user agent, available options are: android-chrome, ios-safari, macos-safari, windows-edge, linux-firefox (default: linux-firefox)",
    )
    parser.add_argument(
        "--force-password",
        dest="passwd",
        help="specify your UAC password implicitly (not recommended)",
    )
    args = parser.parse_args()

    run(args)
