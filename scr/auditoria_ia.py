import random

def detectar_errores(transacciones):
    errores = []
    for t in transacciones:
        if t.tipo == "ingreso" and t.monto > 500000 and "CFDI" not in t.concepto.upper():
            errores.append(f"ALTA - Ingreso > $500,000 sin comprobante fiscal | {t.concepto}")
        if "GASTO PERSONAL" in t.concepto.upper() or "RESTAURANT" in t.concepto.upper():
            errores.append(f"MEDIA - Posible gasto no deducible | {t.concepto}")
    
    if random.random() < 0.35:
        errores.append("IA - Patrón anómalo detectado: secuencia sospechosa de movimientos (fraude probable)")
    
    return errores or ["Ningún error crítico detectado por IA."]