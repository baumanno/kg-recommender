#!/usr/bin/env bash

set -Eeuo pipefail
trap cleanup SIGINT SIGTERM ERR EXIT

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

usage() {
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") [-h] [-v] INDIR TOTALTRACKS

Tabulate distinct tracks.

Distinct tracks are per user, i.e., how many distinct tracks did a user listen to.

This script reads all files in INDIR, and distributes them to an AWK-script via
GNU parallel. The distinct track counts are written to TOTALTRACKS for subsequent
sampling..

Required arguments:

INDIR         Directory containing the per-user tracklists (see 03_tracks_per_user.sh)
TOTALTRACKS   Path to the CSV-file to write the distinct track-counts to.

Available options:

-h, --help        Print this help and exit
-v, --verbose     Print script debug info
--no-color        Turn off output colours
EOF
  exit
}

cleanup() {
  trap - SIGINT SIGTERM ERR EXIT
  # script cleanup here
}

setup_colors() {
  if [[ -t 2 ]] && [[ -z "${NO_COLOR-}" ]] && [[ "${TERM-}" != "dumb" ]]; then
    NOFORMAT='\033[0m' RED='\033[0;31m' GREEN='\033[0;32m' ORANGE='\033[0;33m' BLUE='\033[0;34m' PURPLE='\033[0;35m' CYAN='\033[0;36m' YELLOW='\033[1;33m'
  else
    NOFORMAT='' RED='' GREEN='' ORANGE='' BLUE='' PURPLE='' CYAN='' YELLOW=''
  fi
}

msg() {
  echo >&2 -e "${1-}"
}

die() {
  local msg=$1
  local code=${2-1} # default exit status 1
  msg "$msg"
  exit "$code"
}

parse_params() {

  while :; do
    case "${1-}" in
    -h | --help) usage ;;
    -v | --verbose) set -x ;;
    --no-color) NO_COLOR=1 ;;
    -?*) die "Unknown option: $1" ;;
    *) break ;;
    esac
    shift
  done

  args=("$@")

  # check required params and arguments
  [[ ${#args[@]} -lt 2 ]] && die "Missing script arguments: INDIR, TOTALTRACKS required"

  return 0
}

run() {
  msg "${RED}Read arguments:${NOFORMAT}"
  msg "- INDIR: ${args[0]}"
  msg "- TOTALTRACKS: ${args[1]}"
  
  msg "${GREEN}Running tabulation...${NOFORMAT}"
  msg "${YELLOW}This may take a while, grab a beverage.${NOFORMAT}"
  
    find ${args[0]} \
      -type f \
      -name "*.csv" \
      -print0 \
    | parallel \
      -q0 \
      --eta \
    awk '
BEGIN {
    FS = ",";
    OFS = ",";
}
# Skip the header line
NR>1 {
    tcount[$2] += 1;
}
END {
    print $1, length(tcount) >> "'${args[1]}'";
}'
    
  msg "${GREEN}Pipeline complete${NOFORMAT}"
}

parse_params "$@"
setup_colors

# script logic here
run