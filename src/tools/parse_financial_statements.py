import json
import urllib.request
import sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

with open("G:/My Drive/ØkAdmOfficeHub/data/erp_exports/det_norske_brenneri_regnskap_brreg.json", encoding="utf-8") as f:
    regnskaper = json.load(f)

records = []
for r in regnskaper:
    periode = r.get("regnskapsperiode", {})
    aar = periode.get("tilDato", "")[:4]
    
    # Resultatregnskap
    res = r.get("resultatregnskapResultat", {})
    driftsres = res.get("driftsresultat", {})
    inntekter = driftsres.get("driftsinntekter", {})
    kostnader = driftsres.get("driftskostnad", {}) or driftsres.get("driftskostnader", {})
    finans = res.get("finansresultat", {})
    
    salgsinntekter = inntekter.get("salgsinntekter", 0.0)
    andre_driftsinntekter = inntekter.get("annenDriftsinntekt", 0.0)
    sum_driftsinntekter = inntekter.get("sumDriftsinntekter", salgsinntekter)
    
    loennskostnad = kostnader.get("loennskostnad", 0.0)
    varekostnad = kostnader.get("varekostnad", 0.0)
    avskrivninger = kostnader.get("avskrivningPaaVarigeDriftsmidlerOgImmaterielleEiendeler", 0.0)
    andre_driftskostnader = kostnader.get("annenDriftskostnad", 0.0)
    sum_driftskostnader = kostnader.get("sumDriftskostnad", 0.0)
    
    driftsresultat_ebit = driftsres.get("driftsresultat", 0.0)
    finansinntekter = finans.get("finansinntekt", {}).get("sumFinansinntekter", 0.0)
    finanskostnader = finans.get("finanskostnad", {}).get("sumFinanskostnad", 0.0)
    netto_finans = finans.get("nettoFinans", finansinntekter - finanskostnader)
    
    res_for_skatt = res.get("ordinaertResultatFoerSkattekostnad", 0.0)
    skattekostnad = res.get("ordinaertResultatSkattekostnad", 0.0)
    aarsresultat = res.get("aarsresultat", 0.0)
    
    # Balanse
    eiendeler = r.get("eiendeler", {})
    sum_anleggsmidler = eiendeler.get("anleggsmidler", {}).get("sumAnleggsmidler", 0.0)
    sum_omloepsmidler = eiendeler.get("omloepsmidler", {}).get("sumOmloepsmidler", 0.0)
    
    varelager = eiendeler.get("sumVarer", eiendeler.get("omloepsmidler", {}).get("varer", 0.0))
    kundefordringer = eiendeler.get("sumFordringer", eiendeler.get("omloepsmidler", {}).get("fordringer", 0.0))
    bankinnskudd = eiendeler.get("sumBankinnskuddOgKontanter", eiendeler.get("omloepsmidler", {}).get("bankinnskuddKontanterOgLignende", 0.0))
    sum_eiendeler = eiendeler.get("sumEiendeler", sum_anleggsmidler + sum_omloepsmidler)
    
    # Egenkapital og gjeld
    ek_gjeld = r.get("egenkapitalGjeld", {})
    innskutt_ek = ek_gjeld.get("egenkapital", {}).get("innskuttEgenkapital", {}).get("sumInnskuttEgenkaptial", 0.0)
    opptjent_ek = ek_gjeld.get("egenkapital", {}).get("opptjentEgenkapital", {}).get("sumOpptjentEgenkapital", 0.0)
    sum_egenkapital = ek_gjeld.get("egenkapital", {}).get("sumEgenkapital", innskutt_ek + opptjent_ek)
    
    gjeld = ek_gjeld.get("gjeldOversikt", {})
    kortsiktig_gjeld = gjeld.get("kortsiktigGjeld", {}).get("sumKortsiktigGjeld", 0.0)
    langsiktig_gjeld = gjeld.get("langsiktigGjeld", {}).get("sumLangsiktigGjeld", 0.0)
    sum_gjeld = gjeld.get("sumGjeld", kortsiktig_gjeld + langsiktig_gjeld)
    
    records.append({
        "Regnskapsår": aar,
        "Salgsinntekter (NOK)": salgsinntekter,
        "Sum driftsinntekter (NOK)": sum_driftsinntekter,
        "Lønnskostnad (NOK)": loennskostnad,
        "Sum driftskostnader (NOK)": sum_driftskostnader,
        "Driftsresultat EBIT (NOK)": driftsresultat_ebit,
        "Netto finans (NOK)": netto_finans,
        "Resultat før skatt (NOK)": res_for_skatt,
        "Skattekostnad (NOK)": skattekostnad,
        "Årsresultat (NOK)": aarsresultat,
        "Varelager (NOK)": varelager,
        "Kundefordringer (NOK)": kundefordringer,
        "Bankinnskudd & Kontanter (NOK)": bankinnskudd,
        "Sum omløpsmidler (NOK)": sum_omloepsmidler,
        "Sum anleggsmidler (NOK)": sum_anleggsmidler,
        "Totalsum eiendeler (NOK)": sum_eiendeler,
        "Innskutt egenkapital (NOK)": innskutt_ek,
        "Opptjent egenkapital (NOK)": opptjent_ek,
        "Sum egenkapital (NOK)": sum_egenkapital,
        "Kortsiktig gjeld (NOK)": kortsiktig_gjeld,
        "Langsiktig gjeld (NOK)": langsiktig_gjeld,
        "Totalsum gjeld (NOK)": sum_gjeld,
        "Egenkapitalandel (%)": round((sum_egenkapital / sum_eiendeler * 100.0), 1) if sum_eiendeler else 0.0,
    })

df = pd.DataFrame(records)
print(df.T.to_string())

csv_out = "G:/My Drive/ØkAdmOfficeHub/data/erp_exports/det_norske_brenneri_regnskapshistorikk.csv"
df.to_csv(csv_out, index=False, encoding="utf-8-sig")
print(f"\nOppdatert: {csv_out}")