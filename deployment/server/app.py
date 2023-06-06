import pickle

from random import randrange

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from string import punctuation
import pandas
import requests
import json
from flask import Flask, render_template, abort, jsonify, request, redirect, url_for
from flask_cors import CORS, cross_origin

import warnings

import numpy as np

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/api/predict', methods=['POST'])
@cross_origin( supports_credentials = True )
def predictAPI():
    if request.method == 'POST':
        try:
            data_json =json.loads(request.data)
            if "subject" in data_json:
                subject = data_json['subject']
            else:
                subject = ""
            if "body" in data_json:
                body = data_json['body']
            else:
                body = ""
            if "link_attachement" in data_json:
                urls = data_json['link_attachement']
                urls = urls.split("<>")
            else:
                urls = []
            subject_data = [subject]
            body_data = [body]
            result=0
            if body or subject or urls:
                if subject:
                    subject_prediction = subject_pipeline.predict(subject_data)
                    result += subject_prediction[0] * 0.3
                if body:
                    processed_email = preprocess_text(body)
                    body_prediction = body_pipeline.predict(body_data)
                    result += body_prediction[0] * 0.4
                if urls:
                    url_predection = 0
                    for url in urls:
                        url_predection += subject_pipeline.predict([url])
                    if len(urls)>0:
                        url_predection = url_predection/len(urls)
                    else:
                        url_predection =0
                    result += url_predection*0.3
            else:
                return 0

            final_result = (result) * 100

            return jsonify(str(int(final_result)))
        except Exception as e:
            return jsonify(e)


@app.route('/')
def welcome():  # put application's code here
    return render_template('home/index.html')


"""
News interface :
    *show breaking news about phishing

"""


@app.route('/news')
def news():
    positive = 0
    negative = 0
    neutral = 0

    api_key = '941862de328441b28b8d2498f7736395'
    url = f'https://newsapi.org/v2/everything?pageSize=15&q=phishing&sortBy=relevancy&language=en&apiKey={api_key}'
    response = requests.get(url).json()
    articles = response['articles']


    return render_template('home/index.html', prediction= articles)


"""

@app.route('/api/news')
def newsAPI():
    positive = 0
    negative = 0
    neutral = 0

    api_key = '941862de328441b28b8d2498f7736395'
    url = f'https://newsapi.org/v2/everything?pageSize=15&q=phishing&sortBy=relevancy&language=en&apiKey={api_key}'
    response = requests.get(url).json()
    articles = response['articles']

    json_data = json.dumps(articles)


    return json_data
"""

"""
Email interface :
    *detection of spam email 

"""


@app.route('/EmailSubjectDetection')
def EmailSubjectDetection():
    return render_template('email/EmailSubjectDetection.html')


@app.route('/EmailBodyDetection')
def EmailBodyDetection():
    return render_template('email/EmailBodyDetection.html')


""""
Deployment for fake news detection
"""


@app.route("/newsprediction")
def newsdetection():
    return render_template('fakeNews/NewsDetection.html')


@app.route('/predict', methods=['POST'])
def predict():
    from PredictionModel import PredictionModel
    model = PredictionModel(request.json)
    return jsonify(model.predict())


@app.route('/random', methods=['GET'])
def random():
    data = pandas.read_csv("data/fake_or_real_news_test.csv")
    index = randrange(0, len(data) - 1, 1)
    return jsonify({'title': data.loc[index].title, 'text': data.loc[index].text})


""""
Deployment for subject email detection
"""

import os
import pickle

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Specify the relative paths to the pickle files
subject_pickle_path = os.path.join(current_dir, "model", "subjectcf3.pkl")
body_pickle_path = os.path.join(current_dir, "model", "body99.pkl")
url_pickle_path = os.path.join(current_dir, "model", "subjectcf3.pkl")


# Load the pickle model for subject detection
with open(subject_pickle_path, 'rb') as f:
    subject_pipeline = pickle.load(f)

# Load the pickle model for body detection
with open(body_pickle_path, 'rb') as f:
    body_pipeline = pickle.load(f)

