#!/bin/bash

flags=""
config_file=""

source scripts/functions.sh

py=$(get_python)
env_path=$(get_env_path)

source $env_path
echo "Virtual environment was successfully activated."

while [[ $# -gt 0 ]]; do
  case "$1" in
  --config_file)
    flags="$1"
    shift
    config_file="$1"
    shift
    ;;
  *)
    echo "Unknown option: $1"
    exit 1
    ;;
  esac
  shift
done

echo "Config file: $config_file"

if [ -z "$config_file" ]; then
  echo "Error: Config file argument is an empty string or null."
  exit 1
fi

if [ ! -f "$config_file" ]; then
  echo "Error: Config file argument is not a valid file path."
  exit 1
fi

cmd="$py src/main.py --config_file $config_file"
echo "Running command: $cmd"
eval "$cmd"