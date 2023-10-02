# Project's overview
The following repository provides the full code in Python to a mBERT-based reverse dictionary (RD) for German, Italian and Japanese  words.

## Dataset folders

Besides the full script, two folders containing the datasets used for the implementation are here given: "MyMono" and "MyUWD". For a detailed description, please consult the corresponding READme files within each folder.

## Reproducing the result

Clone this repo and navigate into its home directory. Also make sure
[Bun](https://bun.sh/) is installed.

### Run the scraper

From within the `./scraper` directory run:

```bash
python filter_words.py
```

```bash
bun scraper.ts
```

### Prepare the data

From within the home director of the repo

```bash
python convert_data_to_paper_data.py
```

### Train the model

Set the hyperparameters in the file `./train_model/mix/train_pair_bert.py`. Then run:

```bash
python -m train_model.mix.train_pair_bert
```

## Notes
Code found in `./train_model` is an adaptation of [BertForRD](https://github.com/yhcc/BertForRD). Indeed, this project consists of a replication of Yan and colleagues' (2020) experiment on a crosslingual, unaligned RD. 
The paper of reference can be found at the following link https://aclanthology.org/2020.findings-emnlp.388/. 
As for the full original code, this is available on github at https://github.com/yhcc/BertForRD.git 
