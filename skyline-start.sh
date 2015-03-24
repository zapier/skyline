#!/bin/bash

redis-server /opt/skyline/bin/redis.conf
horizon.d start
analyzer.d start
webapp.d start

#benefits of emitting logs: make available via docker logs command; hold process open so docker keeps the port open and process running
tail -f /var/log/skyline/*
