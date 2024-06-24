import json
import nltk
import logging
import pandas as pd
from functions.mongo_utils import *
from functions.chroma_utils import *
from functions.openai_utils import *
from sentence_transformers import SentenceTransformer

nltk.download('stopwords')
# Obtener stopwords en español
stopwords_es = nltk.corpus.stopwords.words('spanish')
stopword_en = nltk.corpus.stopwords.words('english')
stopwords = stopwords_es + stopword_en
model_embedding = SentenceTransformer('paraphrase-MiniLM-L6-v2') 
collection_mongo_transcription = init_mongodb("Metadata", "Transcription")
collection_mongo_silences = init_mongodb("Metadata", "Silences")
collection_chroma = init_chroma('databases2','Transcription')
client_openai = init_openai()

def get_best_match(user_query):   
    print('>>> 1')
    list_candidates = get_candidates(user_query)
    print('>>> 2')
    tool, arguments, usage = get_response_gpt(user_query, list_candidates)
    print('>>> 3')
    metrics = get_metrics(arguments, list_candidates)
    print('>>> 4')
    resume_candidates = get_resume_candidates(list_candidates)
    print('>>> 5')
    response = {
        "Response": arguments,
        "UsagePrompt": usage.prompt_tokens,
        "UsageCompletion": usage.completion_tokens,
        "UsageTotal": usage.total_tokens,
        "Candidates": resume_candidates,
        "Metrics": metrics
    }
    return response

def get_candidates(user_query):
    window = 10
    list_candidates = []
    clean_user_query = ' '.join([i for i in user_query.lower().split(' ') if i not in stopwords])
    query_embedding = model_embedding.encode(clean_user_query).tolist()
    results_chroma = search_chroma(collection_chroma, None, query_embedding, {}, 5)
    print('=======================================================================')
    print(results_chroma['documents'][0])
    print('======================.......====·······================================')
    if results_chroma['ids']:  # Verificar si hay resultados
        for i, document in enumerate(results_chroma['documents'][0]):
            # Imprimir metadatos si es necesario (ajusta las claves según tus metadatos)
            print(results_chroma['ids'][0][i])
            id = results_chroma['ids'][0][i]
            score = results_chroma['distances'][0][i]
            metadata = results_chroma['metadatas'][0][i]
            start_time = metadata['StartTime'] - window
            end_time = metadata['EndTime'] + window
            file_id = metadata['FileId']
            file_name = metadata['FileName']
            folder_name = metadata['FolderName']

            pipeline = [
                {
                    "$project": {
                        "FileId": 1,
                        "Transcription": 1
                    }
                },
                { "$unwind": "$Transcription" },
                {
                    "$match": {
                        "$and": [
                            { "Transcription.StartTime": { "$gte": start_time } },
                            { "Transcription.EndTime": { "$lte": end_time } },
                            { "FileId": file_id }
                        ]
                    }
                },
                {
                    "$group": {
                        "_id": "$FileId",
                        "Transcriptions": { "$push": "$Transcription" }
                    }
                }
            ]

            # Ejecutar la consulta
            results_mongo = aggregate_mongodb(collection_mongo_transcription, pipeline)
            transcriptions = results_mongo[0]['Transcriptions']
            candidate = {
                #"Score":score,
                "Subject":folder_name,
                "Video":file_name,
                "StartTimeSeconds":transcriptions[0]['StartTime'],
                #"EndTimeSeconds":transcriptions[-1]['EndTime'],
                "Transcript": ' '.join([i['Text'].strip() for i in transcriptions])
            }
            list_candidates.append(candidate)

            print('-------------------Candidato----------------------------')
            print(candidate)
    else:
        print("No se encontraron resultados.")

    #list_candidates_sorted = sorted(list_candidates, key=lambda x: x['Score'], reverse=True)
    return list_candidates

