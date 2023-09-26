from flask import Flask, request, jsonify, make_response, redirect
from flasgger import Swagger
from flasgger.utils import swag_from
from flask_cors import CORS
import requests
import os 
from dotenv import load_dotenv
import json

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
    "title": 'Clean IDE - Compiler API',
    "description": 'This API is part of an MVP made for the 3rd Sprint of the Fullstack Developper graduate course at PUC-RJ',
    "termsOfService": 'Termos de Serviço',
    "contact": {
        "email": "vinians2006@yahoo.com.br"
    },
    "license": {
        "name": "Licença",
        "url": ""
    },
}

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

# TODAS AS ROTAS
# -------------------------------------
@app.before_request
def before_request_func():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'content-type')
        return response


CORS(app, origins='*', methods='*', allow_headers='*')
swagger = Swagger(app=app, config=swagger_config)

load_dotenv()


# ROUTE /compile (POST) CALL A EXTERNAL COMPILER
# ----------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return redirect('/apidocs', code=302)


# ROUTE /compile (POST) CALL A EXTERNAL COMPILER
# ----------------------------------------------
@app.route('/compile', methods=['POST', 'OPTIONS'])
@swag_from('docs/compile.yml')
def compile_code():

    # INFO ACCORD TO THE SELECTED API
    #--------------------------------------------------------------------
    keys     = [os.getenv("RAPIDAPI_KEY_1"), os.getenv("RAPIDAPI_KEY_2")]
    urls     = [os.getenv("RAPIDAPI_URL_1"), os.getenv("RAPIDAPI_URL_2")]
    hosts    = [os.getenv("RAPIDAPI_HOST_1"), os.getenv("RAPIDAPI_HOST_2")]

    langs    = [
                {"python":"python3", "c":"c", "java":"java"},
                {"python":"python", "c":"c", "java":"java"},
               ]

    files    = [
                {"python":"file.py", "c":"file.c", "java":"file.java"},
                {"python":"file.py", "c":"file.c", "java":"file.java"},
               ]
    
    # WHAT API WE WILL USE ?
    #--------------------------------------------------------------------
    what_api = int(os.getenv("USE_API_NUMBER"));

    data        = request.json
    code_to_run = data['code']
    lang        = data['language'].lower()
    stdin       = data['input']
    
    lang        = langs[what_api - 1][lang];
    file        = files[what_api - 1][lang];

    what_key    = keys[what_api - 1]
    what_url    = urls[what_api - 1]
    what_host   = hosts[what_api - 1]

    url = what_url
    host = what_host

    headers = {
        'content-type': 'application/json',
        'X-RapidAPI-Key': what_key,
        'X-RapidAPI-Host': host
    }

    if (what_api == 1):
        body = {
            'language': lang,
            'version': 'latest',
            'code': code_to_run,
            'input': stdin
        }

    if (what_api == 2):
        body = {
	        "language": lang,
	        "stdin": stdin,
	        "files": [
		        {   
	    		    "name": file,
    			    "content": code_to_run       
                }
            ]}
        
    #print(url)
    #print(json.dumps(headers, indent=4))
    #print(json.dumps(body, indent=4))

    try:
        response = requests.post(url, headers=headers, json=body)
        responsej = response.json()
        status = responsej['status']
        print(responsej)
  
        # MAKE RESPONSE DICTIONARY ACCORD TO THE TYPE OF API USED
        #---------------------------------------------------------
        if (what_api == 1):
            if (status != "failed"):
                result = {
                    "status":responsej['status'],
                    "stderr":responsej['stderr'],
                    "output":responsej['stdout'],
                    "time":responsej['executionTime'],
                    "memory":""
                } 
            else:
                result = {
                    "status":responsej['status'],
                    "stderr":"",
                    "output":responsej['error'],
                    "time":"",
                    "memory":""
                }

        if (what_api == 2):
            if (status != "failed"):
                result = {
                    "status":responsej['status'],
                    "stderr":responsej['stderr'],
                    "output":responsej['stdout'],
                    "time":responsej['executionTime'],
                    "memory":""
                } 
            else:
                result = {
                    "status":responsej['status'],
                    "stderr":"",
                    "output":responsej['error'],
                    "time":"",
                    "memory":""
                }
        return result
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
