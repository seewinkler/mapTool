import json
import os

# 🔧 Konfiguration laden
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, "config.json")

with open(config_path, encoding="utf-8") as f:
    config = json.load(f)

# 🌍 Regionen anzeigen
regionen = list(config["regionen"].keys())
print("Verfügbare Regionen:")
for i, region in enumerate(regionen, start=1):
    print(f"{i}. {region}")

# 🎯 Auswahl
wahl = input("Bitte eine Region wählen (Nummer eingeben): ")
try:
    region_index = int(wahl) - 1
    region_name = regionen[region_index]
    ziel_crs = config["regionen"][region_name][0]  # z. B. EPSG:3035
    print(f"Ausgewählte Region: {region_name}, CRS: {ziel_crs}")

    # 📤 In Datei speichern (optional)
    with open(os.path.join(BASE_DIR, "selected_region.txt"), "w", encoding="utf-8") as f:
        f.write(region_name)
except (ValueError, IndexError):
    print("Ungültige Eingabe.")