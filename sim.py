from operator import itemgetter

from flask import Flask, request
from flask_cors import CORS
from flask_jsonpify import jsonify
from flask_restful import Api
from googletrans import Translator
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine

from bns import BNS

db_connect = create_engine('sqlite:///db.sqlite3')
translator = Translator()

documents = []
categories = []
docs = []


def get_data():
    del documents[:]
    del categories[:]
    del docs[:]

    conn = db_connect.connect()  # connect to database
    query = conn.execute("select id,ar,cat,en,cat_en from docs")
    result = {'data': [dict(zip(tuple(query.keys()), i)) for i in query.cursor]}

    for each in result['data']:
        if each['en'] is None:
            row_id = each['id']
            translated = translator.translate(each['ar']).text
            conn.execute("update docs set en = '" + translated + "' where id = " + str(row_id))
        else:
            translated = each['en']

        if each['cat_en'] is None:
            row_id = each['id']
            translated_cat = translator.translate(each['cat']).text
            conn.execute("update docs set cat_en = '" + translated_cat + "' where id = " + str(row_id))
        else:
            translated_cat = each['cat_en']

        documents.append(translated)
        categories.append(translated_cat)

        docs.append({
            'id': each['id'],
            'ar': each['ar'],
            'translated': translated,
            'cat': each['cat'],
            'translated_cat': translated_cat
        })

    print(documents)


app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)
api = Api(app)


@app.route('/sim', methods=['GET'])
def translate():
    if 'text' in request.args and 'cat' in request.args:
        text = request.args['text']
        cat = request.args['cat']
    else:
        return "Error: No id field provided. Please specify an text and a cat."

    get_data()
    BNS_VECTORIZER = BNS()
    BNS_VECTORIZER.fit(documents, categories)
    compared_text = [translator.translate(text).text]

    test_bns_vectors = BNS_VECTORIZER.transform(compared_text)

    print('len(test_bns_vectors) ', len(test_bns_vectors))

    # Lets find most similar sentence and category for given test document
    results = []

    print('len(test_bns_vectors.keys()) ', len(test_bns_vectors.keys()))

    for category in test_bns_vectors.keys():
        vector = test_bns_vectors[category]
        category_trained_sentence_vectors = BNS_VECTORIZER.vectors[category]
        category_trained_sentence = BNS_VECTORIZER.sentences_category_map[category]

        print('len(category_trained_sentence) ', len(category_trained_sentence))
        cosine_scores = cosine_similarity(vector, category_trained_sentence_vectors)[0]

        for score, sent in zip(cosine_scores, category_trained_sentence):

            for doc in docs:
                if doc['translated'] == sent:
                    sent = doc['ar']
                    category = doc['cat']
                    break

            results.append({'match_sentence': doc, 'score': score})

    results = sorted(results, key=itemgetter('score'), reverse=True)
    print('len(results) ', len(results))

    return jsonify({
        '_text': text,
        '_cat': cat,
        '_en': compared_text[0],
        'result': results
    })


@app.route('/add', methods=['GET'])
def add():
    if 'text' in request.args and 'cat' in request.args:
        text = request.args['text']
        cat = request.args['cat']
    else:
        return "Error: No id field provided. Please specify an text and a cat."

    nconn = db_connect.connect()  # connect to database
    nconn.execute("insert into docs (ar,cat) values ('" + text + "','" + cat + "')")

    get_data()

    return jsonify({
        'text': text,
        'result': cat
    })


@app.route('/all', methods=['GET'])
def home():
    get_data()
    return jsonify(docs)


app.run(port='5002')
