import requests
import json

# ============================================================
#  CONFIGURACIÓN
# ============================================================
API_KEY = "cccdb4d3-7c18-4d81-97b7-0e7fb9129d61"  

GEOCODE_URL = "https://graphhopper.com/api/1/geocode"
ROUTE_URL   = "https://graphhopper.com/api/1/route"

# Medios de transporte disponibles 
TRANSPORTES = {
    "1": ("car",        "🚗 Auto"),
    "2": ("bike",       "🚲 Bicicleta"),
    "3": ("foot",       "🚶 A pie"),
}


# ─────────────────────────────────────────────
#  Utilidades
# ─────────────────────────────────────────────

def limpiar_pantalla():
    print("\n" + "=" * 60)


def metros_a_km(metros: float) -> float:
    return metros / 1000


def metros_a_millas(metros: float) -> float:
    return metros / 1609.344


def ms_a_tiempo_legible(ms: int) -> str:
    """Convierte milisegundos a formato h m s."""
    segundos = ms // 1000
    horas, resto = divmod(segundos, 3600)
    minutos, segs = divmod(resto, 60)
    partes = []
    if horas:
        partes.append(f"{horas} h")
    if minutos:
        partes.append(f"{minutos} min")
    if segs or not partes:
        partes.append(f"{segs} seg")
    return " ".join(partes)


# ─────────────────────────────────────────────
#  Geocodificación
# ─────────────────────────────────────────────

def geocodificar(ciudad: str) -> tuple[float, float] | None:
    """Devuelve (lat, lon) o None si no se encontró."""
    params = {
        "q": ciudad,
        "limit": 1,
        "locale": "es",
        "key": API_KEY,
    }
    try:
        resp = requests.get(GEOCODE_URL, params=params, timeout=10)
        resp.raise_for_status()
        hits = resp.json().get("hits", [])
        if not hits:
            return None
        punto = hits[0]["point"]
        return punto["lat"], punto["lng"]
    except requests.RequestException as e:
        print(f"  ⚠️  Error de conexión al geocodificar: {e}")
        return None


# ─────────────────────────────────────────────
#  Cálculo de ruta
# ─────────────────────────────────────────────

def calcular_ruta(origen: tuple, destino: tuple, vehiculo: str) -> dict | None:
    """Retorna el JSON de la ruta o None ante error."""
    # Usamos lista de tuplas para enviar dos 'point' sin que requests los sobreescriba
    params = [
        ("point", f"{origen[0]},{origen[1]}"),
        ("point", f"{destino[0]},{destino[1]}"),
        ("vehicle", vehiculo),
        ("locale", "es"),
        ("instructions", "true"),
        ("calc_points", "true"),
        ("key", API_KEY),
    ]
    try:
        resp = requests.get(ROUTE_URL, params=params, timeout=15)
        if not resp.ok:
            # Mostrar detalle del error devuelto por la API
            try:
                detalle = resp.json()
                msg = detalle.get("message", resp.text[:200])
            except Exception:
                msg = resp.text[:200]
            print(f"  ⚠️  Error {resp.status_code} de la API: {msg}")
            return None
        return resp.json()
    except requests.RequestException as e:
        print(f"  ⚠️  Error de conexión: {e}")
        return None


# ─────────────────────────────────────────────
#  Mostrar resultados
# ─────────────────────────────────────────────

