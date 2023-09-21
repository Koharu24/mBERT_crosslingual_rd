import json
import openai
import translators as ts
from tqdm import tqdm
import os


prompts = {
    "en": dict(
        system="You are an expert assistant in English, Italian, German and Japanese.",
        user="Please find the word in any language you know that more closely matches the given definition. The word I'm looking for is either EN, IT, DE or JP. Give your result as input to the 'parse_result' function.",
    ),
    "ita": dict(
        system="Sei un assistente esperto in inglese, italiano, tedesco e giapponese.",
        user="Trova la parola in qualsiasi lingua conosci che corrisponde più da vicino alla definizione data. La parola che sto cercando è EN, IT, DE o JP. Fornisci il tuo risultato in input alla funzione 'parse_result'.",
    ),
    "de": dict(
        system="Du bist ein Expert Assistent in Englisch, Italienisch, Deutsch und Japanisch.",
        user="Bitte finden Sie das Wort in jeder Sprache, die Sie kennen, die der Definition am nächsten kommt. Das Wort, das ich suche, ist EN, IT, DE oder JP. Geben Sie Ihr Ergebnis als Eingabe für die Funktion 'parse_result' an.",
    ),
    "ja": dict(
        system="あなたは英語、イタリア語、ドイツ語、日本語のエキスパートアシスタントです。",
        user="与えられた定義に最も近い言葉を知っている言語で見つけてください。私が探している言葉はEN、IT、DE、またはJPです。あなたの結果を 'parse_result'関数に入力してください。",
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
for lang in langs[2:]:
    with open(f"./{lang}.json") as f:
        current_lang = json.load(f)

    dest_file_name = f"./{lang}_predictions.json"

    start_from = 0
    if os.path.exists(dest_file_name):
        with open(dest_file_name) as f:
            start_from = len([l for l in f.readlines() if l.strip()])

    if start_from > 0:
        print(f"Skipping {lang} from {start_from}")

    definitions = current_lang["Definition ENG"]

    ts_lang = {
        "ita": "it",
        "de": "de",
        "ja": "ja",
    }[lang]

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
            print(f"Running in {lang} original: {i%2==1}")
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
                except:
                    print("Error, retrying...")
            try:
                result = json.loads(output.choices[0].message.function_call.arguments)
            except:
                print(output.choices[0].message)
            predictions.append(result)

        with open(dest_file_name, "a") as f:
            f.write(f"{json.dumps(predictions)}\n")
