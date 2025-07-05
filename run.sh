#!/usr/bin/env bash

set -e
cd "$(dirname "$0")"

help() {
  cat <<EOF
Usage:
  ./run.sh --docker <subcommand>
  ./run.sh --download <all|datasets|models>
  ./run.sh --help

Options:
  --docker         Run DockerManager commands (build, run, exec)
  --download       Run ResourceFetcher to download resources
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

download() {
  echo "[INFO] Invoking ResourceFetcher with command: $*"
  python3 ./src/resource_fetcher.py "$@"
}

if [[ $# -eq 0 ]]; then
  help
  exit 0
fi

case "$1" in
  --docker)
    docker "$@"
    ;;
  --download)
    download "$@"
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
