import json
import openai
import translators as ts
from tqdm import tqdm
import os

# TODO: non dirgli la lingua target (con prompt in inglese)

prompts = {
    "en": dict(
        system="You are an expert assistant and polyglot.",
        user="Please find the word in any language you know that more closely matches the given definition. The word I'm looking for might not be in the same language as the definition. Give your result as input to the 'parse_result' function.",
    ),
    "ita": dict(
        system="Sei un assistente esperto in inglese, italiano, tedesco e giapponese.",
        user="Trova la parola in qualsiasi lingua conosci che corrisponde più da vicino alla definizione data. La parola che sto cercando potrebbe non essere nella stessa lingua della definizione. Fornisci il tuo risultato in input alla funzione 'parse_result'.",
    ),
    "de": dict(
        system="Du bist ein Expert Assistent in Englisch, Italienisch, Deutsch und Japanisch.",
        user="Bitte finden Sie das Wort in jeder Sprache, die Sie kennen, die der Definition am nächsten kommt. Das Wort nach dem ich suche ist möglicherweise nicht in der gleichen Sprache wie die Definition. Geben Sie Ihr Ergebnis als Eingabe für die Funktion 'parse_result' an.",
    ),
    "ja": dict(
        system="あなたは英語、イタリア語、ドイツ語、日本語のエキスパートアシスタントです。",
        user="与えられた定義に最も近い言語で単語を見つけてください。私が探している単語は、定義と同じ言語になっているとは限りません。あなたの結果を 'parse_result' 関数の入力として与えます。",
    ),
}
langs = ["ita", "de", "ja"]
function_schema = {
    "name": "parse_result",
    "description": "Parses the result word.",
    "parameters": {
        "type": "object",
        "properties": {
            "language": {
                "type": "string",
                "description": "The language of the word that more closely matches the definition given by the user.",
            },
            "word": {
                "type": "string",
                "description": "The word that more closely matches the definition given by the user.",
            },
        },
        "required": ["word"],
    },
}
for lang in ["ja"]:
    print(f"Checking {lang}")
    with open(f"./{lang}.json") as f:
        current_lang = json.load(f)

    dest_file_name = f"./no_clue_{lang}_predictions.json"

    start_from = 0
    # if os.path.exists(dest_file_name):
    #     # with open(dest_file_name) as f:
    #     #     start_from = len([l for l in f.readlines() if l.strip()])
    #     os.remove(dest_file_name)

    if start_from > 0:
        print(f"Skipping {lang} from {start_from}")

    definitions = current_lang["Definition ENG"]

    # ts_lang = {
    #     "ita": "it",
    #     "de": "de",
    #     "ja": "ja",
    # }[lang]

    en_system_prompt = prompts["en"]["system"]
    en_user_prompt = prompts["en"]["user"]
    dest_system_prompt = prompts[lang]["system"]
    dest_user_prompt = prompts[lang]["user"]
    for definition in tqdm(definitions):
        prompts = [
            (en_system_prompt, en_user_prompt),
            (dest_system_prompt, dest_user_prompt),
        ]
        predictions = []
        for i, (system_prompt, user_prompt) in enumerate(prompts):
            # print(f"Running in {lang} original: {i%2==1}")
            user_prompt = f"""
            {user_prompt}
            Definition:
            ---
            {definition}
            ---
            """
            print(user_prompt)
            output = None
            while output is None:
                try:
                    output = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.0,
                        max_tokens=100,
                        functions=[function_schema],
                    )
                except Exception as e:
                    print("Error, retrying...")
            try:
                result = json.loads(output.choices[0].message.function_call.arguments)
            except:
                print(output.choices[0].message)
            print(result)
            predictions.append(result)

        with open(dest_file_name, "a") as f:
            f.write(f"{json.dumps(predictions)}\n")
