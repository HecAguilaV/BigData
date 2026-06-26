import os, sys, json, time, argparse, logging, random
from datetime import datetime
from google.cloud import pubsub_v1

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SUCURSALES = [
    {"id": 1, "nombre": "Arica",        "zona": "Norte",   "region": "XV - Arica y Parinacota",   "lat": -18.4783, "lng": -70.3126, "capacidad": 80},
    {"id": 2, "nombre": "Iquique",       "zona": "Norte",   "region": "I - Tarapacá",               "lat": -20.2307, "lng": -70.1389, "capacidad": 90},
    {"id": 3, "nombre": "Antofagasta",   "zona": "Norte",   "region": "II - Antofagasta",           "lat": -23.6509, "lng": -70.3955, "capacidad": 160},
    {"id": 4, "nombre": "Copiapó",       "zona": "Norte",   "region": "III - Atacama",              "lat": -27.3668, "lng": -70.3314, "capacidad": 70},
    {"id": 5, "nombre": "La Serena",     "zona": "Norte",   "region": "IV - Coquimbo",              "lat": -29.9027, "lng": -71.2520, "capacidad": 110},
    {"id": 6, "nombre": "Valparaíso",    "zona": "Centro",  "region": "V - Valparaíso",             "lat": -33.0472, "lng": -71.6127, "capacidad": 120},
    {"id": 7, "nombre": "Viña del Mar",  "zona": "Centro",  "region": "V - Valparaíso",             "lat": -32.9997, "lng": -71.5510, "capacidad": 180},
    {"id": 8, "nombre": "Santiago Centro","zona":"Centro",  "region": "RM - Metropolitana",         "lat": -33.4489, "lng": -70.6693, "capacidad": 200},
    {"id": 9, "nombre": "Providencia",   "zona": "Centro",  "region": "RM - Metropolitana",         "lat": -33.4255, "lng": -70.6120, "capacidad": 150},
    {"id": 10,"nombre": "Las Condes",    "zona": "Centro",  "region": "RM - Metropolitana",         "lat": -33.4082, "lng": -70.5667, "capacidad": 250},
    {"id": 11,"nombre": "Rancagua",      "zona": "Centro",  "region": "VI - O'Higgins",             "lat": -34.1709, "lng": -70.7425, "capacidad": 100},
    {"id": 12,"nombre": "Talca",         "zona": "Centro",  "region": "VII - Maule",                "lat": -35.4264, "lng": -71.6554, "capacidad": 95},
    {"id": 13,"nombre": "Curicó",        "zona": "Centro",  "region": "VII - Maule",                "lat": -34.9828, "lng": -71.2394, "capacidad": 80},
    {"id": 14,"nombre": "Chillán",       "zona": "Sur",     "region": "XVI - Ñuble",                "lat": -36.6066, "lng": -72.1033, "capacidad": 85},
    {"id": 15,"nombre": "Concepción",    "zona": "Sur",     "region": "VIII - Biobío",              "lat": -36.8270, "lng": -73.0497, "capacidad": 190},
    {"id": 16,"nombre": "Los Ángeles",   "zona": "Sur",     "region": "VIII - Biobío",              "lat": -37.4695, "lng": -72.3555, "capacidad": 70},
    {"id": 17,"nombre": "Temuco",        "zona": "Sur",     "region": "IX - La Araucanía",          "lat": -38.7396, "lng": -72.5901, "capacidad": 140},
    {"id": 18,"nombre": "Valdivia",      "zona": "Sur",     "region": "XIV - Los Ríos",             "lat": -39.8142, "lng": -73.2459, "capacidad": 85},
    {"id": 19,"nombre": "Osorno",        "zona": "Sur",     "region": "X - Los Lagos",              "lat": -40.5741, "lng": -73.1354, "capacidad": 75},
    {"id": 20,"nombre": "Puerto Montt",  "zona": "Sur",     "region": "X - Los Lagos",              "lat": -41.4712, "lng": -72.9396, "capacidad": 110},
    {"id": 21,"nombre": "Castro",        "zona": "Sur",     "region": "X - Los Lagos",              "lat": -42.4804, "lng": -73.7631, "capacidad": 60},
    {"id": 22,"nombre": "Coyhaique",     "zona": "Austral", "region": "XI - Aysén",                 "lat": -45.5712, "lng": -72.0685, "capacidad": 50},
    {"id": 23,"nombre": "Punta Arenas",  "zona": "Austral", "region": "XII - Magallanes",           "lat": -53.1638, "lng": -70.9171, "capacidad": 65},
    {"id": 24,"nombre": "Calama",        "zona": "Norte",   "region": "II - Antofagasta",           "lat": -22.4626, "lng": -68.9263, "capacidad": 100},
    {"id": 25,"nombre": "San Antonio",   "zona": "Centro",  "region": "V - Valparaíso",             "lat": -33.5940, "lng": -71.6124, "capacidad": 70},
    {"id": 26,"nombre": "Quilpué",       "zona": "Centro",  "region": "V - Valparaíso",             "lat": -33.0500, "lng": -71.4494, "capacidad": 75},
    {"id": 27,"nombre": "San Bernardo",  "zona": "Centro",  "region": "RM - Metropolitana",         "lat": -33.6000, "lng": -70.7000, "capacidad": 90},
    {"id": 28,"nombre": "Maipú",         "zona": "Centro",  "region": "RM - Metropolitana",         "lat": -33.5117, "lng": -70.7607, "capacidad": 130},
    {"id": 29,"nombre": "La Florida",    "zona": "Centro",  "region": "RM - Metropolitana",         "lat": -33.5333, "lng": -70.5833, "capacidad": 120},
    {"id": 30,"nombre": "Puerto Varas",  "zona": "Sur",     "region": "X - Los Lagos",              "lat": -41.3191, "lng": -72.9890, "capacidad": 65},
]

