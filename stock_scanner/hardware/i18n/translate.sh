#! /usr/bin/env bash

function display_usage() {
    echo 'Usage :'
    echo 'translate.sh extract'
    echo 'translate.sh init [LANG]'
    echo 'translate.sh compile [LANG]'
    exit 1
}

if [ $# -lt 1 ]; then
    display_usage
fi

case $1 in
extract)
    # Extract translatable strings from python files
    mkdir -p sentinel
    xgettext --language=Python --keyword=_ --output=sentinel/sentinel.pot --from-code=UTF-8 --package-name=sentinel --package-version=1.0 ../sentinel.py
    ;;
init)
    if [ $# -lt 2 ]; then
        display_usage
    fi
    # Initialize translation file
    mkdir -p sentinel
    msginit --input=sentinel/sentinel.pot --output=sentinel/$2.po --locale=$2
    ;;
update)
    if [ $# -lt 2 ]; then
        display_usage
    fi
    # Initialize translation file
    mkdir -p sentinel
    msgmerge --previous sentinel/$2.po sentinel/sentinel.pot --output=sentinel/$2.po
    ;;
compile)
    if [ $# -lt 2 ]; then
        display_usage
    fi
    # Compile translated .po file in a .mo file
    mkdir -p $2/LC_MESSAGES
    msgfmt sentinel/$2.po --output-file $2/LC_MESSAGES/sentinel.mo
    ;;
*)
    display_usage
esac
