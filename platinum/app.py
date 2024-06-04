import re
import pandas as pd
import pickle
import numpy as np

from flask import Flask, jsonify, request
from keras.models import load_model, Sequential
from keras.layers import Embedding, LSTM, Dense, SpatialDropout1D
from tensorflow.keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from

#### Flask App
app = Flask(__name__)

######## Swagger Configuration
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info={
        'title': LazyString(lambda: 'API Documentation for Data Processing and Modeling'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling'),
    },
    host=LazyString(lambda: request.host)
)
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
swagger = Swagger(app, template=swagger_template, config=swagger_config)

# Text Cleaning Function
def cleansing(sent):
    string = sent.lower() # mengkonversi ke huruf non kapital
    string = re.sub(r'<.*?>','', string)  #format html
    string = re.sub(r'&\S+','', string)  #format html
    string = re.sub(r'http\S+', '', string)  #Menghapus URL yang dimulai dengan "http".
    string = re.sub(r'www\.\S+','', string)  #format URL
    string = re.sub(r"\\x[a-fA-F0-9]{2}",'', string)  #format \xf0\x9f\x98\x82\xf0\x9f\x98\x82\xf0\x9f\x98\x82...
    string = string.replace('\\n', '')#enghapus string '/n'
    string = re.sub(r'\b(\w+)\b\s+\b\1\b', r'\1', string) #Menghapus kata-kata yang duplikat.
    string = re.sub(r'(\w)(\1{2,})', r"\1", string) #Menghapus karakter berulang lebih dari 2 kali.
    string = re.sub("(username|user|url|rt|xd)\s|\s(user|url|rt|xd)","",string)
    string = re.sub(r'[^a-zA-Z0-9]',' ', string) #Mengganti karakter non-alphanumeric dengan spasi.
    string = re.sub(r"\b[a-zA-Z]\b","",string) #menghapus kata-kata yang hanya terdiri dari satu huruf.
    string = string.strip() #Menghapus spasi di awal dan akhir string.
    string = re.sub('(s{2,})',' ',string) #Mengganti dua atau lebih spasi berturut-turut dengan satu spasi.
    return string

# Sentiment Labels
sentiment = ['negative', 'neutral', 'positive']

# Create and save Tokenizer and Model
def create_and_save_model():
    # Sample data

    data = pd.read_csv("/Users/irtea/bootcamp DSC/binar-data-science/platinum/binardsc-master/train_preprocess.tsv.txt", sep="\t")
    data.columns = ['text','label']

    # Clean text
    data['text'] = data['text'].apply(cleansing)

    # Tokenizer
    tokenizer = Tokenizer(num_words=5000, lower=True, split=' ')
    tokenizer.fit_on_texts(data['text'].values)
    with open('tokenizer_lstm.pickle', 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Convert text to sequences
    X = tokenizer.texts_to_sequences(data['text'].values)
    X = pad_sequences(X, maxlen=77)

    # Labels
    Y = pd.get_dummies(data['label']).values

    # Create LSTM model
    model = Sequential()
    model.add(Embedding(input_dim=5000, output_dim=100, input_length=77))
    model.add(SpatialDropout1D(0.2))
    model.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
    model.add(Dense(3, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    # Train the model
    model.fit(X, Y, epochs=5, batch_size=64, verbose=2)

    # Save the model
    model.save('model_lstm.h5')

create_and_save_model()

# Load Tokenizer and Model
def load_tokenizer_and_model():
    with open("tokenizer_lstm.pickle", 'rb') as file:
        tokenizer_lstm = pickle.load(file)
    model_lstm = load_model('model_lstm.h5')
    return tokenizer_lstm, model_lstm

tokenizer_lstm, model_lstm = load_tokenizer_and_model()

## API Endpoints

@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():
    input_text = request.form.get('text')
    model = request.form.get('model')

    if model not in ['lstm', 'neural-network']:
        return jsonify({'status_code': 400, 'description': 'Invalid model selection'}), 400

    text = [cleansing(input_text)]

    if model == 'lstm':
        predicted = tokenizer_lstm.texts_to_sequences(text)
        guess = pad_sequences(predicted, maxlen=77)

        prediction = model_lstm.predict(guess)
        polarity = np.argmax(prediction[0])

        return jsonify({'input': input_text, 'prediction': sentiment[polarity]})

    elif model == 'neural-network':
        # Placeholder for neural network model implementation
        # Assuming the neural network model is similar to the LSTM model for demonstration purposes
        predicted = tokenizer_lstm.texts_to_sequences(text)
        guess = pad_sequences(predicted, maxlen=77)

        prediction = model_lstm.predict(guess)
        polarity = np.argmax(prediction[0])

        return jsonify({'input': input_text, 'prediction': sentiment[polarity]})

if __name__ == '__main__':
   app.run()
