#!/bin/bash
# Double-click this on the Mac mini to open the station.
#
# Starts the local server (if it is not already up), stops the screen sleeping,
# and opens Chrome in kiosk mode pointed at it. Closing Chrome (cmd-Q) leaves
# the server running; run stop-station.command to shut everything down.

set -u
cd "$(dirname "$0")" || exit 1

PORT="${STATION_PORT:-8777}"
URL="http://127.0.0.1:${PORT}/"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

echo "Odia language station"
echo

# --- server ---------------------------------------------------------------
if curl -fsS "${URL}api/health" >/dev/null 2>&1; then
  echo "server   already running on ${PORT}"
else
  echo "server   starting…"
  nohup python3 server.py serve > station.log 2>&1 &
  for _ in $(seq 1 25); do
    sleep 0.4
    curl -fsS "${URL}api/health" >/dev/null 2>&1 && break
  done
  if curl -fsS "${URL}api/health" >/dev/null 2>&1; then
    echo "server   up on ${PORT}  (log: station.log)"
  else
    echo "server   FAILED to start. Last lines of station.log:"
    tail -15 station.log
    echo
    read -r -p "Press return to close."
    exit 1
  fi
fi

# --- preflight ------------------------------------------------------------
echo
python3 server.py check
echo

# --- keep the machine awake while the station is up -----------------------
if ! pgrep -f "caffeinate -dimsu" >/dev/null 2>&1; then
  nohup caffeinate -dimsu > /dev/null 2>&1 &
  echo "display  sleep disabled (caffeinate)"
fi

# --- browser --------------------------------------------------------------
if [ ! -x "$CHROME" ]; then
  echo "Chrome not found at $CHROME — opening your default browser instead."
  open "$URL"
else
  echo "browser  opening Chrome in kiosk mode"
  echo
  echo "  To leave kiosk mode: cmd-Q."
  echo "  The first run will ask for microphone permission — say yes."
  echo
  "$CHROME" --kiosk --app="$URL" \
    --user-data-dir="$HOME/Library/Application Support/OdiaStation" \
    --autoplay-policy=no-user-gesture-required \
    --disable-features=TranslateUI,ChromeWhatsNewUI \
    --no-first-run --no-default-browser-check \
    >/dev/null 2>&1
fi

echo
echo "Chrome closed. The server is still running (stop-station.command to stop it)."
