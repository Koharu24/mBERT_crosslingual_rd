import pandas as pd
import json
import os
import ipdb


def xlsx_to_json(excel_file_name, json_file_name):
    df = pd.read_excel(excel_file_name)
    problematic_columns = ["Tags", "Synonyms", "Semantic Field"]
    result = {}

    for column in df.columns:
        result[column] = []
        for index, row in df.iterrows():
            if column in problematic_columns:
                data = row[column]
                if not pd.isnull(data):
                    element = [key.strip() for key in row[column].split(",")]
                else:
                    element = []
            else:
                element = row[column]

            result[column].append(element)

    print(json.dumps(result, indent=2))
    with open(json_file_name, "w") as f:
        json.dump(result, f, indent=2)


def main():
    for file in os.listdir("."):
        if file.endswith(".xlsx"):
            xlsx_to_json(file, file.replace(".xlsx", ".json"))


if __name__ == "__main__":
    main()
