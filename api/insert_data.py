from ExperimentApiPy import app
from api.elastic_connection import connect_elasticsearch
from flask import jsonify, request
from datetime import datetime
import collections
from datetime import datetime

###########################################
# Insert test flag usage events to 
# Elastic index : "ffvariationrequestindex"
###########################################

es = connect_elasticsearch()

@app.route('/api/InsertFlagUsageEvent', methods=['GET'])
def add_flagevent():

    group = 0
    for user in range(1):
        N = "u_group"+str(group)+"_"+str(user)
        user_obj = {
          "RequestPath" : "index/pay",
          "FeatureFlagId" : "FF__38__48__103__test-liang",
          "EnvId" : "103",
          "AccountId" : "38",
          "ProjectId" : "48",
          "FeatureFlagKeyName" : "test-liang",
          "UserKeyId" : N+"@testliang.com",
          "FFUserName" : N,
          "VariationLocalId" : "1",
          "VariationValue" : "true",
          "TimeStamp" : datetime.now(),
          "phoneNumber" : "135987652543"
        }
        result = es.index(index='ffvariationrequestindex',  body=user_obj, request_timeout=10)

    return jsonify(result)


###########################################
# Insert test custom events to 
# Elastic index : "experiments"
###########################################
@app.route('/api/InsertCustomEvent', methods=['GET'])
def add_customevent():

    group = 0
    for user in range(1):
        N = "u_group"+str(group)+"_"+str(user)
        user_obj = {
          "Route" : "index",
          "Secret" : "YourSecret",
          "TimeStamp" : datetime.now().strftime('%s')+'000',
          "Type" : "CustomEvent",
          "EventName" : "clickButtonPaytest",
          "User" : {
            "FFUserName" : N,
            "FFUserEmail" : N+"@testliang.com",
            "FFUserCountry" : "China",
            "FFUserKeyId" : N+"@testliang.com",
            "FFUserCustomizedProperties" : [ ]
          },
          "AppType" : "Javascript",
          "CustomizedProperties" : [
            {
              "Name" : "age",
              "Value" : "16"
            }
          ],
          "ProjectId" : "48",
          "EnvironmentId" : "103",
          "AccountId" : "38"
        }
        result = es.index(index='experiments',  body=user_obj, request_timeout=10)
        
    return jsonify(result)