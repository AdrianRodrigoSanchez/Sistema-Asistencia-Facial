import datetime
import pyttsx3
import speech_recognition as sr
import face_recognition
import cv2
import json
import os
import numpy as np

# ─────────────────────────────────────────────
# ARCHIVOS DE DATOS
# ─────────────────────────────────────────────

USERS_FILE     = 'users.json'       # Almacena usuarios registrados + encodings faciales
ATTENDANCE_FILE = 'attendance.json' # Almacena los registros de entrada (fichajes)


# ══════════════════════════════════════════════
# BLOQUE 1 – VOZ Y AUDIO
# ══════════════════════════════════════════════

def talk(msg):
  
    newVoiceRate = 180
    engine = pyttsx3.init()

    try:
        # Recorremos todas las voces instaladas en el sistema
        voices = engine.getProperty('voices')
        selected_voice = None

        for v in voices:
            name = (v.name or "").lower()
            # Intentamos leer el idioma de la voz (puede venir como bytes o string)
            langs = ""
            try:
                langs = "".join(
                    [l.decode() if isinstance(l, bytes) else str(l)
                     for l in getattr(v, "languages", [])]
                ).lower()
            except Exception:
                langs = ""

            # Buscamos indicios de español en el nombre o en los idiomas
            if 'spanish' in name or 'es' in langs or 'es_' in langs or 'esp' in name:
                selected_voice = v.id
                break

        if selected_voice:
            engine.setProperty('voice', selected_voice)

    except Exception:
        # Si algo falla con las voces, el sistema usa la voz por defecto sin romperse
        pass

    try:
        engine.setProperty('rate', newVoiceRate)
    except Exception:
        pass

    engine.say(msg)
    engine.runAndWait()


def audio_to_text():
  
    r = sr.Recognizer()

    with sr.Microphone() as origin:
        r.pause_threshold = 0.8   # Tiempo de silencio para considerar que el usuario terminó
        print('Puedes comenzar a hablar')
        audio = r.listen(origin)

        try:
            text = r.recognize_google(audio, language='es-es')
            return text
        except sr.UnknownValueError:
            print('Ups, no te entendí')
            return 'Esperando'
        except sr.RequestError:
            print('Ups, sin servicio')
            return 'Esperando'
        except Exception as e:
            print('Ups, algo ha salido mal:', e)
            return 'Esperando'


# ══════════════════════════════════════════════
# BLOQUE 2 – GESTIÓN DEL JSON DE USUARIOS
# ══════════════════════════════════════════════

def load_users():
  
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                # Si el JSON está mal formado, empezamos con lista vacía
                print('Ups, algo ha salido mal leyendo users.json')
                return []
    return []


def save_user(name, face_encoding_list):
    
    users = load_users()

    entry = {
        "name": name.strip().capitalize(),
        "timestamp": datetime.datetime.now().isoformat(),  # Fecha y hora de registro
        "face_encoding": face_encoding_list                # Lista de 128 floats (serializable en JSON)
    }

    users.append(entry)

    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

    print(f'Usuario "{name}" guardado en {USERS_FILE}')


def save_attendance(name):
  
    # Cargamos los fichajes existentes (o empezamos con lista vacía)
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print('Ups, algo ha salido mal leyendo attendance.json')
                data = []
    else:
        data = []

    entry = {
        "name": name,
        "timestamp": datetime.datetime.now().isoformat()
    }

    data.append(entry)

    with open(ATTENDANCE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f'Asistencia de "{name}" registrada en {ATTENDANCE_FILE}')


# ══════════════════════════════════════════════
# BLOQUE 3 – CÁMARA Y RECONOCIMIENTO FACIAL
# ══════════════════════════════════════════════

