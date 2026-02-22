#!/usr/bin/env python3
"""
Upload des architectes vers Monday.com - Version Simplifiée
Crée les items d'abord, met à jour les colonnes ensuite
"""

import json
import urllib.request
import time

# Configuration
TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjU3OTU3Mzk0NywiYWFpIjoxMSwidWlkIjo3NjcxNzM4MSwiaWFkIjoiMjAyNS0xMC0yOFQxNDoyMDowNS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTM2OTM2MDMsInJnbiI6InVzZTEifQ.Z6ReAb-nbI60DB6id48CcnOg5WEEAuRyv7MmefV2LVE"
BOARD_ID = "18401049115"
GROUP_ID = "topics"

def graphql_query(query):
    """Exécute une requête GraphQL"""
    req = urllib.request.Request(
        "https://api.monday.com/v2",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": TOKEN, "Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except Exception as e:
        return {"error": str(e)}

def create_simple_item(nom):
    """Crée un item avec juste le nom"""
    query = f'mutation {{ create_item(board_id: {BOARD_ID}, group_id: "{GROUP_ID}", item_name: "{nom}") {{ id }} }}'
    return graphql_query(query)

def update_column_text(item_id, column_id, value):
    """Met à jour une colonne texte"""
    value_json = json.dumps(value).replace('"', '\\"')
    query = f'mutation {{ change_column_value(board_id: {BOARD_ID}, item_id: {item_id}, column_id: "{column_id}", value: "{value_json}") {{ id }} }}'
    return graphql_query(query)

def update_column_phone(item_id, phone):
    """Met à jour la colonne téléphone"""
    # Nettoyer le téléphone
    tel_clean = phone.replace(' ', '').replace('.', '').replace('-', '')
    if tel_clean.startswith('0') and len(tel_clean) == 10:
        tel_clean = '+33' + tel_clean[1:]
    
    value = json.dumps({"phone": tel_clean, "countryShortName": "FR"})
    query = f'mutation {{ change_column_value(board_id: {BOARD_ID}, item_id: {item_id}, column_id: "phone_mm0sg5cn", value: "{value}") {{ id }} }}'
    return graphql_query(query)

def update_column_link(item_id, url):
    """Met à jour la colonne lien"""
    if not url.startswith('http'):
        url = 'https://' + url
    value = json.dumps({"url": url, "text": "Site web"})
    query = f'mutation {{ change_column_value(board_id: {BOARD_ID}, item_id: {item_id}, column_id: "link_mm0sn03m", value: "{value}") {{ id }} }}'
    return graphql_query(query)

def update_column_location(item_id, address, lat, lng):
    """Met à jour la colonne location"""
    value = json.dumps({"address": address, "lat": str(lat), "lng": str(lng)})
    query = f'mutation {{ change_column_value(board_id: {BOARD_ID}, item_id: {item_id}, column_id: "location_mm0snkad", value: "{value}") {{ id }} }}'
    return graphql_query(query)

def update_column_rating(item_id, rating):
    """Met à jour la colonne rating"""
    value = json.dumps({"rating": float(rating)})
    query = f'mutation {{ change_column_value(board_id: {BOARD_ID}, item_id: {item_id}, column_id: "rating_mm0st2s2", value: "{value}") {{ id }} }}'
    return graphql_query(query)

def update_column_number(item_id, number):
    """Met à jour la colonne nombre"""
    value = json.dumps(number)
    query = f'mutation {{ change_column_value(board_id: {BOARD_ID}, item_id: {item_id}, column_id: "numeric_mm0sddnt", value: "{value}") {{ id }} }}'
    return graphql_query(query)

def update_column_dropdown(item_id, label):
    """Met à jour la colonne dropdown"""
    value = json.dumps({"labels": [label.upper()]})
    query = f'mutation {{ change_column_value(board_id: {BOARD_ID}, item_id: {item_id}, column_id: "dropdown_mm0s7qkj", value: "{value}") {{ id }} }}'
    return graphql_query(query)

def update_column_status(item_id, label):
    """Met à jour la colonne statut"""
    value = json.dumps({"label": label})
    query = f'mutation {{ change_column_value(board_id: {BOARD_ID}, item_id: {item_id}, column_id: "color_mm0sy53r", value: "{value}") {{ id }} }}'
    return graphql_query(query)

def process_architecte(arch):
    """Traite un architecte complet"""
    nom = arch.get('nom', 'Sans nom')[:100].replace('"', '\\"')
    
    # Étape 1: Créer l'item
    result = create_simple_item(nom)
    if 'error' in result or not result.get('data', {}).get('create_item'):
        return None, f"Erreur création: {result}"
    
    item_id = result['data']['create_item']['id']
    
    # Étape 2: Mettre à jour les colonnes
    errors = []
    
    # Téléphone
    if arch.get('telephone'):
        r = update_column_phone(item_id, arch['telephone'])
        if 'error' in r:
            errors.append(f"tel: {r['error']}")
        time.sleep(0.1)
    
    # Site web
    if arch.get('site_web'):
        r = update_column_link(item_id, arch['site_web'])
        if 'error' in r:
            errors.append(f"link: {r['error']}")
        time.sleep(0.1)
    
    # Adresse
    if arch.get('adresse'):
        r = update_column_location(item_id, arch['adresse'], arch.get('latitude'), arch.get('longitude'))
        if 'error' in r:
            errors.append(f"loc: {r['error']}")
        time.sleep(0.1)
    
    # Note
    if arch.get('note'):
        r = update_column_rating(item_id, arch['note'])
        if 'error' in r:
            errors.append(f"rating: {r['error']}")
        time.sleep(0.1)
    
    # Nombre d'avis
    if arch.get('nb_avis'):
        r = update_column_number(item_id, arch['nb_avis'])
        if 'error' in r:
            errors.append(f"num: {r['error']}")
        time.sleep(0.1)
    
    # Région
    if arch.get('region_source'):
        r = update_column_dropdown(item_id, arch['region_source'])
        if 'error' in r:
            errors.append(f"drop: {r['error']}")
        time.sleep(0.1)
    
    # Statut
    r = update_column_status(item_id, "À contacter")
    if 'error' in r:
        errors.append(f"status: {r['error']}")
    
    return item_id, errors if errors else "OK"

def main():
    """Upload tous les architectes"""
    
    with open("/root/.openclaw/workspace/architectes_france_complet.json", 'r') as f:
        data = json.load(f)
    
    architectes = data.get('architectes', [])
    total = len(architectes)
    
    print("=" * 80)
    print("🏗️ UPLOAD ARCHITECTES → MONDAY.COM (Version Simplifiée)")
    print("=" * 80)
    print(f"📊 Total: {total} architectes")
    print(f"⏱️  Estimation: ~{total * 1.5 / 60:.0f} minutes")
    print("=" * 80)
    
    success = 0
    errors = 0
    
    for i, arch in enumerate(architectes, 1):
        nom_court = arch.get('nom', 'N/A')[:40]
        print(f"[{i:4d}/{total}] {nom_court:45}", end=' ', flush=True)
        
        item_id, status = process_architecte(arch)
        
        if item_id:
            print(f"✅ ID:{item_id}")
            success += 1
        else:
            print(f"❌ {status[:40]}")
            errors += 1
        
        # Rapport tous les 50
        if i % 50 == 0:
            print(f"\n📊 Progression: {i}/{total} | ✅ {success} | ❌ {errors}")
            print("-" * 80)
        
        time.sleep(0.2)
    
    print("\n" + "=" * 80)
    print("🎉 TERMINÉ!")
    print(f"✅ Succès: {success}")
    print(f"❌ Erreurs: {errors}")
    print(f"📈 Taux: {success/total*100:.1f}%")

if __name__ == "__main__":
    main()
