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
Code found in `./train_model` is an adaptation of [BertForRD](https://github.com/yhcc/BertForRD).