def capture_face_encoding():
  
    print('Encendiendo la cámara...')
    cap = cv2.VideoCapture(0)   # 0 = primera cámara disponible (webcam)

    if not cap.isOpened():
        print('Ups, algo ha salido mal: no se pudo abrir la cámara')
        return None

    encoding = None

    try:
        talk('Por favor, mira a la cámara.')

        # Bucle de captura: seguimos leyendo frames hasta obtener un rostro
        while True:
            ret, frame = cap.read()   # ret=True si el frame se leyó bien

            if not ret:
                print('Ups, algo ha salido mal al leer el frame de la cámara')
                break

            # Mostramos la imagen en pantalla para que el usuario vea lo que capta la cámara
            cv2.imshow('Sistema de Asistencia - Pulsa Q para salir', frame)

            # face_recognition trabaja con imágenes en formato RGB (OpenCV usa BGR por defecto)
            # Convertimos el color del frame antes de procesarlo
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Buscamos todos los rostros en el frame y calculamos sus encodings
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            if face_encodings:
                # Tomamos el primer rostro detectado (el más prominente)
                encoding = face_encodings[0]
                print('Rostro detectado correctamente.')
                break   # Ya tenemos el encoding, salimos del bucle

            # Si el usuario pulsa Q, salimos aunque no se haya detectado ningún rostro
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print('Captura cancelada por el usuario')
                break

    except Exception as e:
        print('Ups, algo ha salido mal durante el reconocimiento facial:', e)

    finally:
        # SIEMPRE liberamos la cámara y cerramos las ventanas, pase lo que pase
        cap.release()
        cv2.destroyAllWindows()

    return encoding   # Puede ser None si no se detectó ningún rostro


# ══════════════════════════════════════════════
# BLOQUE 4 – LÓGICA PRINCIPAL DEL SISTEMA
# ══════════════════════════════════════════════

def register_new_user():
    
    talk('No estás registrado en el sistema. Vamos a registrarte.')
    talk('Por favor, di tu nombre.')

    # Capturamos el nombre por voz
    name = audio_to_text()

    if not name or name == 'Esperando':
        talk('No he podido escuchar tu nombre. Inténtalo de nuevo más tarde.')
        return

    talk(f'Perfecto, {name}. Ahora voy a capturar tu rostro.')

    # Capturamos el encoding facial
    encoding = capture_face_encoding()

    if encoding is None:
        talk('No he podido capturar tu rostro. Inténtalo de nuevo más tarde.')
        return

   
    encoding_list = encoding.tolist()

    # Guardamos el usuario en el JSON
    save_user(name, encoding_list)

    talk(f'Genial, {name.capitalize()}. Te has registrado correctamente en el sistema.')


def recognize_user():
    

    users = load_users()

    if not users:
        # Si no hay ningún usuario registrado todavía, vamos directamente al registro
        print('No hay usuarios registrados aún.')
        register_new_user()
        return False

  
    talk('Buenos días. Por favor, mira a la cámara para identificarte.')
    encoding = capture_face_encoding()

    if encoding is None:
        talk('No he podido detectar ningún rostro. Por favor, inténtalo de nuevo.')
        return False

    known_encodings = []
    known_names     = []

    for user in users:
        encoding_data = user.get('face_encoding')
        if encoding_data:
            # Convertimos la lista guardada en JSON a array NumPy
            known_encodings.append(np.array(encoding_data))
            known_names.append(user.get('name', 'Desconocido'))

    if not known_encodings:
        print('No se encontraron encodings válidos en users.json')
        register_new_user()
        return False

    matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.6)

   
    if True in matches:
        # Encontramos al usuario: obtenemos su índice y su nombre
        first_match_index = matches.index(True)
        recognized_name   = known_names[first_match_index]

        # Bienvenida por voz
        hour = datetime.datetime.now()
        if hour.hour < 6 or hour.hour > 20:
            momento = 'Buenas noches'
        elif 6 <= hour.hour < 13:
            momento = 'Buenos días'
        else:
            momento = 'Buenas tardes'

        talk(f'{momento}, {recognized_name}. Bienvenido al sistema. Tu asistencia ha sido registrada.')
        print(f'Usuario reconocido: {recognized_name}')

        # Guardamos el fichaje en attendance.json
        save_attendance(recognized_name)
        return True

    else:
        # Ningún encoding coincidió → usuario desconocido
        register_new_user()
        return False


# ══════════════════════════════════════════════
# BLOQUE 5 – PUNTO DE ENTRADA DEL SISTEMA
# ══════════════════════════════════════════════

def run_attendance_system():
  
    print('=== Sistema de Control de Asistencia con Reconocimiento Facial ===')
    talk('Sistema de control de asistencia iniciado.')

    # Ejecutamos el reconocimiento (o registro si es un usuario nuevo)
    recognize_user()

    talk('Sesión finalizada. Hasta pronto.')
    print('=== Sistema finalizado ===')