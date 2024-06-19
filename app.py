import os
import uuid
import unicodedata
import pandas as pd
from functions.video_utils import *
from functions.mongo_utils import *
from functions.chroma_utils import *

# Nombre de la base de datos y colección
collection_mongo = init_mongodb("Metadata", "Transcription")
model_transcript = init_video('tiny')
collection_chroma = init_chroma('Transcription')

audios_list = []
path_videos = 'Videos/'
folders = os.listdir(path_videos)
for folder in folders:
    path_files = os.listdir(path_videos + folder)
    for file in path_files:
        if '.mp3' not in file:
            video_file = f'{path_videos}{folder}/{file}'
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
                list_transcriptions = transcript_video(model_transcript, audio_file)
                data_video = {
                    "FileId": file_id,
                    "FileName": file,
                    "FolderName": folder,
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

                total_count = collection_chroma.count()
                print(f"Total de elementos en la colección: {total_count}")
            else:
                print('Video procesado: ', video_file)