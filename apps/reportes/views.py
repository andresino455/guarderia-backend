from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def procesar_voz(request):
    """
    POST /api/v1/reportes/voz/
    Recibe un archivo de audio, lo transcribe con Whisper (Groq)
    y devuelve los parámetros del reporte interpretados por LLaMA.

    Form-data:
        audio: archivo .webm / .wav / .mp3

    Respuesta:
    {
        "modulo": "asistencia",
        "filtros": { "fecha_desde": "2026-06-01", "fecha_hasta": "2026-06-21" },
        "columnas": null,
        "exportar": null,
        "texto_original": "mostrar asistencia de este mes",
        "descripcion": "Reporte de asistencia del mes actual"
    }
    """
    archivo = request.FILES.get('audio')

    if not archivo:
        return Response(
            {'detail': 'No se recibió ningún archivo de audio.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validar tipo de archivo
    tipos_validos = ['audio/webm', 'audio/wav', 'audio/mpeg', 'audio/mp4', 'audio/ogg']
    if archivo.content_type not in tipos_validos:
        # Algunos browsers mandan tipos raros, ser permisivos
        if not archivo.name.endswith(('.webm', '.wav', '.mp3', '.mp4', '.ogg', '.m4a')):
            return Response(
                {'detail': f'Formato de audio no soportado: {archivo.content_type}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    try:
        from .groq_service import procesar_comando_voz
        resultado = procesar_comando_voz(archivo)
        return Response(resultado, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'detail': f'Error al procesar el audio: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )