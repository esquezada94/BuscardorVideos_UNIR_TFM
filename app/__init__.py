from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from app.functions_app import * 

@app.route('/')
def hello():
    return "Aplicación para la exploración de videos usando LLMs."

@app.route('/search_video', methods=['POST'])
def http_search_video():
    datos = request.get_json()  # Obtiene los datos JSON
    user_query = datos.get('prompt', 'No hay preguntas.') 
    response = get_best_match(user_query) 
    return jsonify(response)  # Devuelve JSON