def horas_a_formato(horas: float) -> str:
    """Convierte horas decimales a formato HH:MM"""
    if horas is None:
        return "00:00"
    
    horas_enteras = int(horas)
    minutos = int((horas - horas_enteras) * 60)
    return f"{horas_enteras:02d}:{minutos:02d}"

def formato_a_horas(formato: str) -> float:
    """Convierte formato HH:MM a horas decimales"""
    if not formato or formato.strip() == "":
        return 0.0
    
    try:
        formato = formato.strip()
        
        if ":" not in formato:
            return float(formato)
        
        partes = formato.split(":")
        horas = int(partes[0])
        minutos = int(partes[1]) if len(partes) > 1 else 0
        
        return horas + (minutos / 60.0)
    except (ValueError, IndexError):
        return 0.0