def get_response_gpt(user_query, list_candidates):
    prompt = f'''
    Ayudas a determinar los mejores candidatos para responder a la petición del cliente, tú única fuente de conocimiento son los candidatos.
    ### UserQuery: {user_query}
    ### Candidates: {json.dumps(list_candidates[0:5])}
    ### Si no encuentras un candidato adecuado respondes que no se encontró informción.
    '''
    messages = [{"role": "user", "content": prompt}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_response",
                "description": "Respondes a las dudas del usuarios en base a los datos candidatos.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "UserResponse": {
                            "type": "string",
                            "description": "Contiene una respuesta coherente a la duda del usuario en base al candidato más acorde.", 
                            },
                        "Reference": {
                            "type": "string",
                            "description": "Contiene la referencia en base al candidato más acorde al query del usuario, debe incluir: nombre de la manteria, video y toma en cuenta que el inicio está en segundos y debes convertirlo a minutos.", 
                            },
                        "Keywords": {
                            "type": "string",
                            "description": "Obtiene las keywords en base al candidato más acorde y el query del usuario." 
                            },
                        "SubjectName": {
                            "type": "string",
                            "description": "Nombre de la materia según los datos del candidato más acorde que suele llamarse subjectname." 
                            },
                        "VideoName": {
                            "type": "string",
                            "description": "Nombre del video según los datos del candidato más acorde, que termina en .mp4" 
                            },
                        "SegundoInicio": {
                            "type": "string",
                            "description": "Segundos en que inicia en base al candidato más acorde que viene del campo StartTimeSeconds." 
                            }
                    },
                    "required": ['UserResponse', 'Reference', 'Keywords', 'SubjectName', 'VideoName', 'SegundoInicio'],
                },
            },
        }
    ]

    return tool_openai(client_openai,'gpt-3.5-turbo',messages,tools)

def get_metrics(arguments, list_candidates):
    # Palabras clave a buscar
    print(arguments)
    logging.info(arguments)
    target_words = [i.lower() for i in arguments['Keywords'].split(',')]

    # Archivos de interés (nombre de archivo: nombre de carpeta)
    target_files = {}
    for i in list_candidates:
        if i['Video'] not in target_files.keys():
            target_files[i['Video']] = i['Subject']

    # Lista para almacenar los segmentos coincidentes
    matching_segments = []

    # Consulta para filtrar por archivos y carpetas de interés
    query = {
        'FileName': {'$in': list(target_files.keys())},
        'FolderName': {'$in': list(target_files.values())}
    }

    # Iterar sobre los documentos que coinciden con la consulta
    result_query_transcript = query_mongodb(collection_mongo_transcription, query)
    result_query_silence = query_mongodb(collection_mongo_silences, query)

    for document in result_query_transcript:
        for segment in document['Transcription']:
            # Dividir el texto en palabras, convertir a minúsculas y eliminar stopwords
            words = [word for word in segment['Text'].lower().split() if word not in stopwords]
            
            # Verificar si todas las palabras de alguna frase clave están presentes
            for phrase in target_words:
                phrase_words = phrase.split()
                if all(word in words for word in phrase_words):
                    match_silence = [i for i in result_query_silence if i['FileId'] == document['FileId']][0]
                    matching_segments.append({
                        'StartTime': segment['StartTime'],
                        'EndTime': segment['EndTime'],
                        'FileName': document['FileName'],
                        'FolderName': document['FolderName'],
                        'FileId': document['FileId'],
                        'TotalTranscriptionTime': match_silence['TotalTranscriptionTime'],
                        'Duration': match_silence['Duration'],
                        'SilenceTime': match_silence['SilenceTime']
                    })
                    break  # Salir del bucle si se encuentra una coincidencia

    # Crear un DataFrame con los resultados (si es necesario)
    df_matching_segments = pd.DataFrame(matching_segments)
    # Calculate time difference
    df_matching_segments['TimeDiff'] = df_matching_segments['EndTime'] - df_matching_segments['StartTime']

    # Group by FileName and FolderName, and sum TimeDiff
    df_result = df_matching_segments.groupby(['FileId', 'FileName', 'FolderName', 'TotalTranscriptionTime', 'Duration', 'SilenceTime'])['TimeDiff'].sum().reset_index()

    # Rename TimeDiff to AccumulatedTime
    df_result = df_result.rename(columns={'TimeDiff': 'AccumulatedTime'})

    df_result_sorted = df_result.sort_values(by='AccumulatedTime', ascending=False)

    # return results
    return df_result_sorted.to_dict(orient='records')

def get_resume_candidates(list_candidates):
    for i in list_candidates:
        messages = [{"role": "user", "content": "Dame un resumen corto: " + i['Transcript'] }]
        resume, usage = completion_openai(client_openai,'gpt-3.5-turbo', messages)
        i['Resume'] = resume

    return list_candidates
