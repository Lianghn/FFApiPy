from flask_app import app
from api.elastic_connection import connect_elasticsearch
from flask import jsonify, request

es = connect_elasticsearch()

@app.route('/', methods=['GET'])
def home():
    message = 'Flask is UP and RUNNING'
    return jsonify(message)



@app.route('/GetData', methods=['POST'])
def get_data():
    #json format:
    #             {"index":"experiments", "id":"d_pNsHsBFqb7-mBbFsuM"}
    data = request.get_json()
    results = es.get(index=data['index'], id=data['id'])
    return jsonify(results['_source'])


@app.route('/SearchDataByIndexAndKey', methods=['POST'])
def search_data():
    #json format:
    #             {"index":"experiments", "key":"Type", "value":"pageview"}

    data = request.get_json()
    query_body = {
        "query": {
            "match": {
                data['key']: data['value'] 
            }
        }
    }

    res = es.search(index=data['index'], body=query_body)
    print(res)
    return jsonify(res['hits']['hits'])
