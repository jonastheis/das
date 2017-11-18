#!/usr/bin/env bash

ps aux | grep -ie "-m server.network.server" |  awk '{print $2}'  |  xargs sudo kill -9
ps aux | grep -ie "-m test.simple" |  awk '{print $2}'  |  xargs sudo kill -9