"""
Servicio que obtiene datos filtrados por los hijos del tutor autenticado.
Usado exclusivamente por el endpoint móvil de reportes por voz.
"""
from django.utils import timezone


def obtener_hijos_del_tutor(usuario):
    """
    Retorna los niños vinculados al tutor autenticado.
    """
    from apps.tutores.models import UsuarioTutor
    from apps.ninos.models import TutorNino

    try:
        ut    = UsuarioTutor.objects.get(id_usuario=usuario, activo=True)
        tutor = ut.id_tutor
    except UsuarioTutor.DoesNotExist:
        return [], None

    vinculos = TutorNino.objects.filter(
        id_tutor=tutor, activo=True
    ).select_related('id_nino')

    ninos = [v.id_nino for v in vinculos]
    return ninos, tutor


def reporte_asistencia(ninos, filtros):
    from apps.asistencia.models import Asistencia

    qs = Asistencia.objects.filter(
        id_nino__in=ninos, activo=True
    ).select_related('id_nino').order_by('-fecha')

    desde  = filtros.get('fecha_desde')
    hasta  = filtros.get('fecha_hasta')
    estado = filtros.get('estado')

    if desde:  qs = qs.filter(fecha__gte=desde)
    if hasta:  qs = qs.filter(fecha__lte=hasta)
    if estado: qs = qs.filter(estado=estado)

    return [
        {
            'nino':         r.id_nino.nombre,
            'fecha':        str(r.fecha),
            'estado':       r.estado,
            'hora_ingreso': str(r.hora_ingreso) if r.hora_ingreso else None,
            'hora_salida':  str(r.hora_salida)  if r.hora_salida  else None,
        }
        for r in qs
    ]


def reporte_pagos(ninos, filtros):
    from apps.servicios.models import Pago

    qs = Pago.objects.filter(
        id_nino__in=ninos, activo=True
    ).select_related('id_nino').order_by('-fecha')

    desde  = filtros.get('fecha_desde')
    hasta  = filtros.get('fecha_hasta')
    estado = filtros.get('estado')

    if desde:  qs = qs.filter(fecha__gte=desde)
    if hasta:  qs = qs.filter(fecha__lte=hasta)
    if estado: qs = qs.filter(estado=estado)

    return [
        {
            'nino':   p.id_nino.nombre,
            'fecha':  str(p.fecha),
            'total':  float(p.total),
            'estado': p.estado,
        }
        for p in qs
    ]


def reporte_actividades(ninos, filtros):
    from apps.actividades.models import Actividad

    qs = Actividad.objects.filter(
        id_nino__in=ninos, activo=True
    ).select_related('id_nino').order_by('-fecha')

    desde = filtros.get('fecha_desde')
    hasta = filtros.get('fecha_hasta')
    tipo  = filtros.get('tipo')

    if desde: qs = qs.filter(fecha__gte=desde)
    if hasta: qs = qs.filter(fecha__lte=hasta)
    if tipo:  qs = qs.filter(tipo=tipo)

    return [
        {
            'nino':        a.id_nino.nombre,
            'tipo':        a.get_tipo_display(),
            'descripcion': a.descripcion,
            'fecha':       str(a.fecha),
        }
        for a in qs
    ]


def reporte_salud(ninos, filtros):
    from apps.salud.models import Salud

    qs = Salud.objects.filter(
        id_nino__in=ninos, activo=True
    ).select_related('id_nino').order_by('-fecha')

    desde = filtros.get('fecha_desde')
    hasta = filtros.get('fecha_hasta')

    if desde: qs = qs.filter(fecha__gte=desde)
    if hasta: qs = qs.filter(fecha__lte=hasta)

    return [
        {
            'nino':         s.id_nino.nombre,
            'fecha':        str(s.fecha),
            'sintomas':     s.sintomas,
            'observaciones':s.observaciones,
        }
        for s in qs
    ]


def resumen_general(ninos):
    """
    Resumen rápido de todos los módulos para hoy.
    """
    from apps.asistencia.models import Asistencia
    from apps.servicios.models import Pago
    from apps.actividades.models import Actividad
    from apps.salud.models import Salud

    hoy = timezone.now().date()

    asistencia_hoy = Asistencia.objects.filter(
        id_nino__in=ninos, fecha=hoy, activo=True
    ).select_related('id_nino')

    pagos_pendientes = Pago.objects.filter(
        id_nino__in=ninos, estado='pendiente', activo=True
    ).count()

    actividades_hoy = Actividad.objects.filter(
        id_nino__in=ninos, fecha=hoy, activo=True
    ).count()

    alertas_salud = Salud.objects.filter(
        id_nino__in=ninos, fecha=hoy, activo=True
    ).count()

    return {
        'asistencia_hoy': [
            {
                'nino':         a.id_nino.nombre,
                'estado':       a.estado,
                'hora_ingreso': str(a.hora_ingreso) if a.hora_ingreso else None,
            }
            for a in asistencia_hoy
        ],
        'pagos_pendientes': pagos_pendientes,
        'actividades_hoy':  actividades_hoy,
        'alertas_salud':    alertas_salud,
        'ninos': [n.nombre for n in ninos],
    }


# Mapa de módulo → función de reporte
REPORTES = {
    'asistencia':  reporte_asistencia,
    'pagos':       reporte_pagos,
    'actividades': reporte_actividades,
    'salud':       reporte_salud,
}


def ejecutar_reporte(modulo, ninos, filtros):
    """
    Ejecuta el reporte correspondiente al módulo.
    Si el módulo no existe o es 'resumen', devuelve el resumen general.
    """
    fn = REPORTES.get(modulo)
    if fn:
        return fn(ninos, filtros)
    return resumen_general(ninos)
