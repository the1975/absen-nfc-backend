#!/bin/sh
# Membuka tunnel localhost.run ke port 8000 dan menampilkan alamat publiknya
command -v ssh >/dev/null || apk add openssh-client
pkill -f "nokey@localhost.run" 2>/dev/null
nohup ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:localhost:8000 nokey@localhost.run > /tmp/tunnel.log 2>&1 &
for i in $(seq 1 25); do
  sleep 1
  HOST=$(grep -aEo '[0-9a-f]{8,}(\.[a-z]+)?\.lhr\.life' /tmp/tunnel.log | tail -1)
  if [ -n "$HOST" ]; then
    echo "Alamat tunnel: https://$HOST"
    exit 0
  fi
done
echo "GAGAL. Baris yang mengandung 'life':"
grep -a "life" /tmp/tunnel.log
echo "--- 30 baris terakhir:"
tail -30 /tmp/tunnel.log
exit 1
