#!/bin/bash

HOST='http://192.168.200.2:801/eportal'

if [ $# -ne 3 ]; then
    echo "This script logs your device into the CQUPT network."
    echo "You need to provide 3 arguments and then input your password."
    echo "Example:"
    echo -e "\n    sh $0 {TYPE} {ID} {IP}\n"
    echo "TYPE  choose 'cmcc' for China Mobile or 'telecom' for China Telecom"
    echo "ID    unified authentication ID"
    echo "IP    IP address of you device"
    exit
fi

read -s -p "Password: " PASSWORD

URL="${HOST}?"
URL="${URL}c=Portal&"
URL="${URL}a=login&"
URL="${URL}callback=dr1003&"
URL="${URL}login_method=1&"
URL="${URL}wlan_user_ip=$3&"
URL="${URL}wlan_user_mac=000000000000&"
URL="${URL}user_account=,0,$2@$1&"
URL="${URL}user_password=$PASSWORD&"
URL="${URL}jsVersion=3.3.3"

echo 'Onboarding...'
out=`curl -sL $URL`

if [[ $out =~ '"ret_code":2' ]]; then
    echo 'Connected. Have fun! :)'
    exit
fi

echo -e 'Something went wrong. \nPlease check out your input and try again.'
