import fiona

def get_layers_interactive(gpkg_path):
    """Interaktive Auswahl von Layern aus einer GPKG-Datei."""
    available_layers = fiona.listlayers(gpkg_path)
    print("\n📚 Verfügbare Layer im Hauptland-GPKG:")
    for i, layer in enumerate(available_layers, 1):
        print(f"{i}. {layer}")

    auswahl = input("\n🔢 Gib die Nummern der gewünschten Layer ein (z. B. 1,3,2): ")
    try:
        indices = [int(i.strip()) - 1 for i in auswahl.split(",")]
        selected_layers = [available_layers[i] for i in indices if 0 <= i < len(available_layers)]
        print(f"✅ Gewählte Layer: {selected_layers}")
        return selected_layers
    except Exception:
        raise ValueError("Ungültige Eingabe bei Layer-Auswahl.")

def get_layers_from_config(config):
    """Layer aus der Konfiguration laden."""
    return config.get("hauptland", [])
