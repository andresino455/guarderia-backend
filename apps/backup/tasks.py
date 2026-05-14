def backup_automatico():
    """Tarea cron que se ejecuta a las 3am."""
    from .backup_service import hacer_backup
    try:
        file_info = hacer_backup()
        print(f"[BACKUP] Backup automático exitoso: {file_info.get('name')}")
    except Exception as e:
        print(f"[BACKUP] Error en backup automático: {e}")