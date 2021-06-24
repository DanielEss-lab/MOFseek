#!/bin/bash
net stop MongoDB
read -rn1
if systemctl is-active --quiet service; then
  echo "no need to stop running MongoDB server process, as it is not running."
  read -rn1
  exit
fi

case "$OSTYPE" in
  msys* | cygwin*)
    echo "WINDOWS"
    echo "Attempt 1..."
    mongo admin --eval "db.shutdownServer()"
    if service mongod status; then
      read -rn1
      exit
    fi
    echo "Attempt 2..."
    "C:\Program Files\MongoDB\Server\4.4\bin\mongod.exe" --remove
    if service mongod status; then
      read -rn1
      exit
    fi
    echo "Attempt 3..."
    net stop mongodb
    ;;
  darwin*)
    echo "OSX"
    brew services stop mongodb-community@4.4
    ;;
  linux*)
    echo "LINUX"
    sudo systemctl stop mongod
    ;;
  *)
    echo "unknown or unsupported: $OSTYPE"
    read -rn1
    exit
    ;;
esac

if service mongod status; then
    echo "Unable to end mongod process. Your computer might be ever so slightly slower until you restart it."
    read -rn1
    exit
fi