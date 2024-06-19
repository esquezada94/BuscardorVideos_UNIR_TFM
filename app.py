import os
import uuid
import unicodedata
import pandas as pd
from datetime import datetime
from functions.video_utils import *
from functions.mongo_utils import *
from functions.chroma_utils import *

# Nombre de la base de datos y colección
collection_mongo = init_mongodb("Metadata", "Transcription")
model_transcript = init_video('medium')
collection_chroma = init_chroma('Transcription')
audios_list = []
path_videos = 'Videos/'
folders = os.listdir(path_videos)
for folder in folders:
    path_files = os.listdir(path_videos + folder)
    for file in path_files:
        if '.mp3' not in file:
            start_time = datetime.now()
            video_file = f'{path_videos}{folder}/{file}'
            try:
                filter = {
                    "FolderName": folder,
                    "FileName": file
                }
                result = query_mongodb(collection_mongo, filter)
                if len(result) == 0: #Comentar este if para volver a ejecutar y reemplazar los videos analizados
                    audio_file = change_extension_video(video_file)
                    print(video_file, audio_file)
                    duration, size_mb = convert_video(video_file, audio_file)
                    audios_list.append(audio_file)
                    file_id = str(uuid.uuid4())
                    print('Iniciando transcription ', datetime.now())
                    list_transcriptions = transcript_video(model_transcript, audio_file)
                    print('Fin transcription ', datetime.now())
                    end_time = datetime.now()
                    data_video = {
                        "FileId": file_id,
                        "FileName": file,
                        "FolderName": folder,
                        "Duration": duration,
                        "StartDatetime": start_time,
                        "EndDatetime": end_time,
                        "Duration": duration,
                        "SizeMb": size_mb,
                        "Transcription": list_transcriptions
                    }
                    
                    delete_mongodb(collection_mongo, filter)
                    save_mongodb(collection_mongo, data_video)
                    df_transcriptions = pd.DataFrame(list_transcriptions)
                    list_ids = df_transcriptions['TranscriptId'].tolist()
                    list_text = df_transcriptions['Text'].tolist()
                    df_metadata = df_transcriptions.drop(["Text", "TranscriptId"], axis=1)
                    df_metadata['FileId'] = file_id
                    df_metadata['FileName'] = file
                    df_metadata['FolderName'] = folder
                    dict_metadata = df_metadata.to_dict(orient='records')
                    filter = {
                        "$and": [
                            {"FolderName": folder},
                            {"FileName": file}
                        ]
                    }
                    delete_from_chroma(collection_chroma, filter)
                    save_data_chroma(collection_chroma, list_ids, list_text, dict_metadata)

                    print(f"Total de elementos en la colección: {len(list_transcriptions)}")
                    print('--------------------------------------------------------')
                    print('--------------------------------------------------------')
                    del list_transcriptions
                    del data_video
                    del df_transcriptions
                    del list_ids
                    del list_text
                    del df_metadata
                    del dict_metadata
                else:
                    print('Video procesado: ', video_file)
                    print('--------------------------------------------------------')
                    print('--------------------------------------------------------')
                
            except Exception as e:
                print( "Error al procesar video: ", video_file,'. ERROR: ', e)