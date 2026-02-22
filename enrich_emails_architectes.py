#!/usr/bin/env python3
"""
Script d'enrichissement emails pour les architectes
Scrape les sites web pour trouver les emails de contact
"""

import json
import re
import urllib.request
import urllib.error
import ssl
import time
from urllib.parse import urlparse

# Configuration
INPUT_FILE = "/root/.openclaw/workspace/architectes_france_complet.json"
OUTPUT_FILE = "/root/.openclaw/workspace/architectes_france_avec_emails.json"
BATCH_SIZE = 50  # Nombre de sites à scraper par batch

def create_ssl_context():
    """Crée un contexte SSL qui accepte les certificats auto-signés"""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

def extract_emails_from_html(html, domain):
    """Extrait les emails du HTML"""
    emails = set()
    
    # Pattern email standard
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    found = re.findall(email_pattern, html)
    
    for email in found:
        # Filtrer les emails valides
        if is_valid_email(email, domain):
            emails.add(email.lower())
    
    return list(emails)

def is_valid_email(email, domain):
    """Vérifie si l'email est valide et pertinent"""
    # Exclure les patterns non pertinents
    excluded = [
        'example.com', 'test.com', 'domain.com', 'email.com',
        'yourname', 'your-email', 'nom@', 'prenom@', 'contact@template',
        'admin@localhost', 'user@domain', 'info@example'
    ]
    
    for ex in excluded:
        if ex in email.lower():
            return False
    
    # Doit contenir un @ et un point après
    if '@' not in email or '.' not in email.split('@')[1]:
        return False
    
    return True

def scrape_website(url):
    """Scrape un site web pour trouver les emails"""
    if not url or url == '':
        return []
    
    # Normaliser l'URL
    if not url.startswith('http'):
        url = 'https://' + url
    
    try:
        context = create_ssl_context()
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(req, context=context, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            domain = urlparse(url).netloc
            return extract_emails_from_html(html, domain)
    
    except Exception as e:
        return []

def enrich_architectes():
    """Enrichit les architectes avec les emails"""
    
    # Charger les données
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    architectes = data.get('architectes', [])
    total = len(architectes)
    
    print(f"🎯 Enrichissement de {total} architectes")
    print(f"📁 Fichier source: {INPUT_FILE}")
    print(f"📁 Fichier sortie: {OUTPUT_FILE}")
    print("=" * 80)
    
    enriched = []
    found_emails = 0
    
    for i, arch in enumerate(architectes, 1):
        site = arch.get('site_web', '')
        
        print(f"\n[{i}/{total}] {arch.get('nom', 'N/A')[:50]}...")
        
        if site:
            print(f"  🌐 Scraping: {site}")
            emails = scrape_website(site)
            
            if emails:
                arch['emails'] = emails
                arch['email_principal'] = emails[0]
                found_emails += 1
                print(f"  ✅ Emails trouvés: {', '.join(emails[:2])}")
            else:
                arch['emails'] = []
                arch['email_principal'] = None
                print(f"  ❌ Aucun email trouvé")
            
            # Petite pause pour ne pas surcharger
            time.sleep(0.5)
        else:
            arch['emails'] = []
            arch['email_principal'] = None
            print(f"  ⚠️ Pas de site web")
        
        enriched.append(arch)
        
        # Sauvegarde intermédiaire tous les 50
        if i % BATCH_SIZE == 0:
            save_progress(enriched, i, found_emails)
    
    # Sauvegarde finale
    save_progress(enriched, total, found_emails)
    
    print("\n" + "=" * 80)
    print("✅ Enrichissement terminé!")
    print(f"📊 Total: {total} | Avec emails: {found_emails} ({found_emails/total*100:.1f}%)")

def save_progress(architectes, processed, found):
    """Sauvegarde le progrès"""
    data = {
        'metadata': {
            'total': len(architectes),
            'avec_emails': found,
            'date_enrichissement': time.strftime('%Y-%m-%d'),
            'projet': 'EnergyCo - Architectes Rénovation'
        },
        'architectes': architectes
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  💾 Sauvegarde: {processed} traités, {found} avec emails")

if __name__ == "__main__":
    enrich_architectes()
