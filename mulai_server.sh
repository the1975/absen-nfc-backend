#!/bin/sh
# Menyalakan database dan server aplikasi, lalu memastikan server benar-benar hidup
cd "$(dirname "$0")" || exit 1
./mulai_db.sh || exit 1
cd server || exit 1
pkill -f "uvicorn main:app" 2>/dev/null
sleep 1
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/server.log 2>&1 &
for i in 1 2 3 4 5 6 7 8 9 10; do
  sleep 1
  if python3 -c "import urllib.request as u; u.urlopen('http://localhost:8000/')" 2>/dev/null; then
    echo "Server menyala di port 8000"
    exit 0
  fi
done
echo "GAGAL, ini isi lognya:"
tail -15 /tmp/server.log
exit 1
