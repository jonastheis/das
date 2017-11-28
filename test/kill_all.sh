#!/usr/bin/env bash

ps aux | grep -ie "-m server.app" |  awk '{print $2}'  |  xargs sudo kill -9
ps aux | grep -ie "-m client.app" |  awk '{print $2}'  |  xargs sudo kill -9