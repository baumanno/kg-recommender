#!/usr/bin/env bash

set -Eeuo pipefail
trap cleanup SIGINT SIGTERM ERR EXIT

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

usage() {
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") [-h] [-v] LFMPATH TRACKSPATH DEST

Filter the large LFM-1b dataset against a list of track-IDs to include.

This script is intended to extract the subset of listening events that include
tracks for which rich audio features are available. It requires both the raw
LFM-1b dataset, as well as a CSV-file with the track-IDs to include.

Required arguments:

LFMPATH          Path to the raw LFM-1b listening events
TRACKSPATH       Path to the CSV-file containing track-IDs to include
DEST             Destination path to write to

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
  [[ ${#args[@]} -lt 3 ]] && die "Missing script arguments: LFMPATH, TRACKSPATH, DEST required"
  
  lfmpath=${args[0]}
  trackspath=${args[1]}
  destination=${args[2]}

  return 0
}

run() {
  msg "${RED}Read arguments:${NOFORMAT}"
  msg "- LFMPATH: ${lfmpath}"
  msg "- TRACKSPATH: ${trackspath}"
  msg "- DEST: ${destination}"
  
  msg "Running pipeline"
  msg "${YELLOW}This may take a while, grab a beverage.${NOFORMAT}"
  
  xzcat ${lfmpath} | \
    awk '
BEGIN {
  FS=",";
  a[""] = 0;
}

NR == FNR {
    a[$2] = 0;
    next;
}
{
  FS="\t";
  $0 = $0;
}
$4 in a {print}' ${trackspath} - \
    > ${destination}
    
  msg "${GREEN}Pipeline complete"
}

parse_params "$@"
setup_colors

# script logic here
run