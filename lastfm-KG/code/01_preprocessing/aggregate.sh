#!/usr/bin/env bash

set -Eeuo pipefail
trap cleanup SIGINT SIGTERM ERR EXIT

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

usage() {
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") [-h] [-v] TMPDIR TOTALCOUNTS

Aggregate local and global playcounts

Local playcounts are how often a single user listened to an individual track;
this is used for generating implicit rating data later on.
Global playcounts are the number of unique tracks a user played; these are used
for filtering users based on number of unique tracks.

Required arguments:

TMPDIR      The directory to store the temporary, split histories
TOTALCOUNTS The file to write the unique track-counts per user

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
  [[ ${#args[@]} -lt 2 ]] && die "Missing script arguments: TMPDIR, TRACKCOUNTS required"

  tmpdir=${args[0]}
  trackcounts=${args[1]}

  return 0
}

run() {
  msg "${RED}Read arguments:${NOFORMAT}"
  msg "- TMPDIR: ${tmpdir}"
  msg "- TRACKCOUNTS: ${trackcounts}"
  msg ""
  
  msg "Aggregating playcounts"

    find ${tmpdir} -type f -name "*.hist.csv" -print0 \
      | parallel -q0 --eta \
      awk '
BEGIN {
  FS=","
  OFS=","
  user_track_count[""]=0
  user_total[""]=0
  seen[""]=0
}
NR>1 {
  user=$1
  artist=$2
  track=$4

  # count how often this user listened to a track
  # keep `user` in the index to be able to write it as a column to the output
  idx_track_count=user "," track
  user_track_count[idx_track_count]++

  # count unique instances of tracks, i.e., "how many distinct tracks were listened to"
  if (!(track in seen)) {
    seen[track]++
    user_total[user]++
  }
}
END {
  for (ut in user_track_count) {
    if (ut != "") {
      print ut, user_track_count[ut] > "'${tmpdir}/'" user ".playcounts.csv"
    }
  }

  # Print number of unique tracks
  for (u in user_total) {
    if (u != "") {
      print u, user_total[u] >> "'${trackcounts}'"
    }
  }
}
'
    # insert a header into the track-counts file; `-i` for in-place, `1i` addresses line 1 and [i]nserts
    sed -i '1iuser_id,n_uniq_tracks' "${trackcounts}"

  msg "${GREEN}Done!${NOFORMAT}"
}

parse_params "$@"
setup_colors

# script logic here
run
