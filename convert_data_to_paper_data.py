import os
from random import shuffle
import json
import re

langs = ["en", "de", "it", "ja"]
for lang in langs:
    source_file = f"./scraper/data/{lang}_definitions.jsonl"
    if os.path.exists(source_file):
        print(f"Processing {source_file}")
        with open(source_file) as f:
            words_with_definitions = [json.loads(line) for line in f]

        words = [w[0] for w in words_with_definitions]
        shuffle(words_with_definitions)

        train_size = int(len(words_with_definitions) * 0.7)
        train = words_with_definitions[:train_size]
        val = words_with_definitions[
            train_size : train_size + int(len(words_with_definitions) * 0.1)
        ]
        test = words_with_definitions[
            train_size + int(len(words_with_definitions) * 0.1) :
        ]

        def remove_text_between_parentheses(text: str) -> str:
            return re.sub(r"\([^)]*\)", "", text).strip()

        train_definitions = "\n".join(
            [
                f"{w[0]}\t{remove_text_between_parentheses(w[1])}"
                for w in words_with_definitions
            ]
        )
        val_definitions = "\n".join(
            [f"{w[0]}\t{remove_text_between_parentheses(w[1])}" for w in val]
        )
        test_definitions = "\n".join(
            [f"{w[0]}\t{remove_text_between_parentheses(w[1])}" for w in test]
        )
        words_txt = "\n".join(words)

        os.makedirs("./new_data_like_paper/mix", exist_ok=True)

        with open(f"./new_data_like_paper/mix/{lang}_dev.csv", "w") as f:
            f.write(val_definitions)

        with open(f"./new_data_like_paper/mix/{lang}_test.csv", "w") as f:
            f.write(test_definitions)

        with open(f"./new_data_like_paper/mix/{lang}_train.csv", "w") as f:
            f.write(train_definitions)

        with open(f"./new_data_like_paper/mix/{lang}.txt", "w") as f:
            f.write(words_txt)

        print(f"{len(words)}")
