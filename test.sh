docker rm -f lm-collector || true
docker build -t collector:latest .
docker run --name lm-collector -d \
  --hostname host-1 \
  -e account=jeffwozniak \
  -e access_id=7nxdH9Cb9c3SfcpF4q2j \
  -e access_key='c$9Zy7$4Vt}HwYSz6N8y^8RVsT%]P2^9+774q^R2' \
  -e collector_size=nano \
  -e COLLECTOR_IDS="1,2" \
  -e description='My Dockerized Collector test3' \
  -e cleanup=true \
  -e use_ea=false \
collector:latest

docker logs -f lm-collector


# docker rm -f lm-collector || true
# docker build -t collector:latest .
# docker run --name lm-collector -ti \
#   --entrypoint bash \
#   --hostname host-1 \
#   -e account=jeffwozniak \
#   -e access_id=7nxdH9Cb9c3SfcpF4q2j \
#   -e access_key='c$9Zy7$4Vt}HwYSz6N8y^8RVsT%]P2^9+774q^R2' \
#   -e collector_size=nano \
#   -e COLLECTOR_IDS="1,2" \
#   -e description='My Dockerized Collector' \
#   -e cleanup=true \
#   -e use_ea=true \
# collector:latest
