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

# 1. Enhetsregisteret (Grunndata)
print("=" * 60)
print(f"Henter grunndata fra Enhetsregisteret for {orgnr}...")
print("=" * 60)

url_enhet = f"https://data.brreg.no/enhetsregisteret/api/enheter/{orgnr}"
req_enhet = urllib.request.Request(url_enhet, headers=headers)
try:
    with urllib.request.urlopen(req_enhet) as resp:
        enhet_data = json.loads(resp.read().decode("utf-8"))
        print(f"Navn:                  {enhet_data.get('navn')}")
        print(f"Organisasjonsform:     {enhet_data.get('organisasjonsform', {}).get('beskrivelse')} ({enhet_data.get('organisasjonsform', {}).get('kode')})")
        print(f"Stiftelsesdato:        {enhet_data.get('stiftelsesdato')}")
        print(f"Reg. Enhetsregisteret: {enhet_data.get('registreringsdatoEnhetsregisteret')}")
        print(f"Næringskode:           {enhet_data.get('naeringskode1', {}).get('kode')} - {enhet_data.get('naeringskode1', {}).get('beskrivelse')}")
        print(f"Antall ansatte:        {enhet_data.get('antallAnsatte')}")
        print(f"Forretningsadresse:    {enhet_data.get('forretningsadresse')}")
        print(f"Postadresse:           {enhet_data.get('postadresse')}")
        print(f"MVA-registrert:        {enhet_data.get('registrertIMvaregisteret')}")
        print(f"Konkurs:               {enhet_data.get('konkurs')}")
        print(f"Under avvikling:       {enhet_data.get('underAvvikling')}")
        print(f"Formål:                {enhet_data.get('formaal')}")
except Exception as e:
    print(f"Feil ved henting av enhetsdata: {e}")

# 2. Underenheter (Virksomheter / produksjonssteder)
print("\n" + "=" * 60)
print("Henter tilknyttede underenheter / bedrifter...")
print("=" * 60)
url_under = f"https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet={orgnr}"
req_under = urllib.request.Request(url_under, headers=headers)
try:
    with urllib.request.urlopen(req_under) as resp:
        under_data = json.loads(resp.read().decode("utf-8"))
        underenheter = under_data.get("_embedded", {}).get("underenheter", [])
        print(f"Fant {len(underenheter)} underenhet(er):")
        for u in underenheter:
            print(f" - {u.get('navn')} (Orgnr: {u.get('organisasjonsnummer')}), Næring: {u.get('naeringskode1', {}).get('kode')}, Ansatte: {u.get('antallAnsatte')}")
except Exception as e:
    print(f"Feil ved henting av underenheter: {e}")

# 3. Regnskapsregisteret (Offisielle årsregnskaper)
print("\n" + "=" * 60)
print(f"Henter regnskapshistorikk fra Regnskapsregisteret for {orgnr}...")
print("=" * 60)
url_regnskap = f"https://data.brreg.no/regnskapsregisteret/regnskap/{orgnr}"
req_regnskap = urllib.request.Request(url_regnskap, headers=headers)
try:
    with urllib.request.urlopen(req_regnskap) as resp:
        regnskap_liste = json.loads(resp.read().decode("utf-8"))
        print(f"Fant {len(regnskap_liste)} innsendte årsregnskap:")
        for r in regnskap_liste:
            periode = r.get("regnskapsperiode", {})
            aar = periode.get("tilDato", "")[:4]
            fra = periode.get("fraDato")
            til = periode.get("tilDato")
            rtype = r.get("regnskapstype")
            oppstilt = r.get("oppstillingsplan")
            print(f"År: {aar} ({fra} til {til}) | Type: {rtype} | ID: {r.get('id')}")
            
            # Print overordnet resultat og balanse dersom tilstede
            res = r.get("egenkapitalGjeld", {})
            inntekter = r.get("virksomhetskostnader", {})
            resultat = r.get("resultatregnskapResultat", {})
            print(f"   Tilgjengelige seksjoner: {list(r.keys())}")
except Exception as e:
    print(f"Feil ved oppslag i Regnskapsregisteret: {e}")

