#!/bin/bash
# Shut the station down: the local server, and the sleep-blocker.
cd "$(dirname "$0")" || exit 1

pkill -f "server.py serve" && echo "server      stopped" || echo "server      was not running"
pkill -f "caffeinate -dimsu" && echo "caffeinate  stopped" || echo "caffeinate  was not running"
echo
echo "Chrome, if it is still open, can be quit with cmd-Q."
