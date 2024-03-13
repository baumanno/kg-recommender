BEGIN {
  n_items = 0
}
FNR == 1 { ++fIndex 
  n=split(FILENAME,fnarray,"/")
  file=fnarray[n]
}
file == "items_id.txt" { # to prevent breakage through empty files
  id = gensub(/nfs:/,"", "g", $2)
  known_items[id] = $1;next
} 
fIndex == 2{
  if (FNR > 1 && ($1 in known_items)) {
    items[n_items] = known_items[$1]
    n_items++
  }
}
END {
  n_train = int(trainsplit*n_items)
  for (i in items){
    if ( int(i) < n_train ){
      printf "%s ", items[i] >> trainfile
    }else{
      printf "%s ", items[i] >> testfile
    }
  }
  printf "\n" >> trainfile
  printf "\n" >> testfile
}
