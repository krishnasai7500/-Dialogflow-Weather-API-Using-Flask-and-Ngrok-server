from __future__ import print_function
#from future.standard_library import install_aliases
#install_aliases()
import requests
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
#from flask import Flask, render_template, request

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    #return 'hello'
    #print(req)

    #print("Request:")
    # commented out by Naresh
    #print(json.dumps(req, indent=4))

    res = processRequest(req)
    #print(res)

    #res = json.dumps(res, indent=4)
    # print(res)
    #r = make_response(res)
    #r.headers['Content-Type'] = 'application/json'
    print(res)
    return res


def processRequest(req):
    #print ("starting processRequest...",req.get("queryResult").get("action"))
    if req.get("queryResult").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1"
    yql_query,city = makeYqlQuery(req)
    if yql_query is None:
        return {}
    r = requests.get(baseurl.format(city)).json()
    #print(baseurl.format(city))
    # yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    # print(yql_url)
    # result = urlopen(yql_url).read()
    #data = json.loads(result)
    #for some the line above gives an error and hence decoding to utf-8 might help
    #data = json.loads(r)
    res = makeWebhookResult(r,city)
    return res


def makeYqlQuery(req):
    #print(req)
    req=req.get("queryResult")
    parameters = req.get("parameters")
    #print(parameters)
    result = parameters.get("geo-county-us")
    print("---------")
    print(result)

    #result=result[0]
    city=result['city']

    #print(result.get('city'))
   # parameters = result.get("parameters")
    #city = result.get("city")
    if city is None:
        return None
    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')",city


def makeWebhookResult(data,city):
   main1=data['weather'][0]
   main2=data['main']
   celsius=(main2['temp']-32)*0.5555
   celsius=truncate(celsius,2)
   #print(type(main2['temp']))
   speech = "Today the weather in " + city + " is " + main1['description'] + \
              ", And today's temperature is " + str(celsius) + "^" + 'C'
   return {
        "fulfillmentText": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }
def truncate(num, n):
    integer = int(num * (10**n))/(10**n)
    return float(integer)

@app.route('/test', methods=['GET'])
def test():
    return  "Hello there my friend !!"

@app.route('/static_reply', methods=['POST'])
def static_reply():
    speech = "Hello there, this reply is from the webhook !! "
    my_result =  {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
       # "source": "apiai-weather-webhook-sample"
    }
    res = json.dumps(my_result, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
if __name__ == "__main__":
    app.run(port= 80,debug=True)