def mostrar_resultado(ciudad_origen: str, ciudad_destino: str,
                      datos: dict, nombre_vehiculo: str):
    path = datos["paths"][0]
    distancia_m  = path["distance"]        # metros
    duracion_ms  = path["time"]            # milisegundos
    instrucciones = path.get("instructions", [])

    km      = metros_a_km(distancia_m)
    millas  = metros_a_millas(distancia_m)
    tiempo  = ms_a_tiempo_legible(duracion_ms)

    limpiar_pantalla()
    print(f"  RESULTADO DEL VIAJE")
    print("=" * 60)
    print(f"  Origen    : {ciudad_origen.title()}")
    print(f"  Destino   : {ciudad_destino.title()}")
    print(f"  Transporte: {nombre_vehiculo}")
    print("-" * 60)
    print(f"  📏 Distancia : {km:,.2f} km  |  {millas:,.2f} millas")
    print(f"  ⏱️  Duración  : {tiempo}")
    print("=" * 60)

    if instrucciones:
        print("\n  🗺️  NARRATIVA DEL VIAJE")
        print("-" * 60)
        for i, paso in enumerate(instrucciones, start=1):
            texto    = paso.get("text", "")
            dist_p   = paso.get("distance", 0)
            dur_p    = paso.get("time", 0)
            dist_str = f"{dist_p/1000:,.1f} km" if dist_p >= 1000 else f"{int(dist_p)} m"
            dur_str  = ms_a_tiempo_legible(dur_p) if dur_p else ""
            linea    = f"  {i:>3}. {texto}"
            if dist_str:
                linea += f"  [{dist_str}"
                if dur_str:
                    linea += f" · {dur_str}"
                linea += "]"
            print(linea)
    else:
        print("\n  (No hay instrucciones detalladas para este medio de transporte.)")

    print("=" * 60)


# ─────────────────────────────────────────────
#  Menú de transporte
# ─────────────────────────────────────────────

def seleccionar_transporte() -> tuple[str, str] | None:
    """Retorna (vehicle_code, nombre_legible) o None si el usuario quiere salir."""
    print("\n  Elige el medio de transporte:")
    print("  " + "-" * 30)
    for clave, (_, nombre) in TRANSPORTES.items():
        print(f"    {clave}. {nombre}")
    print("    v. Salir")
    print("  " + "-" * 30)

    while True:
        opcion = input("  Opción: ").strip().lower()
        if opcion == "v":
            return None
        if opcion in TRANSPORTES:
            return TRANSPORTES[opcion]   # (vehicle_code, nombre)
        print("  ⚠️  Opción inválida. Intenta de nuevo.")


# ─────────────────────────────────────────────
#  Bucle principal
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("   🌎  CALCULADORA DE RUTAS — GraphHopper")
    print("   Ciudades de Chile y Argentina")
    print("=" * 60)
    print("   (Escribe 'v' en cualquier momento para salir)\n")

    while True:
        # ── Ciudad de Origen ──
        ciudad_origen = input("  Ciudad de Origen  : ").strip()
        if ciudad_origen.lower() == "v":
            break

        # ── Ciudad de Destino ──
        ciudad_destino = input("  Ciudad de Destino : ").strip()
        if ciudad_destino.lower() == "v":
            break

        # ── Medio de transporte ──
        resultado_transp = seleccionar_transporte()
        if resultado_transp is None:
            break
        vehicle_code, nombre_vehiculo = resultado_transp

        # ── Geocodificación ──
        print(f"\n  🔍 Buscando coordenadas de '{ciudad_origen}'...")
        coords_origen = geocodificar(ciudad_origen)
        if not coords_origen:
            print(f"  ❌ No se encontró '{ciudad_origen}'. Verifica el nombre.")
            input("\n  Presiona Enter para continuar...")
            continue

        print(f"  🔍 Buscando coordenadas de '{ciudad_destino}'...")
        coords_destino = geocodificar(ciudad_destino)
        if not coords_destino:
            print(f"  ❌ No se encontró '{ciudad_destino}'. Verifica el nombre.")
            input("\n  Presiona Enter para continuar...")
            continue

        # ── Cálculo de ruta ──
        print("  ⚙️  Calculando ruta, por favor espera...")
        datos = calcular_ruta(coords_origen, coords_destino, vehicle_code)
        if not datos or "paths" not in datos:
            msg = datos.get("message", "Respuesta inesperada.") if datos else "Sin respuesta."
            print(f"  ❌ No se pudo calcular la ruta: {msg}")
            input("\n  Presiona Enter para continuar...")
            continue

        # ── Mostrar resultados ──
        mostrar_resultado(ciudad_origen, ciudad_destino, datos, nombre_vehiculo)

        # ── Nueva consulta o salir ──
        print("\n  ¿Qué deseas hacer?")
        print("    1. Calcular otra ruta")
        print("    v. Salir")
        opcion = input("  Opción: ").strip().lower()
        if opcion == "v":
            break
        print()

    print("\n  👋 ¡Hasta pronto!\n")


if __name__ == "__main__":
    main()
