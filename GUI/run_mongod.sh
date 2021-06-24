#!/bin/bash

if service mongod status; then
  read -rn1
  exit 0
fi

if ! command -v "C:\Program Files\MongoDB\Server\4.4\bin\mongod.exe"; then
    echo "This application requires mongod (eg MongoDB Community Server), which can be installed from https://www.mongodb.com/try/download/community?tck=docs_server . It is necessary to install as service."
    read -rn1
    exit 1
fi


case "$OSTYPE" in
  msys* | cygwin*)
    echo "WINDOWS"
    #cd C:\ || read -rn1 && exit
    mkdir -p "C:\data\db"
    "C:\Program Files\MongoDB\Server\4.4\bin\mongod.exe" --dbpath="c:\data\db"
    ;;
  darwin*)
    echo "OSX"
    brew services start mongodb-community@4.4
    # brew services stop mongodb-community@4.4
    ;;
  linux*)
    echo "LINUX"
    sudo systemctl start mongod
    # sudo systemctl stop mongod
    ;;
  *)
    echo "unknown or unsupported: $OSTYPE"
    read -rn1
    exit 2
    ;;
esac

if ! service mongod status; then
    echo "Unable to start mongod process"
    read -rn1
    exit 3
fi

read -rn1
exit 0