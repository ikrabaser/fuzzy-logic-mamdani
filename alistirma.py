"""Alıştırma modu: rastgele bir sıcaklık için fan hızı sorusu üretir, cevabını denetler.

Sistem fan_hizi_ornegi.py ile aynıdır (Ilık / Sıcak girdi, Orta / Hızlı çıkış). Her soruda
üç cevap istenir: Ilık üyeliği, Sıcak üyeliği ve seçilen yöntemle net fan hızı. Doğru
cevaplar bulanik.py'deki genel motordan gelir.

Çalıştır:
    python alistirma.py                   # 3 soru, yöntemler rastgele
    python alistirma.py --soru 5          # 5 soru
    python alistirma.py --yontem COA      # hep COA sor (COA, BOA, MOM, SOM, LOM)
    python alistirma.py --seed 42         # aynı soruları yeniden üret
    python alistirma.py --cozum 28        # x = 28 için çözümü adım adım göster

Ondalık için nokta ya da virgül yazabilirsin. Boş bırakıp Enter'a basarsan o cevap boş
sayılır ve soru sonunda çözüm özeti gösterilir.
"""

import argparse
import random

import fan_hizi_ornegi as fan
from bulanik import YONTEMLER, durulastir, mamdani

UYELIK_TOLERANSI = 0.01
DURULASTIRMA_TOLERANSI = 0.1

SISTEM = """Sistem
  Girdi (sıcaklık, °C)    : Ilık = üçgen(15, 25, 35),  Sıcak = üçgen(25, 35, 45)
  Çıkış (fan hızı, 0-100) : Orta = üçgen(30, 50, 70),  Hızlı = üçgen(50, 75, 100)
  Kural 1: EĞER sıcaklık Ilık  İSE hız Orta
  Kural 2: EĞER sıcaklık Sıcak İSE hız Hızlı
"""

YONTEM_ADLARI = {"COA": "centroid (COA)", "BOA": "bisector (BOA)", "MOM": "maksimumların ortalaması (MOM)",
                 "SOM": "maksimumların en küçüğü (SOM)", "LOM": "maksimumların en büyüğü (LOM)"}


# --------------------------------------------------------------------------
# Soru üretme ve doğru cevap
# --------------------------------------------------------------------------

def soru_uret(rng, yontem=None):
    """Rastgele tam sayı bir sıcaklık seçer. x = 30'da iki kural eşit güçte ateşlendiği ve
    maksimumlar iki ayrı parçada kaldığı için (MOM / SOM / LOM karmaşık) 30 sorulmaz."""
    x = rng.choice([v for v in range(16, 45) if v != 30])
    return {"x": float(x), "yontem": yontem or rng.choice(list(YONTEMLER))}


def cevap_hesapla(x):
    """Doğru cevaplar: iki üyelik ve beş durulaştırma yöntemi."""
    guc = [fan.uyelik(x, *fan.SICAKLIK[kosul])[0] for kosul, _ in fan.KURALLAR]
    s = mamdani(fan.GIRDI, fan.CIKTI, fan.MOTOR_KURALLARI, {"sicaklik": x}, fan.Y)
    sonuc = {"Ilık": guc[0], "Sıcak": guc[1]}
    sonuc.update({m: durulastir(fan.Y, s["birlesik"], m) for m in YONTEMLER})
    return sonuc


def sayi_oku(metin):
    """'0,7' ve '0.7' ikisini de okur. Boş ya da geçersiz girişte None döndürür."""
    metin = metin.strip().replace(",", ".")
    if not metin:
        return None
    try:
        return float(metin)
    except ValueError:
        return None


def dogru_mu(verilen, dogru, tolerans):
    return verilen is not None and abs(verilen - dogru) <= tolerans


def sor(mesaj):
    try:
        return sayi_oku(input(mesaj))
    except EOFError:                      # girdi bittiyse boş cevap say
        return None


# --------------------------------------------------------------------------
# Çözüm özeti
# --------------------------------------------------------------------------