def simulate_aforo(base_count=40):
    events = []
    for s in SUCURSALES:
        hora = datetime.now().hour
        factor_hora = 1.0
        if 10 <= hora <= 12: factor_hora = 2.0
        elif 17 <= hora <= 20: factor_hora = 2.5
        elif 0 <= hora <= 8: factor_hora = 0.1
        dia = datetime.now().weekday()
        factor_dia = 1.5 if dia >= 5 else 1.0
        if s["zona"] == "Norte": factor_zona = random.uniform(0.9, 1.1)
        elif s["zona"] == "Centro": factor_zona = random.uniform(1.0, 1.2)
        elif s["zona"] == "Sur": factor_zona = random.uniform(0.8, 1.0)
        else: factor_zona = random.uniform(0.5, 0.8)
        current = max(0, int(base_count * factor_hora * factor_dia * factor_zona * random.uniform(0.8, 1.2)))
        entra = random.randint(0, max(1, int(current * 0.15)))
        sale = random.randint(0, max(1, int(current * 0.12)))
        nuevo_aforo = max(0, current + entra - sale)
        events.append({
            "timestamp": datetime.now().isoformat(),
            "id_sucursal": s["id"],
            "nombre_sucursal": s["nombre"],
            "zona": s["zona"],
            "region": s["region"],
            "lat": s["lat"],
            "lng": s["lng"],
            "capacidad_maxima": s["capacidad"],
            "aforo_actual": min(nuevo_aforo, s["capacidad"]),
            "personas_entran": entra,
            "personas_salen": sale,
            "porcentaje_ocupacion": round(min(nuevo_aforo, s["capacidad"]) / s["capacidad"] * 100, 1),
        })
    return events

def publish(project_id, topic_id, delay=5):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    logging.info(f"Publicando {len(SUCURSALES)} sucursales en {topic_path} cada {delay}s")
    while True:
        events = simulate_aforo()
        for ev in events:
            data = json.dumps(ev, ensure_ascii=False).encode("utf-8")
            publisher.publish(topic_path, data)
        logging.info(f"Publicados {len(events)} eventos de aforo")
        time.sleep(delay)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", default="cordillerabi")
    parser.add_argument("--topic_id", default="aforo-topic")
    parser.add_argument("--delay", type=float, default=5)
    args = parser.parse_args()
    publish(args.project_id, args.topic_id, args.delay)
