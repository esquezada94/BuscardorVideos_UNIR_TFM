import whisper
import torch

# Verificar si CUDA está disponible
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)

# Cargar el modelo en el dispositivo adecuado (GPU o CPU)
model = whisper.load_model("medium").to(device)

# Ruta al archivo de audio que quieres transcribir
audio_path = "Audios/Grabacion1.m4a"

# Transcribir el audio, especificando el dispositivo
result = model.transcribe(audio_path)

# Imprimir el texto transcrito
print(result["text"])