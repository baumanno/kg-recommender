#!/usr/bin/env bash

set -Eeuo pipefail
trap cleanup SIGINT SIGTERM ERR EXIT

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

usage() {
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") [-h] [-v] USERS COUNTSDIR OUTFILE

Extract the playcounts for specific users.

This script extracts playcounts for users contained in the file specified by USERS.
USERS will likely contain a sample of a larger population.

For the users specified in USERS, the corresponding unstructured profile in COUNTSDIR
is read, and the tracks therein are tabulated to arrive at per-track playounts.

These profiles are then written to OUTFILE.

Required arguments:

USERS       Path to the CSV-file containing the users.
COUNTSDIR   The directory where the unstructured profiles reside 
            (see code/01_preprocessing/04_user_profiles/03_tracks_per_user.sh)
OUTFILE     Path to the CSV-file to write the per-user playcounts to.

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
  [[ ${#args[@]} -lt 3 ]] && die "Missing script arguments: USERS, COUNTSDIR, OUTFILE required"

  return 0
}

run() {
  msg "${RED}Read arguments:${NOFORMAT}"
  msg "- USERS:     ${args[0]}"
  msg "- COUNTSDIR: ${args[1]}"
  msg "- OUTFILE:   ${args[2]}"
  
  msg "${GREEN}Running extraction...${NOFORMAT}"
  msg "${YELLOW}This may take a while, grab a beverage.${NOFORMAT}"
  
  users=$(awk '
BEGIN {
  FS=",";
}
NR > 1 { print $1; }
  ' ${args[0]})
  
  printf "${args[1]}%s.csv\0" $users | parallel -q0 --eta \
  awk '
BEGIN {
  FS=",";
  OFS=",";
}
NR > 1 {
  plays[$2]++;
  u = $1;
}
END {
  for (p in plays) {
    print u, p, plays[p];
  }
}' |
awk '
BEGIN {
  OFS = ",";
  print "uid", "compound", "count";
}
{ print $0; }
' > ${args[2]}

    
  msg "${GREEN}Extraction complete${NOFORMAT}"
}

parse_params "$@"
setup_colors

# script logic here
run