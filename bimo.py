import re
import pandas as pd
import json
# import Sastrawi 
import sqlite3 

# from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

from flask import Flask, jsonify

#### flask
app = Flask(__name__)

from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

df_kamus_kata = pd.read_csv("new_kamusalay.csv", encoding='iso-8859-1', header = None)
df_kamus_kata = dict(zip(df_kamus_kata[0], df_kamus_kata[1]))
def normalize_alay(text):
    return ' '.join([df_kamus_kata[word] if word in df_kamus_kata else word for word in text.split(' ')])
    

html_tag = re.compile(r'<.*?>')
http_link = re.compile(r'https://\s+')
www_link = re.compile(r'www\.\s+')
puncuation = re.compile(r'[^\w\s]')
def data_cleaning(text) :
    text = text.lower() 
    text = re.sub(r'\bx([a-fA-F0-9]{2})',r'',text)
    text = re.sub(html_tag, r'', text)
    text = re.sub(www_link, r'', text)
    text = re.sub(http_link, r'', text)
    text = re.sub(puncuation, r'', text)
    text = normalize_alay(text)
    text = text.strip()
    return text
def file_bimo(data):
    conn = sqlite3.connect('file_bimo.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Tweet_finish (
        after_clean TEXT
    )
    ''')
    for item in data:
        

            
        cursor.execute('''
            INSERT INTO Tweet_finish (after_clean) VALUES (?)
        ''', (item,))

    conn.commit()
    conn.close()


########swagerr
app.json_encoder = LazyJSONEncoder
swagger_template = {
    "info": {
        "title":  "API Documentation for Data Processing and Modeling",
        "version": "1.0.0",
        "description": "Dokumentasi API"
    },
    "host": "127.0.0.1:5000"
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)


@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():

    text = request.form.get('text')

    text_sinonim = normalize_alay(text)
    text_cleaning = data_cleaning(text_sinonim)
    # text_stop = " ".join(stopword.remove(text_cleaning) for text_cleaning in text_cleaning.split() )

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': text_cleaning
    }        

    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/text_processing_file.yml", methods=['POST'])
@app.route('/text-processing-file', methods=['POST'])
def text_processing_file():

    # Upladed file
    file = request.files.getlist('file')[0]

    # Import file csv ke Pandas
    temp_df = pd.read_csv(file,encoding='latin-1')
    temp_df['after_normalize'] = temp_df['Tweet'].apply(normalize_alay)
    temp_df['after_clean'] = temp_df['after_normalize'].apply(lambda x: data_cleaning(x))
    # temp_df['after_clean'] = temp_df['after_clean'].apply(lambda x: " ".join(stopword.remove(x) for x in x.split() ))
    
    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': temp_df['after_clean'].values.tolist()
    }
    file_bimo(temp_df['after_clean'].values.tolist())
    response_data = jsonify(json_response)
    return response_data

##running api
if __name__ == '__main__':
   app.run()
   

