# Import libraries
import flask
from flask import render_template, jsonify, request, abort
from flask.wrappers import Response
import pandas as pd
import numpy as np
import pickle
import pathlib

from werkzeug.wrappers import response


# Import Models
appDirPath = pathlib.Path(__file__).parent.resolve()
modelPath = appDirPath / 'model.pkl'
model_file = open(modelPath, "rb")
model = pickle.load(model_file)

# Function for predict rol
def predictRol(newAge):
    if newAge < 0 or newAge > 120 :
        return "invalid"

    nueva_persona = pd.DataFrame(np.array([[newAge]]),columns=['edad'])

    prediccion = model.predict(nueva_persona)
    prediccion_df = pd.DataFrame(prediccion, columns=['rol'])

    resultados = pd.concat([nueva_persona.set_index(prediccion_df.index), prediccion_df], axis=1)

    roles_resultado = {"rol":  {0:'hijo', 1:'padre', 2:'abuelo'}}
    resultados.replace(roles_resultado, inplace=True)

    print(resultados)

    return resultados['rol'][0]

# Create Flask App
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Routes
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/api', methods=['GET'])
def ageCalculate():
    age = request.args.get('age')

    # If age is not int, return error 400
    try:
        age = int(age)
    except:
        invalidResponse = Response(status=400)
        invalidResponse.headers.add('Access-Control-Allow-Origin', '*')
        return abort(invalidResponse)

    # Get prediction
    result = predictRol(age)

    # If prediction gives an error, return error 400
    if result == "invalid":
        invalidResponse = Response(status=400)
        invalidResponse.headers.add('Access-Control-Allow-Origin', '*')
        return abort(invalidResponse)

    response = jsonify(rol=result)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response, 200
     
app.run(host='0.0.0.0')