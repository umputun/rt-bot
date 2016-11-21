#/bin/sh
cd /srv/rt-bot
# export DOCKER_HOST=unix:///var/run/docker.sock

echo "deploy bots"
/usr/bin/docker-compose ps
/usr/bin/docker-compose pull
/usr/bin/docker-compose up -d
/usr/bin/docker-compose ps
/usr/bin/docker images --no-trunc | grep none | awk "{print \$3}" | xargs /usr/bin/docker rmi
echo "all done"
