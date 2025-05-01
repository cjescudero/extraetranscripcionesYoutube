# Extractor de Transcripciones de YouTube

Esta herramienta permite extraer transcripciones de videos de YouTube, ya sea de videos individuales o de una lista de reproducción completa. Las transcripciones se guardan en un archivo Markdown, con secciones separadas para cada video.

## Instalación

```bash
uv pip install pytube youtube-transcript-api
```

## Uso

### Para extraer transcripciones de una lista de reproducción:

```bash
python extract_transcripts.py --playlist "URL_DE_LA_PLAYLIST" --output transcripts.md
```

### Para extraer transcripciones de videos individuales:

```bash
python extract_transcripts.py --videos "URL_VIDEO1" "URL_VIDEO2" --output transcripts.md
```

### Opciones disponibles:

- `-p, --playlist`: URL de la lista de reproducción de YouTube
- `-v, --videos`: Una o más URLs de videos individuales
- `-o, --output`: Nombre del archivo de salida (por defecto: transcripts.md)

## Formato de Salida

El script genera un archivo Markdown con el siguiente formato:

```markdown
## [Título del Video 1]
[Transcripción del Video 1]

## [Título del Video 2]
[Transcripción del Video 2]
```

Si una transcripción no está disponible, se indicará con el mensaje "_Transcripción no disponible._" 