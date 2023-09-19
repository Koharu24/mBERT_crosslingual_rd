from nltk.stem import PorterStemmer
import spacy
import re
from tqdm import tqdm
import os
import ipdb

nlp = spacy.load("en_core_web_sm")
forbidden_characters = [
    ".",
    " ",
    "(",
    ")",
    ":",
    ";",
    ",",
    ".",
    "'",
    "&",
    "/",
    "’",
    "–",
    "—",
    "!",
    "?",
    "“",
    "”",
    "\\",
] + list("1234567890")


def main():
    pos_categories = set(["VERB", "NOUN", "ADJ", "ADV", "INTJ", "PRON"])

    dest_words = "./data/en_filtered.txt"
    with open("./data/en_words.txt", "r") as f:
        words = [line.strip() for line in f.readlines()]

    words = [
        el
        for el in tqdm(words)
        if not re.search(r"\d", el)
        and not re.search(r"(.)\1\1", el)
        and not any(char in el for char in forbidden_characters)
        and len(el) > 1
        and el[0] != el[1]
    ]
    if os.path.exists(dest_words):
        with open(dest_words) as f:
            already_cleaned_words = f.readlines()
    else:
        already_cleaned_words = []

    words = list(set(already_cleaned_words).union(set(words)))

    nlps = [nlp(word) for word in tqdm(words) if len(word) > 1]
    nlps_with_valid_pos = [nlp for nlp in tqdm(nlps) if nlp[0].pos_ in pos_categories]
    lemmas = list(set([nlp[0].lemma_ for nlp in tqdm(nlps_with_valid_pos)]))

    lemmas = list(set(lemmas).union(set(already_cleaned_words)))
    # unique_words = remove_same_stem(words)
    print(f"Number of unique lemmas: {len(lemmas)}, out of {len(words)}")

    ipdb.set_trace()

    with open("./data/en_filtered.txt", "w") as f:
        f.writelines(lemmas)


# def remove_same_stem(words: list[str]):
#     stemmer = PorterStemmer()
#     unique_stems = {}
#     unique_words = []
#     for word in words:
#         stem = stemmer.stem(word)
#         if stem not in unique_stems:
#             unique_stems[stem] = word
#             unique_words.append(word)
#
#     return unique_words


def filter_words_by_pos_spacy(word_list, pos_categories):
    filtered_words_with_pos = {}

    for word in word_list:
        doc = nlp(word)
        pos = doc[0].pos_
        if pos in pos_categories:
            filtered_words_with_pos[word] = pos

    return list(filtered_words_with_pos.keys())


# # Write unique words to file
# with open("./en_words_no_same_stem.txt", "w") as f:
#     f.writelines(unique_words)
#
#
# with open("./en_words_no_same_stem.txt", "w") as f:
#     f.writelines(unique_words)

if __name__ == "__main__":
    main()
