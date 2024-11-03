#!/bin/bash

set -e

#
uwsgi twitfix.ini &

# nginx
nginx -g "daemon off;"
