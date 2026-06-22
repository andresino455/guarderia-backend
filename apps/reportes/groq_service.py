import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def transcribir_audio(archivo_audio):
    """
    Recibe un archivo de audio y lo transcribe con Whisper via Groq.
    archivo_audio: objeto tipo file (InMemoryUploadedFile de Django)
    Retorna el texto transcripto.
    """
    transcripcion = client.audio.transcriptions.create(
        model="whisper-large-v3",
        file=(archivo_audio.name, archivo_audio.read(), archivo_audio.content_type),
        language="es",
        response_format="text",
    )
    return transcripcion


def interpretar_comando(texto):
    """
    Recibe el texto transcripto y usa LLaMA para extraer
    los parámetros del reporte en formato JSON.

    Retorna un dict con:
    {
        "modulo": "asistencia" | "ninos" | "salud" | "pagos" | "actividades",
        "filtros": {
            "fecha_desde": "YYYY-MM-DD" | null,
            "fecha_hasta": "YYYY-MM-DD" | null,
            "estado": "..." | null,
            "tipo": "..." | null,
        },
        "columnas": [...] | null,
        "exportar": "pdf" | "excel" | null,
        "texto_original": "...",
        "descripcion": "Descripción legible de lo que se va a generar"
    }
    """
    from datetime import date
    hoy = date.today().isoformat()

    prompt_sistema = f"""
Sos un asistente para un sistema de guardería infantil.
Tu tarea es interpretar comandos de voz y convertirlos en parámetros de reporte en JSON.

HOY ES: {hoy}

MÓDULOS DISPONIBLES:
- asistencia: registros de entrada/salida de niños
- ninos: listado de niños registrados
- salud: registros de salud y síntomas
- pagos: pagos y cobros
- actividades: actividades pedagógicas y recreativas

ESTADOS VÁLIDOS:
- asistencia: presente, ausente, tardanza
- pagos: pendiente, pagado, anulado

TIPOS VÁLIDOS:
- actividades: pedagogica, recreativa, deportiva, artistica, social, otro

COLUMNAS POR MÓDULO:
- asistencia: nino_nombre, fecha, estado, hora_ingreso, hora_salida
- ninos: nombre, fecha_nacimiento, edad, info_medica, activo
- salud: nino_nombre, fecha, sintomas, observaciones
- pagos: nino_nombre, fecha, total, estado, cantidad_items
- actividades: nino_nombre, tipo_display, descripcion, fecha

REGLAS:
- "hoy" = {hoy}
- "esta semana" = desde el lunes de esta semana hasta hoy
- "este mes" = desde el 1 del mes actual hasta hoy
- "ayer" = un día antes de hoy
- Si no se especifica módulo, intentá deducirlo del contexto
- Si no se especifica fecha, dejar null
- Si dice "exportar a PDF" o "en PDF", exportar = "pdf"
- Si dice "exportar a Excel" o "en Excel", exportar = "excel"
- Si no menciona exportar, exportar = null
- columnas: si no especifica, devolver null (se usarán todas)

RESPONDÉ SOLO CON JSON VÁLIDO, sin explicaciones ni markdown.
""".strip()

    respuesta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user",   "content": f"Comando: {texto}"},
        ],
        temperature=0.1,
        max_tokens=500,
        response_format={"type": "json_object"},
    )

    contenido = respuesta.choices[0].message.content

    try:
        resultado = json.loads(contenido)
    except json.JSONDecodeError:
        resultado = {
            "modulo":      "asistencia",
            "filtros":     {},
            "columnas":    None,
            "exportar":    None,
            "descripcion": "No se pudo interpretar el comando.",
        }

    resultado["texto_original"] = texto
    return resultado


def procesar_comando_voz(archivo_audio):
    """
    Pipeline completo: audio → texto → parámetros de reporte.
    """
    texto     = transcribir_audio(archivo_audio)
    parametros = interpretar_comando(texto)
    return parametros