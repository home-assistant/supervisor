#!/bin/bash
set -e

udevd --daemon
udevadm trigger

if CMD="$(command -v "$1")"; then
  shift
  exec "$CMD" "$@"
else
  echo "Command not found: $1"
  exit 1
fi
