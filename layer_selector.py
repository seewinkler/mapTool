import fiona

def get_layers_interactive(gpkg_path):
    """Interaktive Null-basierte Auswahl von Layern aus einer GPKG-Datei."""
    available_layers = fiona.listlayers(gpkg_path)

    print("\n📚 Verfügbare Layer im Hauptland-GPKG:")
    for i, layer in enumerate(available_layers):  # beginnt bei 0
        print(f"{i}. {layer}")

    auswahl = input("\n🔢 Gib die Nummern der gewünschten Layer ein (z. B. 0,2,3) – oder leer für alle: ").strip()
    
    try:
        if auswahl == "":
            selected_layers = list(available_layers)
        else:
            indices = sorted(set(int(i.strip()) for i in auswahl.split(",")))
            selected_layers = []
            for i in indices:
                if 0 <= i < len(available_layers):
                    selected_layers.append(available_layers[i])
                else:
                    print(f"⚠️ Index {i} ist ungültig und wurde ignoriert.")

        print(f"\n✅ Gewählte Layer: {selected_layers}")
        return selected_layers
    except Exception as e:
        raise ValueError(f"Ungültige Eingabe bei Layer-Auswahl. Details: {e}")

def get_layers_from_config(config):
    """Layer aus der Konfiguration laden."""
    return config.get("hauptland", [])