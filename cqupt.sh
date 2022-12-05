#!/bin/bash

set -e

echo "
   ____ ___  _   _ ____ _____ 
  / ___/ _ \| | | |  _ \_   _|
 | |  | | | | | | | |_) || |  
 | |__| |_| | |_| |  __/ | |  
  \____\__\_\\\\___/|_|    |_|.edu.cn
"


PORTAL='http://192.168.200.2:801/eportal'

declare -A agents=(
    ['Android (Chrome)']='Mozilla/5.0 (Linux; Android 12; Pixel 6 Build/SD1A.210817.023; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.71 Mobile Safari/537.36'
    ['iOS (Safari)']='Mozilla/5.0 (iPhone13,2; U; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/15E148 Safari/602.1'
    ['Windows (Edge)']='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    ['macOS (Safari)']='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
    ['Linux (Firefox)']='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'
    ['Playstation 5']='Mozilla/5.0 (PlayStation; PlayStation 5/2.26) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15'
    ['Xbox Series X']='Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox Series X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36 Edge/20.02'
    ['Nintendo Switch']='Mozilla/5.0 (Nintendo Switch; WifiWebAuthApplet) AppleWebKit/601.6 (KHTML, like Gecko) NF/4.0.0.5.10 NintendoBrowser/5.1.0.13343'
    ['Amazon Kindle 4']='Mozilla/5.0 (X11; U; Linux armv7l like Android; en-us) AppleWebKit/531.2+ (KHTML, like Gecko) Version/5.0 Safari/533.2+ Kindle/3.0+'
    ['Google Bot']='Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    ['Bing Bot']='Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)'
    ['Yahoo! Bot']='Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)'
)


declare -A nets=(
    ['Other']='xyw'
    ['China Telecom']='telecom'
    ['China Unicom']='unicom'
    ['China Mobile']='cmcc'
)

read -p "Account: " account

read -s -p "Password (invisible): " password

echo

PS3="Network provider (select 'Other' if you are a teacher): "
select net in "${!nets[@]}"; do
    if [ -n "$net" ]; then
        break
    fi
    echo "[WARN] Invalid option, please select again."
done


PS3='User agent: '
select agent in "${!agents[@]}"; do
    if [ -n "$agent" ]; then
        break
    fi
    echo "[WARN] Invalid option, please select again."
done


read -p "Local IPv4 address (Leave it blank to extract automatically): " ipv4
if [ -z $ipv4 ]; then
    # taken from https://stackoverflow.com/questions/21336126/linux-bash-script-to-extract-ip-address
    ipv4=$(ip route get 8.8.8.8 | awk -F"src " 'NR==1{split($2,a," ");print a[1]}')
fi


read -p "Sign in as '$account, $net, $agent, $ipv4'? [Y/n]: " confirm
if [[ "$confirm" == "n" ]]; then
    exit 0
fi


printf -v api "%s?c=Portal&a=login&callback=dr1003&login_method=1&wlan_user_ip=%s&wlan_user_mac=000000000000&user_account=,0,%s@%s&user_password=%s&jsVersion=3.3.3" $PORTAL $ipv4 $account ${nets[$net]} $password
success_res='dr1003({"result":"0","msg":"","ret_code":2})'

echo "[INFO] Connecting..."

attempt=3
for i in $(seq 1 $attempt); do
    res=`curl -sL -A "${agents[$agent]}" $api`
    echo "[INFO] Attempt ($i/$attempt): $res"

    # Yea I know.
    if [[ $res == *"$success_res"* ]]; then
        echo "[INFO] Connected. Have fun :)"
        exit
    fi

    sleep 1
done

echo -e '[ERROR] Failed to connect. Please check out your inputs and try again.'
