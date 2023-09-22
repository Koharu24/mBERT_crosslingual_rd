import os
import json
from fastNLP.io import Loader, DataBundle
from fastNLP import Instance, DataSet
import ipdb


def read_dataset(path, lower, word_idx=1, def_idx=-1):
    ds = DataSet()
    import ipdb

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            # if len(line.split("\t")) > 2:
            #     ipdb.set_trace()
            line = line.strip()

            if line:
                parts = line.split("\t")
                if lower:
                    ins = Instance(
                        word=parts[word_idx].lower(), definition=parts[def_idx].lower()
                    )
                else:
                    ins = Instance(word=parts[word_idx], definition=parts[def_idx])
                ds.append(ins)
    return ds


class BiUnAlignLoader(Loader):
    """
    非监督的双语

    """

    def __init__(self, lg1_lg2, lower=True):
        # lg1是target_language
        super().__init__()
        # assert lg1_lg2 in ("en_es", "en_fr")
        self.lg1_lg2 = lg1_lg2
        self.lower = lower

    def load(self, folder):
        #  首先读取两个单语文件
        lg1, lg2 = self.lg1_lg2.split("_")
        fns = {
            "dev": "{}_dev.csv",
            # 'test':'{}_test500.csv'.format(self.lg1_lg2),
            "train": "{}_train.csv",
        }
        data_bundle = DataBundle()
        words = {}
        for lg in [lg1, lg2]:
            for name, fn in fns.items():
                path = os.path.join(folder, fn.format(lg))
                ds = read_dataset(path, self.lower, 0)
                data_bundle.set_dataset(ds, name=f"{lg}_{name}")
            target_words = {}
            with open(os.path.join(folder, "{}.txt".format(lg)), encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        if self.lower:
                            line = line.lower()
                        target_words[line] = 1
            target_words = list(target_words.keys())
            words[lg] = target_words

        bi1 = f"{lg1}_{lg2}"
        bi2 = f"{lg2}_{lg1}"
        for bi in [bi1, bi2]:
            l1, l2 = bi.split("_")
            path = os.path.join(folder, "{}_test.csv".format(bi))
            ds = read_dataset(path, self.lower, 1)
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split("\t")
                        w1 = parts[0].lower().strip()
                        words[l2].append(w1)
                        w2 = parts[1].lower().strip()
                        words[l1].append(w2)

            data_bundle.set_dataset(ds, "{}_test".format(bi))

        new_words = {}
        for key, val in words.items():
            new_words[key] = list(set(val))
        words = new_words
        setattr(data_bundle, "target_words_dict", words)

        return data_bundle


class MixUnAlignLoader(Loader):
    #
    def __init__(self, lower=True):
        super().__init__()
        self.lower = lower

    def load(self, folder):
        data_bundle = DataBundle()
        fns = {
            "dev": "{}_dev.csv",
            # 'test':'{}_test500.csv'.format(self.lg1_lg2),
            "train": "{}_train.csv",
        }
        data_bundle = DataBundle()
        words = {}
        for lg in ["en", "es", "fr"]:
            for name, fn in fns.items():
                path = os.path.join(folder, fn.format(lg))
                ds = read_dataset(path, self.lower, 0)
                data_bundle.set_dataset(ds, name=f"{lg}_{name}")
            target_words = {}
            with open(os.path.join(folder, "{}.txt".format(lg)), encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        if self.lower:
                            line = line.lower()
                        target_words[line] = 1
            target_words = list(target_words.keys())
            words[lg] = target_words
        setattr(data_bundle, "target_words_dict", words)

        for bi in ["en_fr", "fr_en", "en_es", "es_en"]:
            path = os.path.join(folder, "{}_test.csv".format(bi))
            ds = read_dataset(path, self.lower, 1)
            data_bundle.set_dataset(ds, "{}_test".format(bi))

        return data_bundle