"""
Servicio que obtiene datos filtrados por los hijos del tutor autenticado.
Usado exclusivamente por el endpoint móvil de reportes por voz.
"""
from django.utils import timezone


def obtener_hijos_del_tutor(usuario):
    """
    Retorna los niños vinculados al tutor autenticado.
    """
    from apps.tutores.models import UsuarioTutor
    from apps.ninos.models import TutorNino

    try:
        ut    = UsuarioTutor.objects.get(id_usuario=usuario, activo=True)
        tutor = ut.id_tutor
    except UsuarioTutor.DoesNotExist:
        return [], None

    vinculos = TutorNino.objects.filter(
        id_tutor=tutor, activo=True
    ).select_related('id_nino')

    ninos = [v.id_nino for v in vinculos]
    return ninos, tutor


def reporte_asistencia(ninos, filtros):
    from apps.asistencia.models import Asistencia

    qs = Asistencia.objects.filter(
        id_nino__in=ninos, activo=True
    ).select_related('id_nino').order_by('-fecha')

    desde  = filtros.get('fecha_desde')
    hasta  = filtros.get('fecha_hasta')
    estado = filtros.get('estado')

    if desde:  qs = qs.filter(fecha__gte=desde)
    if hasta:  qs = qs.filter(fecha__lte=hasta)
    if estado: qs = qs.filter(estado=estado)

    return [
        {
            'nino':         r.id_nino.nombre,
            'fecha':        str(r.fecha),
            'estado':       r.estado,
            'hora_ingreso': str(r.hora_ingreso) if r.hora_ingreso else None,
            'hora_salida':  str(r.hora_salida)  if r.hora_salida  else None,
        }
        for r in qs
    ]


def reporte_pagos(ninos, filtros):
    from apps.servicios.models import Pago

    qs = Pago.objects.filter(
        id_nino__in=ninos, activo=True
    ).select_related('id_nino').order_by('-fecha')

    desde  = filtros.get('fecha_desde')
    hasta  = filtros.get('fecha_hasta')
    estado = filtros.get('estado')

    if desde:  qs = qs.filter(fecha__gte=desde)
    if hasta:  qs = qs.filter(fecha__lte=hasta)
    if estado: qs = qs.filter(estado=estado)

    return [
        {
            'nino':   p.id_nino.nombre,
            'fecha':  str(p.fecha),
            'total':  float(p.total),
            'estado': p.estado,
        }
        for p in qs
    ]


def reporte_actividades(ninos, filtros):
    from apps.actividades.models import Actividad

    qs = Actividad.objects.filter(
        id_nino__in=ninos, activo=True
    ).select_related('id_nino').order_by('-fecha')

    desde = filtros.get('fecha_desde')
    hasta = filtros.get('fecha_hasta')
    tipo  = filtros.get('tipo')

    if desde: qs = qs.filter(fecha__gte=desde)
    if hasta: qs = qs.filter(fecha__lte=hasta)
    if tipo:  qs = qs.filter(tipo=tipo)

    return [
        {
            'nino':        a.id_nino.nombre,
            'tipo':        a.get_tipo_display(),
            'descripcion': a.descripcion,
            'fecha':       str(a.fecha),
        }
        for a in qs
    ]


def reporte_salud(ninos, filtros):
    from apps.salud.models import Salud

    qs = Salud.objects.filter(
        id_nino__in=ninos, activo=True
    ).select_related('id_nino').order_by('-fecha')

    desde = filtros.get('fecha_desde')
    hasta = filtros.get('fecha_hasta')

    if desde: qs = qs.filter(fecha__gte=desde)
    if hasta: qs = qs.filter(fecha__lte=hasta)

    return [
        {
            'nino':         s.id_nino.nombre,
            'fecha':        str(s.fecha),
            'sintomas':     s.sintomas,
            'observaciones':s.observaciones,
        }
        for s in qs
    ]


def resumen_general(ninos):
    """
    Resumen rápido de todos los módulos para hoy.
    """
    from apps.asistencia.models import Asistencia
    from apps.servicios.models import Pago
    from apps.actividades.models import Actividad
    from apps.salud.models import Salud

    hoy = timezone.now().date()

    asistencia_hoy = Asistencia.objects.filter(
        id_nino__in=ninos, fecha=hoy, activo=True
    ).select_related('id_nino')

    pagos_pendientes = Pago.objects.filter(
        id_nino__in=ninos, estado='pendiente', activo=True
    ).count()

    actividades_hoy = Actividad.objects.filter(
        id_nino__in=ninos, fecha=hoy, activo=True
    ).count()

    alertas_salud = Salud.objects.filter(
        id_nino__in=ninos, fecha=hoy, activo=True
    ).count()

    return {
        'asistencia_hoy': [
            {
                'nino':         a.id_nino.nombre,
                'estado':       a.estado,
                'hora_ingreso': str(a.hora_ingreso) if a.hora_ingreso else None,
            }
            for a in asistencia_hoy
        ],
        'pagos_pendientes': pagos_pendientes,
        'actividades_hoy':  actividades_hoy,
        'alertas_salud':    alertas_salud,
        'ninos': [n.nombre for n in ninos],
    }


# Mapa de módulo → función de reporte
REPORTES = {
    'asistencia':  reporte_asistencia,
    'pagos':       reporte_pagos,
    'actividades': reporte_actividades,
    'salud':       reporte_salud,
}


def ejecutar_reporte(modulo, ninos, filtros):
    """
    Ejecuta el reporte correspondiente al módulo.
    Si el módulo no existe o es 'resumen', devuelve el resumen general.
    """
    fn = REPORTES.get(modulo)
    if fn:
        return fn(ninos, filtros)
    return resumen_general(ninos)