import os
import whisper
import torch
from moviepy.editor import VideoFileClip

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
    audio = video.audio
    audio.write_audiofile(audio_file, bitrate=bitrate)

audios_list = []
path_videos = 'Videos/'
folders = os.listdir(path_videos)
for folder in folders:
    path_files = os.listdir(path_videos + folder)
    for file in path_files:
        if '.mp3' not in file:
            video_file = f'{path_videos}{folder}/{file}'
            audio_file = change_video_extension_to_mp3(video_file)
            convert_video_to_audio(video_file, audio_file)
            audios_list.append(audio_file)


# Verificar si CUDA está disponible
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)

# Cargar el modelo en el dispositivo adecuado (GPU o CPU)
model = whisper.load_model("tiny").to(device)
#tiny base small medium large

# Ruta al archivo de audio que quieres transcribir
audio_path = audios_list[0]

# Transcribir el audio, especificando el dispositivo
result = model.transcribe(audio_path)

# Imprimir el texto transcrito

for i in result['segments']:
    print(i['id'], i['start'], i['end'], i['text'])
