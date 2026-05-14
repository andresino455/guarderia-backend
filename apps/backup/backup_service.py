import os
import subprocess
import gzip
from datetime import datetime
from django.conf import settings
from .drive_service import subir_backup

def generar_nombre_archivo():
    ahora = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"backup_guarderia_{ahora}.sql.gz"

def hacer_backup():
    """
    Genera un dump de PostgreSQL comprimido y lo sube a Google Drive.
    Retorna la info del archivo subido.
    """
    db = settings.DATABASES["default"]

    env = os.environ.copy()
    env["PGPASSWORD"] = db.get("PASSWORD", "")

    # Comando pg_dump
    cmd = [
        "pg_dump",
        "-h", db.get("HOST", "localhost"),
        "-p", str(db.get("PORT", "5432")),
        "-U", db.get("USER", "postgres"),
        "-d", db.get("NAME", ""),
        "--no-password",
        "-F", "p",  # formato plain SQL
    ]

    resultado = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
    )

    if resultado.returncode != 0:
        raise Exception(f"Error en pg_dump: {resultado.stderr.decode()}")

    # Comprimir con gzip
    contenido_comprimido = gzip.compress(resultado.stdout)
    nombre = generar_nombre_archivo()

    # Subir a Drive
    file_info = subir_backup(contenido_comprimido, nombre)
    return file_info

def restaurar_backup(file_id):
    """
    Descarga un backup de Drive y lo restaura en la BD.
    """
    from .drive_service import descargar_backup

    contenido_comprimido = descargar_backup(file_id)
    contenido_sql = gzip.decompress(contenido_comprimido)

    db = settings.DATABASES["default"]
    env = os.environ.copy()
    env["PGPASSWORD"] = db.get("PASSWORD", "")

    # Primero terminar conexiones activas
    cmd_terminar = [
        "psql",
        "-h", db.get("HOST", "localhost"),
        "-p", str(db.get("PORT", "5432")),
        "-U", db.get("USER", "postgres"),
        "-d", "postgres",
        "--no-password",
        "-c",
        f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{db.get('NAME')}' AND pid <> pg_backend_pid();",
    ]
    subprocess.run(cmd_terminar, env=env, capture_output=True)

    # Restaurar
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
        raise Exception(f"Error restaurando: {resultado.stderr.decode()}")

    return True