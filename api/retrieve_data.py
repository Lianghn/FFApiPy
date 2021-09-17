from ExperimentApiPy import app
from api.elastic_connection import connect_elasticsearch
from flask import jsonify, request
from datetime import datetime
import numpy as np
import scipy as sp
from scipy import stats
import collections

es = connect_elasticsearch()

@app.route('/', methods=['GET'])
def home():
    message = 'Flask is UP and RUNNING'
    return jsonify(message)


# GetData From Index + Id
@app.route('/GetData', methods=['POST'])
def get_data():
    #json format:
    #             {"index":"experiments", "id":"d_pNsHsBFqb7-mBbFsuM"}
    data = request.get_json()
    results = es.get(index=data['index'], id=data['id'])
    return jsonify(results['_source'])

# Get Data From Ony Index & Index + Type
@app.route('/SearchDataByIndexAndKey', methods=['POST'])
def search_data():
    #json format:
    #             {"index":"experiments", "key":"Type", "value":"pageview"}

    data = request.get_json()
    if data['value'] :
        query_body = {
            "query": {
                "match": {
                    data['key']: data['value'] 
                }
            }
        }
    else :
        query_body = {
            "query": {
                "match_all": {
                }
            }
        }
    res = es.search(index=data['index'], body=query_body)
    print(res)
    return jsonify(res['hits']['hits'])


# Get Exp Results
@app.route('/api/ExperimentResults', methods=['POST'])
def expt_data():
    #########################################################
    #inputdata json format:
    #  {'Flag' : 
    #        {'Id' : FlagId,
    #         'BaselineVariation': 'var2', 
    #          'Variations: [value1, value2, value3]
    #          }, 
    #    'ExperimentId': Id,
    #    'ExperimentStartTime': Timestamp1, 
    #    'ExperimentEndTime': Timestamp2
    #   }
    ##########################################################
    # output format : 
    #      {'var1' : 
    #            { 'TargetEventNumber' : Number1, 
    #              'UnqueVisitorsNumber' : Number2,  
    #              'ConversionRate': Number3, 
    #              'ChangesToBaseline': Number4, 
    #              'ConfidentInterval': (value_min, value_max), 
    #              'p_value': Number5 
    #             }, 
    #         'var2' :
    #                ......
    #       } 
    ############################################################
    # Get data from frontend
    startime = datetime.now()
    data = request.get_json()
    # Query Flag data
    query_body_A = {
        "query": {
            "match": {
                'FeatureFlagId': data['Flag']['Id'] 
            }
        }
    }

    res_A = es.search(index="ffvariationrequestindex", body=query_body_A)

 # Query Expt data   
    query_body_B = {
    "query": {
        "bool": {
            "must": {
                "match": {
                            'Type' : 'pageview'
                }
            },
            "filter": {
                "range": {
                    "TimeStamp": {
                        "gte": data['StartExptTime'],
                        "lte": data['EndExptTime']
                    }
                }
            }
        }
    }
    }
    res_B = es.search(index="experiments", body=query_body_B)

# Stat of Flag
    dict_var_user = {}
    dict_var_occurence = {}
    for item in res_A['hits']['hits']:
        if item['_source']['VariationValue'] not in list(dict_var_occurence.keys()) :
            dict_var_occurence[ item['_source']['VariationValue'] ]  = 1
            dict_var_user[ item['_source']['VariationValue'] ]  = [item['_source']['FFUserName']]
        else :
            dict_var_occurence[ item['_source']['VariationValue'] ] = dict_var_occurence[ item['_source']['VariationValue'] ] + 1
            dict_var_user[ item['_source']['VariationValue'] ]  =  dict_var_user[ item['_source']['VariationValue'] ] + [item['_source']['FFUserName']]

    print('dictionary of flag var:occurence')
    print(dict_var_occurence)

    for item in dict_var_user.keys():
        dict_var_user[item] = list(set(dict_var_user[item]))
    print('dictionary of flag var:usr')
    print(dict_var_user)

    # To delete when real data comes   
    dict_var_user['Green'] = ['user1630749856']
    dict_var_user['A'] = ['user1630750520','user1630749287']

    # Stat of Expt.
    dict_expt_occurence = {}
    for item in res_B['hits']['hits']:
        for it in dict_var_user.keys():
            if item['_source']['User']['FFUserName'] in dict_var_user[it] :
                if it not in list(dict_expt_occurence.keys()):
                    dict_expt_occurence[it] = 1
                else:
                    dict_expt_occurence[it] = 1 + dict_expt_occurence[it]
    print('dictionary of expt var:occurence')
    print(dict_expt_occurence)

    # Get Confidence interval
    def mean_confidence_interval(data, confidence=0.95):
        a = 1.0 * np.array(data)
        n = len(a)
        m, se = np.mean(a), sp.stats.sem(a)
        h = se * sp.stats.t.ppf((1 + confidence) / 2., n-1)
        return m, m-h, m+h

    output = []
    var_baseline = data['Flag']['BaselineVariation']
    BaselineRate = dict_expt_occurence[var_baseline]/dict_var_occurence[var_baseline]
    # Preprare Baseline data sample distribution for Pvalue Calculation 
    dist_baseline = [1 for i in range(dict_expt_occurence[var_baseline])] + [0 for i in range(dict_var_occurence[var_baseline]-dict_expt_occurence[var_baseline])] 
    for item in dict_var_occurence.keys(): 
        if item in  dict_expt_occurence.keys():
            dist_item = [1 for i in range(dict_expt_occurence[item])] + [0 for i in range(dict_var_occurence[item]-dict_expt_occurence[item])]
            rate, min, max = mean_confidence_interval(dist_item)
            confidenceInterval = [ 0 if round(min,2)<0 else round(min,2), 1 if round(max,2)>1 else round(max,2)]
            pValue = round(1-stats.ttest_ind(dist_baseline, dist_item).pvalue,2)
            output.append({ 'variation': item,
                            'conversion' : dict_expt_occurence[item],  
                            'uniqueUsers' : dict_var_occurence[item], 
                            'conversionRate':   round(rate,2),
                            'changeToBaseline' : round(rate-BaselineRate,2),
                            'confidenceInterval': confidenceInterval, 
                            'pValue': pValue,
                            'isBaseline': True if data['Flag']['BaselineVariation'] == item else False, 
                            'isWinner': False,
                            'isInvalid': True if pValue < 0.95 else False
                            } 
                        )
    # Get winner variation
    listValid = [output.index(item) for item in output if item['isInvalid'] == False]
    #    listValid = [0,1]
    # If at least one variation is valid:
    if len(listValid) != 0: 
        dictValid = {}
        for index in listValid:
            dictValid[index] = output[index]['conversionRate']
        maxRateIndex = [k for k, v in sorted(dictValid.items(), key=lambda item: item[1])][-1]        
        output[maxRateIndex]['isWinner'] = True

    #   print(output)
    endtime = datetime.now()
    print('processing time:') 
    print((endtime-startime))
    return jsonify(output)