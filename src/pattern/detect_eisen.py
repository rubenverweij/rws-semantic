"""Train simple model to detect eisen"""
import os
import re
import datetime
import pandas as pd

def read_file(filename):
    with open(filename, 'r') as file:
        text = file.read()
    text = text.replace('\r\n', '')
    text = text.replace('\n', '')
    text = re.sub(r"- ", '-', text)
    text = re.sub(r" -", '-', text)
    text = re.sub(r" +", '', text)
    return text

def get_document_text(folder: str):
    document_dict = {}
    for _, _, filenames in os.walk(folder):

        for filename in filenames:
            document_name = filename.split("_")[0]
            page = {
                "filename": filename,
                "documentname": document_name,
                "page": filename.split("_")[1],
                "text": read_file(os.path.join(folder, filename))
            }
            if document_name in document_dict.keys():
                document_dict.get(document_name).append(page)
            else:
                document_dict[document_name] = [page]
    return document_dict

def use_regex(input_text):
    pattern = re.compile(r"[A-z]{3}-[0-9]{5}", re.IGNORECASE)
    pattern2 = re.compile(r"[A-z]{3}-[0-9]{6}", re.IGNORECASE)
    pattern3 = re.compile(r"[A-z]{3}-[0-9]{6}", re.IGNORECASE)
    return pattern.findall(input_text) + pattern2.findall(input_text) + pattern3.findall(input_text)

if __name__ == "__main__":

    # first run src/convert_to_pdf.sh to get text data
    # than retrieve text data and search for eisen
    files = get_document_text(folder="data/text/")
    eisen = pd.read_excel("data/eisen/SSS eisen.xlsx")
    eisen_dict = {k: [] for k in eisen["ID"].to_list()}

    count = 0
    for file, pages in files.items():
        for page in pages:
            detected = use_regex(page['text'])
            if detected:
                for eis in detected:
                    count += 1
                    if eis in eisen_dict.keys():
                        eisen_dict.update({eis: [page['page']] + eisen_dict[eis]})
                    else:
                        eisen_dict[eis] = [page['page']]
    
    pages = files["SSDD-PrinsesMarijkesluis"]
    file = [page['text'] for page in pages if page["page"] == "27"]

    print(f"Found {count} eis references")

    date_stamp = datetime.datetime.now().strftime("%Y_%m_%d")
    result_dir = f"results/{date_stamp}"
    if not os.path.exists(result_dir):
      os.mkdir(result_dir)

    pd.DataFrame(eisen_dict.items(), columns=['eis', 'gevonden_op_pagina']).to_csv(f"{result_dir}/eis_detectie.csv")
                    

    








    