BEGIN{
  rel_file=outdir"/relations_id.txt"
  print "id", "relation" > rel_file
  ent_file=outdir"/entities_id.txt"
  print "id", "entity" > ent_file
  itm_file=outdir"/items_id.txt"
  print "id", "item" > itm_file
  KG_file=outdir"/kg_final.txt"
  n_ent=0
  n_rel=0
}
FNR == 1 { ++fIndex 
n=split(FILENAME,fnarray,"/")
file=fnarray[n]
}
file == "filter_predicates" { # using filename here to prevent breakage through empty files
  filter_predicates[$0];next
} 
file == "filter_relations"{ # using filename here to prevent breakage through empty files
  filter_relations[$0];next
}
fIndex == 3 { # first iteration of KG.ttl file to track items and obtain in-&out-degrees
  if ( $0 ~ /^\s*$/ ) next; # skip empty lines
  if ( $3 ~ /"/ ) next; # only for triples where the object isn't some string
  if ( $1 ~ /@prefix/ ) next; # skip lines with namespace definitions
  # we skip considering filter-files here to make sure to capture all the items at the cost of tracking a few unnecessary in-&out-degrees
    
  entity_counter_out[$1] += 1 # counting out degree
  entity_counter_in[$3] += 1  # counting in degree
  
  # if subject is of type nfs:s1234 we have found an item
  if ( $1 ~ /nfs:s[[:digit:]{1,4}]/ && !($1 in items) ){
    items[$1]=n_ent
    ent[$1]=n_ent
    print n_ent, $1 >> itm_file
    print n_ent, $1 >> ent_file
    n_ent++
  }
  
  next
}
fIndex == 4 { # second iteration of same KG.ttl file to obtain KG with IDs
  # same filtering as above
  if ( $0 ~ /^\s*$/ ) next; # skip empty lines
  if ( $3 ~ /"/ ) next; # only for triples where the object isn't some string
  if ( $1 ~ /@prefix/ ) next; # skip lines with namespace definitions
  if ( $1 in filter_predicates ) next; # filter predicates and relations
  if ( $2 in filter_relations ) next;
  if ( $3 in filter_predicates ) next;
  
  # filter out things with out-degree of at least min_degree_out, but keep all items!
  if ( !($1 in items) && (entity_counter_out[$1] < min_degree_out) ) next;
  # filter out things with in-degree of at least min_degree_in, but keep all items!
  if ( !($1 in items) && (entity_counter_in[$3] < min_degree_in) ) next;

  if ( !($1 in items) && !($1 in ent)){ # track unseen entities
    ent[$1]=n_ent
    print n_ent, $1 >> ent_file
    n_ent++
  }
  
  if (!($2 in rel)){ # keep track of relations
    rel[$2]=n_rel
    print n_rel, $2 >> rel_file
    n_rel++
  }
  
  if ( !($3 in items) && !($3 in ent)){ # track unseen entities
    ent[$3]=n_ent
    print n_ent, $3 >> ent_file
    n_ent++
  }
  
  print ent[$1],rel[$2],ent[$3] >> KG_file
}
