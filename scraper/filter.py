import ipdb

with open("./data/it_filtered.txt", "r") as f:
    it_words = f.readlines()

with open("./data/en_filtered.txt", "r") as f:
    en_words = f.readlines()

assert len(it_words) == len(en_words)

is_nasty = [len(w.split()) > 2 for w in it_words]
it_words = [w for w, n in zip(it_words, is_nasty) if not n]
en_words = [w for w, n in zip(en_words, is_nasty) if not n]

with open("./data/it_filtered_nice.txt", "w") as f:
    f.writelines(it_words)

with open("./data/en_filtered_nice.txt", "w") as f:
    f.writelines(en_words)
