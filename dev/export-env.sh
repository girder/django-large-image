# Export environment variables from the .env file in the first argument.
# If no argument is given, default to "dev/.env.docker-compose-native".
# This file must be sourced, not run.

if [ -n "$1" ]; then
  # If an argument was provided, use it as the .env file
  _dotenv_file="$1"
else
  # Otherwise, use the default .env file
  if [ -n "$ZSH_VERSION" ]; then
    # ZSH has a different way to get the directory of the current script
    _dotenv_dir="$0:A:h"
  else
    # Assume this is Bash
    _dotenv_dir="$( dirname "${BASH_SOURCE[0]}" )"
  fi
  _dotenv_file="${_dotenv_dir}/.env.docker-compose-native"
fi

# Export all assignments in the $_dotenv_file
# Using "set -a" allows .env files with spaces or comments to work seamlessly
# https://stackoverflow.com/a/45971167
set -a
. "$_dotenv_file"
set +a

# Clean up, since sourcing this leaks any shell variables
unset _dotenv_dir
unset _dotenv_file
