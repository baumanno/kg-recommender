# Knowledge Graph Recommender

Generates recommendations for user-profile Knowledge Graphs, based on items from a catalog Knowledge Graph, and a metric.

## Generating Recommendations:

Run the python script as described below. The metrics param (-m) takes a comma-separated list of metrics. The script takes a single catalog KG file, and multiple (space-separated) user-profile KG files.

### Instructions

```bash
$ python3 recommend.py -m [metric1,metric2,...] [catalog file KG (*.ttl)] [user profile KG file (*.ttl)] <user profile KG file (*.ttl)> ...
```
The recommendation list will be output to a text file.

Example:
```bash
$ python3 recommend.py -m closeness,degree catalog.ttl user-profile01.ttl userprofile02.ttl userprofile03.ttl
```

### Help

Just run the following command:

```bash
$ python3 recommend.py -h
```

