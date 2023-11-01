# Netflix Knowledge Graph

Generates a KG from the netflix catalog obtained from [kaggle](https://www.kaggle.com/datasets/shivamb/netflix-shows) (As of Oct. 2023).

## Instructions:

The input data is available in the *data/raw/* directory. In case it is compressed (*.xz files), it will be necessary to extract it first.

### 1. Generating the base KG:

```bash
$ cd code/
$ genBaseKGs.sh
```
The KG will be available in the *data/processed* directory, both in Turtle (*.ttl) and GraphML (*.graphml) formats.

### 2. Generating random user profiles:

Two parameters are required. The amount of user profiles to be generated, a minimum and a maximum of entries that will be randomly generated per user. Below we generate 88 user profiles, with a minimum of 5 entries and a maximum of 55 entries.

```bash
$ cd code/
$ genUserProfiles.sh 88 5 55
```
The profiles will be available in the *data/processed* directory, in CSV (*.csv) format.

### 3. Generating KGs for the (previously) generated user profiles:

```bash
$ cd code/
$ genUserProfilesKGs.sh
```

The user profile KGs will be available in the *data/processed* directory, both in Turtle (*.ttl) and GraphML (*.graphml) formats.

