import os
import uuid
import torch
import whisper
from moviepy.editor import VideoFileClip

def init_video(model_name):
    # Verificar si CUDA está disponible
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(device)

    # Cargar el modelo en el dispositivo adecuado (GPU o CPU)
    #tiny base small medium large
    model = whisper.load_model(model_name).to(device)
    return model

def change_extension_video(video_file):
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
    directory = directory.replace('Videos','Audios')
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Construye la nueva ruta con la extensión .mp3
    audio_file = os.path.join(directory, base_name + ".mp3")
    return audio_file

def convert_video(video_file, audio_file, end_time=600, bitrate="1600k"):
    """
    Convierte los primeros minutos de un video a audio MP3 con una tasa de bits determinada.

    Args:
        video_file (str): Ruta al archivo de video de entrada.
        audio_file (str): Ruta al archivo de audio de salida (MP3).
        end_time (int): Tiempo en segundos en el que finalizar la conversión (por defecto, 10 minutos = 600 segundos).
        bitrate (str): Tasa de bits del audio de salida (por defecto, 1600 kbps).
    """
    video = VideoFileClip(video_file)
    duration = video.duration  # Duración en segundos
    size = video.size  # Tamaño en bytes (ancho, alto)
    end_time = min(end_time, duration) # Ajustar end_time si es necesario
    #video = video.subclip(0, end_time)  # Recorta el video hasta end_time

    # Convertir tamaño a MB (opcional)
    size_mb = (size[0] * size[1] * 3) / (1024 * 1024) 
    audio = video.audio
    audio.write_audiofile(audio_file, bitrate=bitrate)
    del video

    return duration, size_mb

def transcript_video(model, audio_file):
    # Transcribir el audio, especificando el dispositivo
    result = model.transcribe(audio_file)

    # Imprimir el texto transcrito

    list_transcriptions = []

    for i in result['segments']:
        list_transcriptions.append({
            "Id": i['id'],
            "TranscriptId": str(uuid.uuid4()),
            "StartTime": i['start'],
            "EndTime": i['end'],
            "Text": i['text']
        })
        #print(i['id'], i['start'], i['end'], i['text'])
    
    return list_transcriptions