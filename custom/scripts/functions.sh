#!/bin/bash

check_library() {
  local desired_library="$1"
  if pip show "$desired_library" >/dev/null 2>&1; then
    return 0
  else
    return 1
  fi
}

install_libraries() {
  local requirements_file="$1"
  while IFS= read -r line; do
    library=$(echo "$line" | cut -d '=' -f 1)
    if pip show "$library" >/dev/null 2>&1; then
      echo "$library is already installed."
    else
      echo "$library is not installed."
      echo "Installing $library..."
      pip install "$line"
    fi
  done <"$requirements_file"
}

check_env_exists() {
  if [ -d "env" ]; then
    return 0
  else
    return 1
  fi
}

get_python() {
  if [ "$(uname)" == "Darwin" ] || [ "$(uname)" == "Linux" ]; then
    echo "python3"
  else
    echo "python"
  fi
}

get_env_path() {
  if [ "$(uname)" == "Darwin" ] || [ "$(uname)" == "Linux" ]; then
    echo "env/bin/activate"
  else
    echo "env/Scripts/activate"
  fi
}