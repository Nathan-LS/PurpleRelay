#!/usr/bin/env bash
eval $(dbus-launch --auto-syntax)
screen -dmS finch finch || exit 1
cp /opt/PurpleRelay/routes-example.json /app/routes-example.json
exec "$@"
