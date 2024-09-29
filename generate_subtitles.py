import speech_recognition as sr
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import os

def extract_audio(video_path, audio_path):
    """Extraire l'audio d'une vidéo et le sauvegarder au format WAV."""
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def generate_subtitles(audio_path):
    """Générer des sous-titres à partir d'un fichier audio."""
    recognizer = sr.Recognizer()
    subtitles = []
    
    # Chargement de l'audio
    audio = AudioSegment.from_wav(audio_path)
    
    # Diviser l'audio en morceaux de 30 secondes
    for i in range(0, len(audio), 30000):
        chunk = audio[i:i+30000]
        chunk_path = f"chunk_{i//30000}.wav"
        chunk.export(chunk_path, format="wav")

        # Reconnaissance vocale
        with sr.AudioFile(chunk_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language='fr-FR')
                start_time = i / 1000  # Convertir ms en s
                end_time = (i + len(chunk)) / 1000
                subtitles.append((start_time, end_time, text))
            except sr.UnknownValueError:
                print(f"Impossible de comprendre l'audio dans le segment {i//30000}.")
            except sr.RequestError as e:
                print(f"Erreur de service de reconnaissance vocale : {e}")

        os.remove(chunk_path)  # Supprimer le fichier audio temporaire

    return subtitles

def save_subtitles(subtitles, output_file):
    """Sauvegarder les sous-titres au format SRT."""
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, (start, end, text) in enumerate(subtitles):
            f.write(f"{i+1}\n")
            f.write(f"{format_time(start)} --> {format_time(end)}\n")
            f.write(f"{text}\n\n")

def format_time(seconds):
    """Formatter le temps en heures:minutes:secondes,millisecondes."""
    millis = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    hours, minutes = divmod(seconds, 3600)
    minutes, seconds = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

if __name__ == "__main__":
    video_path = "votre_video.mp4"  # Remplacez par le chemin de votre vidéo
    audio_path = "audio.wav"
    
    extract_audio(video_path, audio_path)
    subtitles = generate_subtitles(audio_path)
    save_subtitles(subtitles, "sous_titres.srt")

    # Nettoyage
    os.remove(audio_path)
