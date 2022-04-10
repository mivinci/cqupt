#!/bin/bash

HOST='http://192.168.200.2:801/eportal'


if [ $# -ne 4 ]; then
    printf "This script is for you to log in the CQUPT network. \nYou are supposed to provide 4 arguments formatted as follows:\n"
    printf "\n\tbash $0 {type} {ID} {password} {IP address}\n\n"
    printf "%-12s: Choose 'cmcc' for China Mobile and 'telecom' for China Telecom.\n" "type"
    printf "%-12s: Your account identity.\n" "ID"
    printf "%-12s: Yout account password.\n" "password"
    printf "%-12s: The internal IP address given by the network.\n" "IP address"
    exit
fi

URL="${HOST}?"
URL="${URL}c=Portal&"
URL="${URL}a=login&"
URL="${URL}callback=dr1003&"
URL="${URL}login_method=1&"
URL="${URL}wlan_user_ip=$4&"
URL="${URL}wlan_user_mac=000000000000&"
URL="${URL}user_account=,0,$2@$1&"
URL="${URL}user_password=$3&"
URL="${URL}jsVersion=3.3.3"

echo 'Onboarding...'
out=`curl -sL $URL`

if [[ $out =~ '"ret_code":2' ]]; then
    echo 'Done! You are ready to go :)'
    exit
fi

echo 'Failed! Please make sure all that you provided are correct.'