def cozum_ozeti(x, cevaplar):
    print("  --- Çözüm özeti ---")
    for ad, (a, b, c) in fan.SICAKLIK.items():
        print(f"  {ad:<5}: {fan.uyelik(x, a, b, c)[1]}")
    egriler = []
    for (kosul, sonuc), w in zip(fan.KURALLAR, (cevaplar["Ilık"], cevaplar["Sıcak"])):
        if w == 0:
            print(f"  {sonuc}: w = 0, kural ateşlenmez")
            continue
        a, b, c = fan.HIZ[sonuc]
        sol, sag = a + w * (b - a), c - w * (c - b)
        print(f"  {sonuc}: {w:.4f} seviyesinden kesilir, plato y = {sol:.4f} ile {sag:.4f} arasında")
        egriler.append([(a, 0.0), (sol, w), (sag, w), (c, 0.0)])
    V, _ = fan.zarf(egriler)
    kose = " -> ".join(f"({y:g}, {mu:.2f})" for y, mu in V)
    print(f"  Birleşik küme köşeleri: {kose}")
    sonuc = "  ".join(f"{m} = {cevaplar[m]:.3f}" for m in YONTEMLER)
    print(f"  Beş yöntem: {sonuc}")
    print("  Adım adım tam çözüm için:  python alistirma.py --cozum", f"{x:g}\n")


# --------------------------------------------------------------------------
# Alıştırma döngüsü
# --------------------------------------------------------------------------

def alistirma_yap(soru_sayisi=3, yontem=None, seed=None):
    """Soruları sorar. Döndürür: (doğru cevap sayısı, toplam cevap sayısı)."""
    rng = random.Random(seed)
    print(SISTEM)
    dogru_sayisi = toplam = 0
    for k in range(1, soru_sayisi + 1):
        soru = soru_uret(rng, yontem)
        x, m = soru["x"], soru["yontem"]
        cevaplar = cevap_hesapla(x)

        print(f"Soru {k}/{soru_sayisi}")
        print(f"  Sıcaklık x = {x:g} °C. Fan hızını {YONTEM_ADLARI[m]} yöntemiyle durulaştırınız.")
        verilenler = {
            "Ilık": sor("  a) Ilık üyeliği        : "),
            "Sıcak": sor("  b) Sıcak üyeliği       : "),
            m: sor(f"  c) {m} ile net hız      : "),
        }
        hepsi_dogru = True
        for ad, verilen in verilenler.items():
            tol = UYELIK_TOLERANSI if ad in ("Ilık", "Sıcak") else DURULASTIRMA_TOLERANSI
            toplam += 1
            if dogru_mu(verilen, cevaplar[ad], tol):
                dogru_sayisi += 1
                print(f"     {ad}: doğru ({cevaplar[ad]:.4f})")
            else:
                hepsi_dogru = False
                gosterilen = "boş" if verilen is None else f"{verilen:g}"
                print(f"     {ad}: yanlış (yazdığın: {gosterilen}, doğru: {cevaplar[ad]:.4f})")
        if hepsi_dogru:
            print("  Hepsi doğru.\n")
        else:
            cozum_ozeti(x, cevaplar)
    print(f"Skor: {dogru_sayisi}/{toplam}")
    return dogru_sayisi, toplam


def main():
    ap = argparse.ArgumentParser(description="Bulanık mantık alıştırma modu (sıcaklık -> fan hızı)")
    ap.add_argument("--soru", type=int, default=3, help="soru sayısı (varsayılan 3)")
    ap.add_argument("--yontem", choices=list(YONTEMLER), help="hep bu yöntemi sor")
    ap.add_argument("--seed", type=int, help="aynı soruları yeniden üretmek için")
    ap.add_argument("--cozum", type=float, metavar="X", help="x için çözümü adım adım göster")
    args = ap.parse_args()
    if args.cozum is not None:
        fan.calistir(args.cozum)
    else:
        alistirma_yap(args.soru, args.yontem, args.seed)


if __name__ == "__main__":
    main()
