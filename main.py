 #// imports
import json
import os
import requests

from flask import Flask, jsonify, render_template, request
from openai import OpenAI

 #// get secrets
bs1 = os.getenv('BS1')
bs2 = os.getenv('BS2')
bs3 = os.getenv('CLAUDE')
theKey = os.environ['APIKEY']

 #// define some things
client = OpenAI(
  base_url=bs1,
  api_key=theKey
)
app = Flask(__name__)
allowingRequests = True
proxyKey = os.getenv('PROXY-KEY')

 #// functions
def check_auth(request):
  auth_header = request.headers.get('Authorization')
  if auth_header:
      try:
          auth_type, auth_token = auth_header.split(' ')
          if auth_type.lower() == 'bearer' and auth_token == proxyKey:
              return True
      except ValueError:
          pass
  return False
  
def is_openai(string):
  return string.lower().startswith('gpt')

 #// main
@app.route('/api/chat/completions', methods=['POST', 'GET'])
def chatCompletions():
  if request.method == "POST":
    payload = request.get_json()
    allowed = check_auth(request)

    try:

      if allowed and allowingRequests:
         #// get payload vars
        pModel = payload.get('model')
        pMessages = payload.get('messages')
        pTools = payload.get('tools')
        pTemperature = payload.get('temperature')
        pMaxTokens = payload.get('max_tokens')
        pTopP = payload.get('top_p')

         #// is this an openai model??
        isOpenai = is_openai(pModel)
        

         #// generate response or not
        response = {"error": "ig it broke🤷‍♂️"}

        if isOpenai:
          response = client.chat.completions.create(
            model=pModel,
            messages=pMessages,
            temperature=pTemperature,
            max_tokens=pMaxTokens,
            top_p=pTopP,

            tools = pTools
          )
          
           #// get as json cause it isnt normally
          response_dict = response.model_dump()
          response = json.dumps(response_dict, indent=2)
        else:
          nHeaders = {"Content-Type": "application/json"}
          nPayload = {
            "model": pModel,
            "messages": pMessages,
            "temperature": pTemperature,

            "tools": pTools
          }
          response = requests.post(bs2, data=nPayload, headers=nHeaders).text

        return response
        
    except Exception as error:
      return jsonify({"erorr": str(error)})
  return render_template('pages/chatCompletions.html')

@app.route('/', methods=['GET'])
def homePage():
  return render_template('pages/home.html')

@app.route('/docs', methods=['GET'])
def docsPage():
  return render_template('pages/docs.html')

 #// run the flask app
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)