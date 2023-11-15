#!/usr/bin/env bash

set -Eeuo pipefail
trap cleanup SIGINT SIGTERM ERR EXIT

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

usage() {
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") [-h] [-v] TRACKSPATH LESPATH DEST

Extract users' tracks into individual files.

This script first replaces all single IDs with the correct compound ID, and then
extracts each user's listening history into one file per user. This intermediate
step is required for subsequently tabulating total counts and playcounts (which
requires too much memory to do in a single pass).

Note that artist-ID, album-ID, and timestamp are not retained!

Required arguments:

TRACKSPATH  Path to the CSV-file containing track-IDs to include
LESPATH     Path to the CSV-file containing the listening events extracted
            from the raw LFM-1b data (see 02_filter_les.sh)
DEST        Destination path to write to

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
  [[ ${#args[@]} -lt 3 ]] && die "Missing script arguments: TRACKIDS, LES, DEST required"

  return 0
}

run() {
  msg "${RED}Read arguments:${NOFORMAT}"
  msg "- TRACKIDS: ${args[0]}"
  msg "- LES: ${args[1]}"
  msg "- DEST: ${args[2]}"
  msg ""
  
  msg "Running extraction"
  msg "${YELLOW}This may take a while, grab a beverage.${NOFORMAT}"
  
    awk '
BEGIN {
    FS=",";
    OFS=",";
    header_once[""] = 0;
}
NR == FNR {
    a[$2] = $1;
    next;
}
{
    FS="\t";
    $0=$0;
}
$4 in a {
    outfile = "'${args[2]}'/" $1 ".csv";
    $4 = a[$4];
    if (!($1 in header_once)) {
      header_once[$1] = 0;
      print "user", "compound", "count" > outfile;
    }
    print $1, $4, "1" >> outfile;
}
    ' ${args[0]} ${args[1]}
    
  msg "${GREEN}Pipeline complete${NOFORMAT}"
}

parse_params "$@"
setup_colors

# script logic here
run