# ExperimentApiPy

Under "ExperimentApiPy/config", create file "config.ini".
In this file, put lines:

    [elastic]
    es_host =  http://localhost:9200

Then repalce localhost by your elasticsearch url.


Run:

    $>python ExperimentApiPy.py


To Get Data from ElasticSearch according Index and Id:

    $>curl localhost:5000/GetData -d '{"index":"experiments", "id":"d_pNsHsBFqb7-mBbFsuM"}' -H 'Content-Type: application/json'

To Search Data from ElasticSearch according Index and Type:


    $>curl localhost:5000/SearchDataByIndexAndKey -d '{"index":"experiments", "key":"Type", "value":"pageview"}' -H 'Content-Type: application/json'

