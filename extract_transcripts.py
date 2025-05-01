#!/usr/bin/env python3
"""
Script para extraer transcripciones de vídeos de YouTube (individuales o de una playlist)
y generar un archivo Markdown con secciones para cada vídeo.

Dependencias:
    pip install yt-dlp youtube-transcript-api requests

Uso:
    # Para una playlist:
    python extract_transcripts.py --playlist PLAYLIST_URL --output transcripts.md

    # Para vídeos individuales:
    python extract_transcripts.py --videos VIDEO_URL1 VIDEO_URL2 --output transcripts.md
"""

from __future__ import annotations

import argparse
import os
import random
import re
import sys
import time
from datetime import datetime
from typing import List, Optional, Tuple, Dict, TextIO

import requests
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

class VideoInfo:
    """Clase para almacenar información del video."""
    def __init__(self, title: str, video_id: str) -> None:
        self.title = title
        self.video_id = video_id

class YouTubeTranscriptExtractor:
    """Clase principal para extraer transcripciones de YouTube."""
    
    def __init__(self) -> None:
        self.ydl_opts: Dict[str, bool] = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'ignoreerrors': True,
        }

    def get_playlist_info(self, playlist_url: str) -> Tuple[Optional[str], List[str]]:
        """Obtiene el título y los videos de una playlist."""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                if not playlist_info:
                    return None, []
                
                videos: List[str] = []
                for entry in playlist_info.get('entries', []):
                    if entry:
                        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                        videos.append(video_url)
                
                return playlist_info.get('title'), videos
        except Exception as e:
            print(f"Error al obtener la playlist: {str(e)}", file=sys.stderr)
            return None, []

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extrae el ID del video de una URL de YouTube."""
        patterns = [
            r'(?:v=|/v/|^)([^&\n?#]+)',
            r'(?:youtu\.be/|youtube\.com/embed/)([^?\n&]+)',
            r'(?:watch\?v=|v/|embed/|youtu\.be/)([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_video_info_fallback(self, url: str) -> Optional[VideoInfo]:
        """Método alternativo para obtener información del video usando la API de oEmbed."""
        video_id = self.extract_video_id(url)
        if not video_id:
            return None
            
        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            response = requests.get(oembed_url)
            if response.status_code == 200:
                data = response.json()
                return VideoInfo(
                    title=data.get('title', ''),
                    video_id=video_id
                )
        except Exception as e:
            print(f"Error en fallback para {url}: {str(e)}", file=sys.stderr)
        
        return None

    @staticmethod
    def fetch_transcript(video_id: str, languages: List[str] = ['es', 'en']) -> Optional[str]:
        """
        Intenta descargar la transcripción en español o inglés.
        Devuelve el texto completo o None si no está disponible.
        """
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages)
            lines = [item['text'] for item in transcript_list]
            return '\n'.join(lines)
        except TranscriptsDisabled:
            print(f"Las transcripciones están deshabilitadas para el video {video_id}", file=sys.stderr)
            return None
        except NoTranscriptFound:
            print(f"No se encontró transcripción para el video {video_id}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error al obtener la transcripción del video {video_id}: {str(e)}", file=sys.stderr)
            return None

    def process_video(self, url: str, md_file: TextIO) -> None:
        """Procesa un video individual y escribe su transcripción en el archivo."""
        try:
            video_info: Optional[VideoInfo] = None
            try:
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_info = VideoInfo(
                        title=info.get('title', ''),
                        video_id=info.get('id', '')
                    )
            except:
                video_info = self.get_video_info_fallback(url)
            
            if not video_info:
                print(f"No se pudo obtener información del video: {url}", file=sys.stderr)
                md_file.write(f"## Error al procesar video: {url}\n\n")
                md_file.write("_Error al obtener información del video._\n\n")
                return

            print(f"Procesando video: {video_info.title}")
            md_file.write(f"## {video_info.title}\n\n")
            
            transcript = self.fetch_transcript(video_info.video_id)
            if transcript:
                md_file.write(transcript + "\n\n")
            else:
                md_file.write("_Transcripción no disponible._\n\n")
                
        except Exception as e:
            print(f"Error inesperado al procesar {url}: {str(e)}", file=sys.stderr)
            md_file.write(f"## Error al procesar video: {url}\n\n")
            md_file.write("_Error al procesar el video._\n\n")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extrae transcripciones de YouTube y genera un Markdown"
    )
    parser.add_argument(
        '-p', '--playlist',
        help="URL de la playlist de YouTube"
    )
    parser.add_argument(
        '-v', '--videos', nargs='+',
        help="URLs de vídeos individuales"
    )
    parser.add_argument(
        '-o', '--output', default='transcriptions/transcript.md',
        help="Nombre del archivo Markdown de salida (por defecto: transcriptions/transcript.md)"
    )
    args = parser.parse_args()

    # Asegurar que la carpeta transcriptions existe
    os.makedirs('transcriptions', exist_ok=True)

    if not args.playlist and not args.videos:
        print("Debes especificar una playlist o al menos un video.", file=sys.stderr)
        sys.exit(1)

    video_urls: List[str] = []
    playlist_title: Optional[str] = None
    
    extractor = YouTubeTranscriptExtractor()
    
    if args.playlist:
        print(f"Obteniendo vídeos de la playlist: {args.playlist}")
        playlist_title, playlist_urls = extractor.get_playlist_info(args.playlist)
        if not playlist_urls:
            print("No se pudieron obtener videos de la playlist.", file=sys.stderr)
        video_urls.extend(playlist_urls)
    if args.videos:
        video_urls.extend(args.videos)

    if not video_urls:
        print("No se encontraron URLs de videos para procesar.", file=sys.stderr)
        sys.exit(1)

    with open(args.output, 'w', encoding='utf-8') as md:
        # Escribir encabezado del documento
        if playlist_title:
            md.write(f"# {playlist_title}\n\n")
            md.write(f"[Ver playlist en YouTube]({args.playlist})\n\n")
            md.write(f"_Transcripciones extraídas el {datetime.now().strftime('%d/%m/%Y %H:%M')}_\n\n")
            md.write("---\n\n")
        
        for i, url in enumerate(video_urls, 1):
            print(f"\nProcesando video {i} de {len(video_urls)}")
            extractor.process_video(url, md)
            # Pequeña pausa entre videos
            if i < len(video_urls):
                time.sleep(random.uniform(1.0, 2.0))

    print(f"\nMarkdown generado: {args.output}")

if __name__ == '__main__':
    main()