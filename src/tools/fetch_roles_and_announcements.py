import sys
import json
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

orgnr = "996928977"

# 1. Roller i selskapet (Styre, Daglig leder, Revisor)
print("=" * 65)
print("ROLLER & STYRE I DET NORSKE BRENNERI AS")
print("=" * 65)

url_roller = f"https://data.brreg.no/enhetsregisteret/api/enheter/{orgnr}/roller"
req_roller = urllib.request.Request(url_roller, headers=headers)
try:
    with urllib.request.urlopen(req_roller) as resp:
        roller_data = json.loads(resp.read().decode("utf-8"))
        for g in roller_data.get("rollegrupper", []):
            gruppe_navn = g.get("type", {}).get("beskrivelse")
            print(f"\n📂 {gruppe_navn}:")
            for rol in g.get("roller", []):
                tittel = rol.get("type", {}).get("beskrivelse")
                person = rol.get("person", {})
                if person:
                    fornavn = person.get("navn", {}).get("fornavn", "")
                    mellom = person.get("navn", {}).get("mellomnavn", "")
                    etternavn = person.get("navn", {}).get("slektsnavn", "")
                    navn = f"{fornavn} {mellom} {etternavn}".replace("  ", " ").strip()
                    fodselsdato = person.get("fodselsdato", "")
                    fratraadt = rol.get("fratraadt", False)
                    print(f"  • {tittel}: {navn} (Fratrådt: {fratraadt})")
                elif rol.get("enhet"):
                    enhet_navn = rol.get("enhet", {}).get("navn", "")
                    enhet_org = rol.get("enhet", {}).get("organisasjonsnummer", "")
                    print(f"  • {tittel}: {enhet_navn} (Org.nr: {enhet_org})")
except Exception as e:
    print(f"Kunne ikke hente roller: {e}")

# 2. Siste Kunngjøringer fra Brønnøysund
print("\n" + "=" * 65)
print("SISTE KUNNGJØRINGER I BRØNNØYSUNDREGISTERET")
print("=" * 65)

url_k = f"https://data.brreg.no/enhetsregisteret/api/kunngjoringer?orgnr={orgnr}"
try:
    with urllib.request.urlopen(urllib.request.Request(url_k, headers=headers)) as r:
        k_data = json.loads(r.read().decode("utf-8"))
        kunngj = k_data.get("_embedded", {}).get("kunngjoringer", [])
        if kunngj:
            for k in kunngj[:8]:
                dato = k.get("publisertDato", "")
                ktype = k.get("type", {}).get("beskrivelse", "")
                tittel = k.get("tittel", "")
                print(f"  • {dato}: {ktype} {f'- {tittel}' if tittel else ''}")
        else:
            print("  Ingen spesifikke kunngjøringer returnert på dette endepunktet.")
except Exception as e:
    print(f"Kunne ikke hente kunngjøringer: {e}")

