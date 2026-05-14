import os
import gzip
import subprocess
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.usuarios.permissions import IsAdmin


def generar_dump():
    """Genera el dump de PostgreSQL y retorna los bytes comprimidos."""
    db = settings.DATABASES["default"]
    env = os.environ.copy()
    env["PGPASSWORD"] = db.get("PASSWORD", "")

    cmd = [
        "pg_dump",
        "-h", db.get("HOST", "localhost"),
        "-p", str(db.get("PORT", "5432")),
        "-U", db.get("USER", "postgres"),
        "-d", db.get("NAME", ""),
        "--no-password",
        "-F", "p",
    ]

    resultado = subprocess.run(cmd, env=env, capture_output=True)

    if resultado.returncode != 0:
        raise Exception(resultado.stderr.decode())

    return gzip.compress(resultado.stdout)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def descargar_backup(request):
    """
    GET /api/v1/backup/descargar/
    Genera el dump y lo devuelve como archivo descargable.
    """
    try:
        contenido = generar_dump()
        nombre = f"backup_guarderia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql.gz"

        response = HttpResponse(contenido, content_type="application/gzip")
        response["Content-Disposition"] = f'attachment; filename="{nombre}"'
        response["Content-Length"] = len(contenido)
        return response

    except Exception as e:
        return Response(
            {"detail": f"Error al generar backup: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def restaurar_backup(request):
    """
    POST /api/v1/backup/restaurar/
    Recibe el archivo .sql.gz y restaura la BD.
    """
    archivo = request.FILES.get("archivo")
    if not archivo:
        return Response(
            {"detail": "Debés subir un archivo .sql.gz"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not archivo.name.endswith((".sql.gz", ".sql")):
        return Response(
            {"detail": "El archivo debe ser .sql.gz o .sql"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        contenido = archivo.read()

        # Descomprimir si es .gz
        if archivo.name.endswith(".gz"):
            contenido_sql = gzip.decompress(contenido)
        else:
            contenido_sql = contenido

        db = settings.DATABASES["default"]
        env = os.environ.copy()
        env["PGPASSWORD"] = db.get("PASSWORD", "")

        cmd = [
            "psql",
            "-h", db.get("HOST", "localhost"),
            "-p", str(db.get("PORT", "5432")),
            "-U", db.get("USER", "postgres"),
            "-d", db.get("NAME", ""),
            "--no-password",
        ]

        resultado = subprocess.run(
            cmd,
            input=contenido_sql,
            env=env,
            capture_output=True,
        )

        if resultado.returncode != 0:
            raise Exception(resultado.stderr.decode())

        return Response({"detail": "Base de datos restaurada correctamente."})

    except Exception as e:
        return Response(
            {"detail": f"Error al restaurar: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )