import json
import logging
from functions.mongo_utils import *
from functions.chroma_utils import *
from functions.openai_utils import *

collection_mongo = init_mongodb("Metadata", "Transcription")
collection_chroma = init_chroma('Transcription')
client_openai = init_openai()

def get_best_match(user_query):   
    logging.info('########################################################') 
    logging.info(user_query) 
    list_candidates = get_candidates(user_query)
    logging.info('########################################################') 
    logging.info(list_candidates) 
    tool, arguments, usage = get_response_gpt(user_query, list_candidates)
    logging.info('###########################ARGUMENTS#############################') 
    logging.info(arguments) 
    logging.info('##########################USAGE##############################') 
    logging.info(usage) 
    print(usage)
    response = {
        "Response": arguments,
        "UsagePrompt": usage.prompt_tokens,
        "UsageCompletion": usage.completion_tokens,
        "UsageTotal": usage.total_tokens
    }
    return response

def get_candidates(user_query):
    window = 10
    list_candidates = []
    results_chroma = search_chroma(collection_chroma, [user_query], {}, 10)
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
            results_mongo = aggregate_mongodb(collection_mongo, pipeline)
            transcriptions = results_mongo[0]['Transcriptions']
            candidate = {
                "Score":score,
                "Subject":folder_name,
                "Video":file_name,
                "StartTimeSeconds":transcriptions[0]['StartTime'],
                "EndTimeSeconds":transcriptions[-1]['EndTime'],
                "Transcript": ' '.join([i['Text'].strip() for i in transcriptions])
            }
            list_candidates.append(candidate)

            print('-------------------Candidato----------------------------')
            print(candidate)
    else:
        print("No se encontraron resultados.")

    list_candidates_sorted = sorted(list_candidates, key=lambda x: x['Score'], reverse=True)
    return list_candidates_sorted

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
                            "description": "Contiene una respuesta coherente a la duda del usuario.", 
                            },
                        "References": {
                            "type": "string",
                            "description": "Contiene las referencias del candidato que se le responde al usuario, debe incluir: nombre de la manteria, video y los minutos.", 
                            },
                        "Keywords": {
                            "type": "string",
                            "description": "Obtiene las palabras clave más relevantes en base a la temática." 
                            },
                        "SubjectName": {
                            "type": "string",
                            "description": "Nombre de la materia que es mejor candidato." 
                            },
                        "VideoName": {
                            "type": "string",
                            "description": "Nombre del video que es mejor candidato." 
                            },
                        "SegundoInicio": {
                            "type": "string",
                            "description": "Segundos en que inicia el mejor candidato." 
                            }
                    },
                    "required": ['UserResponse', 'References', 'Keywords', 'SubjectName', 'VideoName'],
                },
            },
        }
    ]

    return tool_openai(client_openai,'gpt-3.5-turbo',messages,tools)