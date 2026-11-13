#!/bin/sh
# Menyalakan MariaDB kalau belum jalan (jalankan tiap buka terminal baru)
if mariadb-admin ping >/dev/null 2>&1; then
  echo "MariaDB sudah jalan"
  exit 0
fi
mkdir -p /run/mysqld && chown mysql:mysql /run/mysqld
rm -f /run/mysqld/mysqld.sock
nohup mariadbd-safe --user=mysql --datadir=/var/lib/mysql > /tmp/mysql.log 2>&1 &
for i in 1 2 3 4 5 6 7 8 9 10; do
  sleep 1
  if mariadb-admin ping >/dev/null 2>&1; then
    echo "MariaDB menyala"
    exit 0
  fi
done
echo "GAGAL menyalakan, lihat: tail -20 /tmp/mysql.log"
exit 1
