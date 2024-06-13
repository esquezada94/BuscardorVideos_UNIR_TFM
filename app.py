import os
import whisper
import torch
import pymongo
from moviepy.editor import VideoFileClip

# Verificar si CUDA está disponible
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)

def change_video_extension_to_mp3(video_file):
  """
  Cambia la extensión de un archivo de video a .mp3, conservando el nombre base.

  Args:
      video_file (str): La ruta completa al archivo de video (e.g., 'videos/mi_video.mov').

  Returns:
      str: La ruta completa al nuevo archivo de audio con extensión .mp3 (e.g., 'videos/mi_video.mp3').
  """
  
  # Divide la ruta del archivo en directorio, nombre base y extensión
  directory, file_name = os.path.split(video_file)
  base_name, extension = os.path.splitext(file_name)

  # Construye la nueva ruta con la extensión .mp3
  audio_file = os.path.join(directory, base_name + ".mp3")
  
  return audio_file

def convert_video_to_audio(video_file, audio_file, end_time=600, bitrate="1600k"):
    """
    Convierte los primeros minutos de un video a audio MP3 con una tasa de bits determinada.

    Args:
        video_file (str): Ruta al archivo de video de entrada.
        audio_file (str): Ruta al archivo de audio de salida (MP3).
        end_time (int): Tiempo en segundos en el que finalizar la conversión (por defecto, 10 minutos = 600 segundos).
        bitrate (str): Tasa de bits del audio de salida (por defecto, 1600 kbps).
    """
    video = VideoFileClip(video_file).subclip(0, end_time)  # Recorta el video hasta end_time
    duration = video.duration  # Duración en segundos
    size = video.size  # Tamaño en bytes (ancho, alto)

    # Convertir tamaño a MB (opcional)
    size_mb = (size[0] * size[1] * 3) / (1024 * 1024) 
    audio = video.audio
    audio.write_audiofile(audio_file, bitrate=bitrate)

    return duration, size_mb

# Cargar el modelo en el dispositivo adecuado (GPU o CPU)
#tiny base small medium large
model = whisper.load_model("tiny").to(device)

def get_transcript(audio_file):
    # Transcribir el audio, especificando el dispositivo
    result = model.transcribe(audio_file)

    # Imprimir el texto transcrito

    list_transcriptions = []

    for i in result['segments']:
        list_transcriptions.append({
            "Id": i['id'],
            "StartTime": i['start'],
            "EndTime": i['end'],
            "Text": i['text']
        })
        print(i['id'], i['start'], i['end'], i['text'])
    
    return list_transcriptions

def save_mongodb(data):
    # Conexión al servidor MongoDB (reemplaza con tus datos)
    client = pymongo.MongoClient("mongodb://localhost:27017/")  

    # Nombre de la base de datos y colección
    db_name = "Metadata"
    collection_name = "Transcription"

    # Obtener la base de datos y colección (se crea si no existe)
    db = client[db_name]
    collection = db.get_collection(collection_name)

    # Insertar el documento
    resultado = collection.insert_one(data)

    # Imprimir el ID del documento insertado
    print("Documento insertado con ID:", resultado.inserted_id)

audios_list = []
path_videos = 'Videos/'
folders = os.listdir(path_videos)
for folder in folders:
    path_files = os.listdir(path_videos + folder)
    for file in path_files:
        if '.mp3' not in file:
            video_file = f'{path_videos}{folder}/{file}'
            audio_file = change_video_extension_to_mp3(video_file)
            duration, size_mb = convert_video_to_audio(video_file, audio_file)
            audios_list.append(audio_file)
            list_transcriptions = get_transcript(audio_file)
            data_video = {
                "FileName": file,
                "Duration": duration,
                "SizeMb": size_mb,
                "Transcription": list_transcriptions
            }
            save_mongodb(data_video)
