from spacy.util import filter_spans
from transformers import MarianMTModel, MarianTokenizer
from tqdm import tqdm
import ipdb
import torch as t
import os


# def translate(text: list[str], model_name: str):
#     tokenizer = MarianTokenizer.from_pretrained(model_name)
#     model = MarianMTModel.from_pretrained(model_name)
#     batch = tokenizer(text, padding=True, return_tensors="pt", truncation=True)
#     translated = model.generate(**batch)
#     tgt_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
#     return tgt_text
#


def translate(text: list[str], model_name: str, batch_size: int, dest_file: str):
    if os.path.exists(dest_file):
        print(f"Removing {dest_file}")
        os.remove(dest_file)

    device = t.device("cuda" if t.cuda.is_available() else "cpu")
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name).to(device)
    tgt_text = []

    for i in tqdm(range(0, len(text), batch_size)):
        batch_texts = text[i : i + batch_size]
        batch = tokenizer(
            batch_texts, padding=True, return_tensors="pt", truncation=True
        )
        batch = {k: v.to(device) for k, v in batch.items()}

        batch = batch | {"max_length": 5}

        # Use torch.no_grad to prevent tracking of gradients
        with t.no_grad():
            translated = model.generate(**batch)

        batch_tgt_text = [
            tokenizer.decode(t, skip_special_tokens=True) for t in translated
        ]
        tgt_text.extend(batch_tgt_text)

        # Append translated words to the destination file
        with open(dest_file, "a") as f:
            for word in batch_tgt_text:
                f.write(f"{word}\n")

        # Delete tensors to free up GPU memory
        del batch
        del translated
        t.cuda.empty_cache()

    return tgt_text


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


def filter_words(input_list: list[str]):
    return [
        word.strip()
        for word in input_list
        if word[0] != word[1]
        and len(word.strip()) > 1
        and not any(char in word for char in forbidden_characters)
    ]


with open("./data/en_filtered.txt", "r") as f:
    en_words = [w.strip() for w in f.readlines()]

print(len(en_words))

# with open("./data/en_filtered.txt", "w") as f:
#     f.write("\n".join(en_words))
#
print(len(en_words))
print(en_words[:10])
# it_words = translate(en_words, "Helsinki-NLP/opus-mt-en-it", batch_size=15)
# with open("./data/it_filtered.txt", "w") as f:
#     f.write("\n".join(it_words))
de_words = translate(
    en_words,
    "Helsinki-NLP/opus-mt-en-de",
    batch_size=500,
    dest_file="./data/de_filtered.txt",
)

ja_words = translate(
    en_words,
    "Helsinki-NLP/opus-mt-en-jap",
    batch_size=500,
    dest_file="./data/ja_filtered.txt",
)
