#!/usr/bin/env bash

set -e
cd "$(dirname "$0")"

help() {
  cat <<EOF
Usage:
  ./run.sh --docker <subcommand>
  ./run.sh --help

Options:
  --docker         Run DockerManager commands (build, run, exec)
  --help, -h       Show this help message
EOF
}

docker() {
  shift
  if [[ $# -eq 0 ]]; then
    echo "[ERROR] Missing subcommand for --docker. Expected: build, run, or exec."
    echo
    help
    exit 1
  fi

  echo "[INFO] Invoking DockerManager with command: $*"
  python3 ./src/docker_manager.py "$@"
}

if [[ $# -eq 0 ]]; then
  help
  exit 0
fi

case "$1" in
  --docker)
    docker "$@"
    ;;
  --help|-h)
    help
    ;;
  *)
    echo "[ERROR] Unknown option: $1"
    echo
    help
    exit 1
    ;;
esac
