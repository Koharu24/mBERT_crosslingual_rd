import translators as ts
import re
from tqdm import tqdm

dest_langs = [
    "it",
    "de",
    "ja",
]

with open("./en_filtered.txt", "r") as f:
    en_words = f.readlines()
forbidden_characters = [
    "-",
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
]

en_words = [
    el
    for el in en_words
    if not re.search(r"\d", el)
    and not re.search(r"(.)\1\1", el)
    and not any(char in el for char in forbidden_characters)
    and len(el) > 1
]
with open("./en_filtered_clean.txt", "w") as f:
    f.writelines(en_words)
translators = [
    "google",
    "bing",
    "deepl",
]
current_translator = translators[0]
for dest_lang in dest_langs:
    print(f"Translating to {dest_lang}")
    with open(f"./{dest_lang}_filtered.txt", "a") as f:
        for en_word in tqdm(en_words):
            success = False
            while not success:
                try:
                    translated_word = str(
                        ts.translate_text(
                            en_word,
                            to_language=dest_lang,
                            translator=current_translator,
                        )
                    )
                    success = True
                except Exception as e:
                    # switch translator
                    print(
                        f"Switching translator from {current_translator} to {translators[(translators.index(current_translator) + 1) % len(translators)]}"
                    )
                    current_translator = translators[
                        (translators.index(current_translator) + 1) % len(translators)
                    ]

            f.write(translated_word + "\n")
