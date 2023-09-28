import json
import os
import ipdb
import numpy as np

langs = ["ita", "de", "ja"]

for lang in langs:
    with open(f"./{lang}.json") as f:
        current_lang = json.load(f)

    pred_file_name = f"./backup/no_clue_{lang}_predictions.json"
    with open(pred_file_name) as f:
        predictions = [json.loads(l) for l in f.readlines() if l.strip()]

    words = [
        w.strip().lower()
        for w in (
            current_lang["Word"] if "Word" in current_lang else current_lang["Ideogram"]
        )
    ]
    if len(words) != len(predictions):
        print(f"{lang} {len(words)} != {len(predictions)}")
        continue
    resuts = [
        [w == p1["word"].lower(), w == p2["word"].lower()]
        for w, (p1, p2) in zip(words, predictions)
    ]
    results = np.array(resuts)
    print(f"{lang} {results.mean(axis=0)}")
