# ExperimentApiPy

Under "ExperimentApiPy/config", create file "config.ini".
In this file, put lines:

    [elastic]
    es_host =  http://localhost:9200

    [elasticpasswd]
    es_passwd =  elastic_password
    
Then repalce localhost by your elasticsearch url  & replace elastic_password by password for user 'elastic'.


Run:
    $>pip install -r requirements.txt
    $>python ExperimentApiPy.py


To Get Data from ElasticSearch according Index and Id:

    $>curl localhost:5000/GetData -d '{"index":"experiments", "id":"d_pNsHsBFqb7-mBbFsuM"}' -H 'Content-Type: application/json'

To Search Data from ElasticSearch according Index and Type:


    $>curl localhost:5000/SearchDataByIndexAndKey -d '{"index":"experiments", "key":"Type", "value":"pageview"}' -H 'Content-Type: application/json'


To Get Experiement Result from ElasticSearch :

    $>curl localhost:5000/MVPExperimentResults -d '{"Flag" : {"Id": "FF__2__2__4__ffc-multi-variation-cache-test-data1-1630579986592","BaselineVariation": "A", "Variations" : ["A","Green"]}, "EventName": "TestEvent", "StartExptTime": 1631886446, "EndExptTime": 1631886480}' -H 'Content-Type: application/json' 

Visualiz the Json data in : https://jsongrid.com/json-grid