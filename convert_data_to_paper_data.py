import os
from random import shuffle
import ipdb
import json
import re
import translators as ts

add_semantic_info = True 
add_sentence_example = False 


def remove_text_between_parentheses(text: str) -> str:
    return re.sub(r"\([^)]*\)", "", text).strip()


langs = [
    "de",
    "it",
    "ja",
]
for lang in langs:
    source_file = f"./scraper/data/{lang}_definitions.jsonl"
    if os.path.exists(source_file):
        print(f"Processing {source_file}")
        words_with_definitions = []
        with open(source_file, errors="ignore") as f:
            for line in f:
                if line.strip() == "":
                    continue
                try:
                    words_with_definitions.append(json.loads(line))
                except:
                    print(f"Error in {line}")
                    continue
        print(f"LEN: {len(words_with_definitions)}")

        unique_words = list(set([w[0] for w in words_with_definitions]))
        shuffle(unique_words)

        train_size = int(len(unique_words) * 0.7)
        val_size = int(len(unique_words) * 0.15)
        train_words = set(unique_words[:train_size])
        val_words = set(unique_words[train_size : train_size + val_size])
        test_words = set(unique_words[train_size + val_size :])
        print(
            f"""
        Words:
            Train: {len(train_words)}
            Val: {len(val_words)}
            Test: {len(test_words)}
        """
        )

        train = [w for w in words_with_definitions if w[0] in train_words]
        val = [w for w in words_with_definitions if w[0] in val_words]
        test = [w for w in words_with_definitions if w[0] in test_words]

        tot_ds = train + val + test
        words = list(set([w[0] for w in tot_ds]))

        print(
            f"""
        Definitions:
            Train: {len(train)}
            Val: {len(val)}
            Test: {len(test)}
        """
        )
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

        print(f"{lang} {len(words)}")

        if lang != "en":
            with open(
                f"./untranslatable_word_dataset/{lang if lang != 'it' else 'ita'}.json"
            ) as f:
                cross = json.load(f)
            target_words = [
                w.strip()
                for w in (cross["Word"] if "Word" in cross else cross["Ideogram"])
            ]
            synonyms = (
                cross["Synonyms"] if "Synonyms" in cross else cross["English synonyms"]
            )
            new_synonyms = []
            for w, syn in zip(target_words, synonyms):
                if isinstance(syn, float):
                    syn = []
                if len(syn) == 0:
                    print(f"Translating {w}")
                    res = ts.translate_text(w, to_language="en")
                    new_synonyms.append([res])
                else:
                    new_synonyms.append(syn)
            eng_word = [syn[0] for syn in new_synonyms]
            cross_definitions_eng = [d.strip() for d in cross["Definition ENG"]]
            if add_semantic_info:
                cross_definitions_eng = [
                    f"{d + '.' if not d.endswith('.') else ''} Semantic field:{s}"
                    for d, s in zip(cross_definitions_eng, cross["Semantic field"])
                ]
            if add_sentence_example:
                cross_definitions_eng = [
                    f"{d + '.' if not d.endswith('.') else ''} Example:{s}"
                    for d, s in zip(cross_definitions_eng, cross["Example"])
                ]
            def_target_key = [
                k
                for k in list(cross.keys())
                if ("Definition" in k) and (lang in k.lower().split()[1])
            ]
            if len(def_target_key) == 0:
                def_target_key = "Definition JPN"
            else:
                def_target_key = def_target_key[0]
            cross_definitions_target = cross[def_target_key]
            en_target_ds = []
            for vals in zip(target_words, eng_word, cross_definitions_target):
                try:
                    en_target_ds.append("\t".join(vals))
                except:
                    print(f"Error in {vals}")
                    continue
            en_target_ds = "\n".join(en_target_ds)
            # en_target_ds = "\n".join(
            #     [
            #         "\t".join(vals)
            #         for vals in zip(target_words, eng_word, cross_definitions_target)
            #     ]
            # )

            target_en_ds = []
            for vals in zip(eng_word, target_words, cross_definitions_eng):
                try:
                    target_en_ds.append("\t".join(vals))
                except:
                    print(f"Error in {vals}")
                    continue
            target_en_ds = "\n".join(target_en_ds)
            # target_en_ds = "\n".join(
            #     [
            #         "\t".join(vals)
            #         for vals in zip(eng_word, target_words, cross_definitions_eng)
            #     ]
            # )
            with open(f"./new_data_like_paper/mix/{lang}_en_test.csv", "w") as f:
                f.write(target_en_ds)

            with open(f"./new_data_like_paper/mix/en_{lang}_test.csv", "w") as f:
                f.write(en_target_ds)
