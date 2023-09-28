import json
import os
import ipdb
import random


def load_data(folder: str, relative_train_size: float = 0.7) -> dict:
    file_names = [fn for fn in os.listdir(folder) if fn.endswith(".json")]
    contents = {
        fn.split(".")[0]: json.load(open(os.path.join(folder, fn), "r"))
        for fn in file_names
    }

    result = {}
    for lang, content in contents.items():
        key = [k for k in content.keys() if k.startswith("Word")][0]
        unique_words = list(set(content[key]))
        print(f"{lang} : {len(unique_words)=}")
        train_size = int(len(unique_words) * relative_train_size)
        test_size = (len(unique_words) - train_size) // 2
        random.shuffle(unique_words)
        train_words = unique_words[:train_size]
        test_words = unique_words[train_size : train_size + test_size]
        val_words = unique_words[train_size + test_size :]
        train_mask = [word in train_words for word in content[key]]
        test_mask = [word in test_words for word in content[key]]
        val_mask = [word in val_words for word in content[key]]
        result[lang] = {
            "train": {
                key: [value[i] for i, mask in enumerate(train_mask) if mask]
                for key, value in content.items()
            },
            "test": {
                key: [value[i] for i, mask in enumerate(test_mask) if mask]
                for key, value in content.items()
            },
            "val": {
                key: [value[i] for i, mask in enumerate(val_mask) if mask]
                for key, value in content.items()
            },
        }
    return result


if __name__ == "__main__":
    load_data("./MyUWD/")
