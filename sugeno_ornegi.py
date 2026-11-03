"""Örnek 4: Sugeno modeli ile sıcaklık -> fan hızı, Mamdani ile karşılaştırma.

Aynı girdi kümeleri ve aynı kurallar (fan_hizi_ornegi.py), ama çıkış farklı kurulur.

    Mamdani : kural sonucu bir BULANIK KÜME  -> kırp, birleştir, durulaştır (alan hesabı)
    Sugeno  : kural sonucu bir SABİT SAYI z  -> ağırlıklı ortalama, durulaştırma gerekmez

Kural 1: EĞER sıcaklık Ilık  İSE  z1 = 50   (Orta kümesinin tepesi)
Kural 2: EĞER sıcaklık Sıcak İSE  z2 = 75   (Hızlı kümesinin tepesi)

    z = (w1*z1 + w2*z2) / (w1 + w2)

Çalıştır:  python sugeno_ornegi.py          (x = 28 ve x = 33, sonra karşılaştırma tablosu)
           python sugeno_ornegi.py 30 40    (verilen sıcaklıklar için)
"""

import sys

import fan_hizi_ornegi as fan
from bulanik import agirlikli_ortalama, durulastir, mamdani

# Sugeno kural sonuçları: her kuralın sabit çıkışı (Mamdani çıkış kümesinin tepe noktası)
SABITLER = [fan.HIZ[sonuc][1] for _, sonuc in fan.KURALLAR]      # [50, 75]


def sugeno(x):
    """Sugeno (sıfırıncı derece) çıkışı. Döndürür: ateşleme güçleri, sabitler, net değer."""
    guclerin = [fan.uyelik(x, *fan.SICAKLIK[kosul])[0] for kosul, _ in fan.KURALLAR]
    if sum(guclerin) == 0:
        raise ValueError("Hiçbir kural ateşlenmedi: ağırlıklı ortalama tanımsız.")
    return guclerin, SABITLER, agirlikli_ortalama(guclerin, SABITLER)


def mamdani_coa(x):
    s = mamdani(fan.GIRDI, fan.CIKTI, fan.MOTOR_KURALLARI, {"sicaklik": x}, fan.Y)
    return durulastir(fan.Y, s["birlesik"], "COA")


def calistir(x):
    print("=" * 66)
    print(f"ÖRNEK 4 - Sugeno modeli, sıcaklık -> fan hızı   (x = {x:g} °C)")
    print("=" * 66)

    print("\nAdım 1  Bulanıklaştırma (Mamdani ile aynı)")
    for ad, (a, b, c) in fan.SICAKLIK.items():
        print(f"  {ad:<6}: ucgen({a}, {b}, {c})  ->  {fan.uyelik(x, a, b, c)[1]}")

    print("\nAdım 2  Ateşleme gücü (Mamdani ile aynı)")
    try:
        guclerin, sabitler, z = sugeno(x)
    except ValueError as hata:
        print(f"  {hata}\n")
        return
    for i, ((kosul, _), w) in enumerate(zip(fan.KURALLAR, guclerin), start=1):
        print(f"  Kural {i}: IF sıcaklık is {kosul:<5}  ->  w{i} = {w:.4f}")

    print("\nAdım 3  Kural sonuçları: kırpma yok, her kuralın çıkışı bir sabit sayı")
    for i, ((_, sonuc), zi) in enumerate(zip(fan.KURALLAR, sabitler), start=1):
        print(f"  Kural {i}: THEN z{i} = {zi:g}   ({sonuc} kümesinin tepesi)")

    print("\nAdım 4  Ağırlıklı ortalama (birleştirme ve alan hesabı yok)")
    pay = " + ".join(f"{w:.4f}*{zi:g}" for w, zi in zip(guclerin, sabitler))
    payda = " + ".join(f"{w:.4f}" for w in guclerin)
    print(f"  z = ({pay}) / ({payda})")
    print(f"    = {sum(w * zi for w, zi in zip(guclerin, sabitler)):.4f} / {sum(guclerin):.4f}")
    print(f"    = {z:.4f}")

    coa = mamdani_coa(x)
    print(f"\nKarşılaştırma: Mamdani (COA) = {coa:.4f},  Sugeno = {z:.4f},  fark = {z - coa:+.4f}\n")


def karsilastirma_tablosu(sicakliklar):
    print("=" * 66)
    print("Sugeno ve Mamdani (COA) karşılaştırması")
    print("=" * 66)
    print(f"  {'x':>5}{'w1':>8}{'w2':>8}{'Sugeno':>10}{'Mamdani COA':>14}{'fark':>9}")
    for x in sicakliklar:
        try:
            guclerin, _, z = sugeno(x)
        except ValueError:
            print(f"  {x:>5g}   hiçbir kural ateşlenmedi")
            continue
        coa = mamdani_coa(x)
        fark = round(z - coa, 3) + 0.0          # -0.000 yazmasın
        print(f"  {x:>5g}{guclerin[0]:>8.3f}{guclerin[1]:>8.3f}{z:>10.3f}{coa:>14.3f}{fark:>+9.3f}")
    print("\n  Sugeno yalnızca kümelerin tepe noktalarına bakar; Mamdani COA ise kırpılmış")
    print("  kümelerin genişliğini de hesaba katar. Hızlı kümesi (50-100) Orta'dan (30-70)")
    print("  geniş olduğu için iki kural birlikte ateşlendiğinde (25 < x < 35) COA, Sugeno'dan")
    print("  farklı çıkar. Tek kural ateşlendiğinde (x <= 25 ve x >= 35) kırpılmış küme")
    print("  simetrik olduğundan ikisi aynıdır.\n")


if __name__ == "__main__":
    degerler = [float(a) for a in sys.argv[1:]]
    for sicaklik in degerler or [28.0, 33.0]:
        calistir(sicaklik)
    karsilastirma_tablosu(degerler or [20, 25, 28, 30, 33, 35, 40])
