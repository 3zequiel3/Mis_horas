def horas_a_formato(horas_decimal):
    """Convierte horas decimales a formato HH:MM"""
    if not horas_decimal:
        return "00:00"
    
    horas_enteras = int(horas_decimal)
    minutos = int((horas_decimal - horas_enteras) * 60)
    return f"{horas_enteras:02d}:{minutos:02d}"

def formato_a_horas(formato_str):
    """Convierte formato HH:MM a horas decimales"""
    try:
        if ":" in formato_str:
            horas, minutos = map(int, formato_str.split(":"))
            return horas + (minutos / 60)
        else:
            return float(formato_str)
    except:
        return 0.0