with open(url_pickle_path, 'rb') as f:
    url_pipeline = pickle.load(f)

# load the pickle model for subject detection
# with open("/server/model/Subjectrf3.pkl", 'rb') as f:
#    pipeline = pickle.load(f)
#
# # load the pickle model for body detection
# with open("/server/model/bodyrfc5.pkl", 'rb') as f:
#     pipeline = pickle.load(f)


@app.route("/subjectdetection")
def subjectdetection():
    return render_template('email/EmailSubjectDetection.html')


@app.route('/subjectpredict', methods=['POST'])
def subjectpredict():
    if request.method == 'POST':
        message = request.form['message']
        data = [message]

        prediction = subject_pipeline.predict(data)
    
    return render_template('email/EmailSubjectDetection.html', prediction=prediction)


@app.route('/api/subjectpredict', methods=['POST'])
def subjectpredictAPI():
    if request.method == 'POST':
        message = request.form['message']
        data = [message]

        prediction = subject_pipeline.predict(data)
    my_list = prediction.tolist()
    json_data = json.dumps(my_list)
    return json_data
    


""""
Deployment for body email detection
"""


def preprocess_text(text):
    # Apply any preprocessing steps to the text
    # For example, you can remove stopwords, perform stemming, etc.
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)

    # Remove stop words and punctuations and perform stemming on each word
    stop_words = set(stopwords.words('english') + list(punctuation))
    stemmer = PorterStemmer()
    words = [word_tokenize(sentence.lower()) for sentence in sentences]
    filtered_words = [[stemmer.stem(word) for word in words_list if word not in stop_words] for words_list in words]

    # Calculate the frequency of each word in the text
    word_frequency = {}
    for words_list in filtered_words:
        for word in words_list:
            if word not in word_frequency:
                word_frequency[word] = 1
            else:
                word_frequency[word] += 1

    # Calculate the weighted frequency of each sentence
    sentence_scores = {}
    for i, words_list in enumerate(filtered_words):
        for word in words_list:
            if word in word_frequency:
                if i not in sentence_scores:
                    sentence_scores[i] = word_frequency[word]
                else:
                    sentence_scores[i] += word_frequency[word]

    # Get the top N sentences with the highest scores
    summary_sentences = []
    top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    for index, score in top_sentences:
        summary_sentences.append(sentences[index])

    # Combine the top sentences into a summary
    text = ' '.join(summary_sentences)
    processed_text = text  # Placeholder, replace with your preprocessing steps
    return processed_text


@app.route("/bodydetection ")
def bodydetection():
    return render_template('email/EmailSubjectDetection.html')


@app.route('/bodypredict', methods=['POST'])
def bodypredict():

    if request.method == 'POST':
        message = request.form['message']
        data = [message]
        processed_email = preprocess_text(message)
        prediction = body_pipeline.predict(data)

    return render_template('email/EmailSubjectDetection.html', prediction=prediction)

@app.route('/api/bodypredict', methods=['POST'])
def bodypredictAPI():

    if request.method == 'POST':
        message = request.form['message']
        data = [message]
        processed_email = preprocess_text(message)
        prediction = body_pipeline.predict(data)
    my_list = prediction.tolist()
    json_data = json.dumps(my_list)
        
    return json_data


""""
Deployment for URL email detection
"""
# load the pickle model for url detection
#with open("/server/model/url_xgb9.pkl", 'rb') as f:
#    model = pickle.load(f)


@app.route("/urldetection")
def urldetection():
    return render_template('url/UrlDetection.html')


@app.route('/urlpredict', methods=['POST'])
def urlpredict():
    if request.method == 'POST':
        message = request.form['message']
        data = [message]

        prediction = subject_pipeline.predict(data)

    return render_template('url/UrlDetection.html', prediction=prediction)



@app.route('/api/urlpredict', methods=['POST'])
def urlpredictAPI():
    if request.method == 'POST':
        message = request.form['message']
        data = [message]

        prediction = subject_pipeline.predict(data)
    my_list = prediction.tolist()
    json_data = json.dumps(my_list)

    return json_data






if __name__ == '__main__':
    app.run(debug=True)