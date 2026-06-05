# Sistema de Control de Asistencia con Reconocimiento Facial

Sistema inteligente de control de asistencia que combina **reconocimiento facial**, **asistente de voz** y **gestión de datos en tiempo real**, desarrollado en Python.

## Descripción

El sistema identifica automáticamente a los usuarios mediante reconocimiento facial. Si el usuario no está registrado, el sistema lo registra capturando su rostro y su nombre por voz. Cada acceso queda registrado con fecha y hora en un archivo JSON.

## Funcionalidades

- Asistente de voz en español (texto a voz y reconocimiento de voz)
- Detección y reconocimiento facial en tiempo real
- Registro automático de nuevos usuarios
- Almacenamiento de fichajes con fecha y hora
- Tolerancia configurable para el reconocimiento facial

## Tecnologías utilizadas

- **Python 3**
- **face_recognition** — Reconocimiento facial
- **OpenCV (cv2)** — Captura de vídeo en tiempo real
- **pyttsx3** — Síntesis de voz
- **SpeechRecognition** — Reconocimiento de voz
- **NumPy** — Procesamiento de encodings faciales
- **JSON** — Almacenamiento de usuarios y registros

## Estructura del proyecto

```
├── main.py              # Punto de entrada del sistema
├── asistente_voz.py     # Lógica principal del sistema
├── users.json           # Base de datos de usuarios (generado automáticamente)
└── attendance.json      # Registro de fichajes (generado automáticamente)
```

## Instalación y uso

1. Instala las dependencias:

```bash
pip install face_recognition opencv-python pyttsx3 SpeechRecognition numpy
```

2. Ejecuta el sistema:

```bash
python main.py
```

## Autor

**Adrián Rodrigo Sánchez**  
[LinkedIn](https://linkedin.com/in/adrian-rodrigo-sanchez)

---
*Proyecto desarrollado durante el Curso de Especialización en Inteligencia Artificial y Big Data — IES Virgen de Gracia, Puertollano*
