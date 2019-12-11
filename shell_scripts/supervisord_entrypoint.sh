#!/usr/bin/env sh
set -e

npm run build

if [ $# -eq 0 ] || [ "${1#-}" != "$1" ]; then
  set -- supervisord "$@"
fi

echo "[+] flask createdb"
flask createdb

if [ ! -d "./migrations" ]; then
  echo "[+] flask db init"
  flask db init
fi

echo "[+] flask db migrate"
flask db migrate

echo "[+] flask db upgrade"
flask db upgrade

echo "[+] flask stamp head"
flask db stamp head

# test access for nydata exercise
echo "[+] flask adduser"
flask adduser tester tester123456 tester@nydata.com

exec "$@"
