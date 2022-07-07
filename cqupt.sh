#!/bin/bash

HOST='http://192.168.200.2:801/eportal'


if [ $# -ne 3 ]; then
    printf "This script is for you to log in the CQUPT network.\nYou are supposed to provide 3 arguments formatted as follows.\nYou'll then be asked to input your password.\n"
    printf "\n\tsh $0 {type} {id} {address}\n\n"
    printf "%-7s: Choose 'cmcc' for China Mobile and 'telecom' for China Telecom.\n" "type"
    printf "%-7s: Your account identity.\n" "id"
    printf "%-7s: The internal IP address given by the network.\n" "address"
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
    echo 'Have fun! :)'
    exit
fi

echo 'Failed! Please make sure all that you provided are correct.'
