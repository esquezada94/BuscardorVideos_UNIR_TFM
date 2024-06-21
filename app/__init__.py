from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from app.functions_app import * 

@app.route('/')
def hello():
    return "Hola desde Flask y Docker!"

@app.route('/ejemplo_get', methods=['GET'])
def ejemplo_get():
    nombre = request.args.get('nombre', 'Desconocido')  # Obtiene 'nombre' de la URL
    response = get_best_match()
    return response

@app.route('/search_video', methods=['POST'])
def ejemplo_post_json():
    datos = request.get_json()  # Obtiene los datos JSON
    user_query = datos.get('prompt', 'No hay preguntas.') 
    response = get_best_match(user_query) 
    return jsonify(response)  # Devuelve JSON