"""Örnek 3: sıcaklık -> fan hızı, tek girdili Mamdani modeli, 2 kural (el hesabı).

Girdi (sıcaklık, °C)   : Ilık = üçgen(15, 25, 35),  Sıcak = üçgen(25, 35, 45)
Çıkış (fan hızı, 0-100): Orta = üçgen(30, 50, 70),  Hızlı = üçgen(50, 75, 100)
Kural 1: EĞER sıcaklık Ilık  İSE hız Orta
Kural 2: EĞER sıcaklık Sıcak İSE hız Hızlı

Önce sonucu adım adım kapalı formüllerle (kâğıt-kalem mantığıyla) bulur, sonra aynı
sonucu bulanik.py'deki genel motorla karşılaştırır. Beş durulaştırma yönteminin
(COA, BOA, MOM, SOM, LOM) hepsi hesaplanır.

Çalıştır:  python fan_hizi_ornegi.py          (x = 28 ve x = 33)
           python fan_hizi_ornegi.py 30 40    (verilen sıcaklıklar için)
"""

import sys
from functools import partial

import numpy as np

from bulanik import durulastir, mamdani, ucgen

# --------------------------------------------------------------------------
# Problem tanımı
# --------------------------------------------------------------------------

SICAKLIK = {"Ilık": (15, 25, 35), "Sıcak": (25, 35, 45)}   # (başlangıç, tepe, bitiş)
HIZ = {"Orta": (30, 50, 70), "Hızlı": (50, 75, 100)}
KURALLAR = [("Ilık", "Orta"), ("Sıcak", "Hızlı")]          # (koşul, sonuç)

Y = np.linspace(0, 100, 1_000_001)                          # çıkış evreni (genel motor için)

GIRDI = {"sicaklik": {ad: partial(ucgen, a=a, b=b, c=c) for ad, (a, b, c) in SICAKLIK.items()}}
CIKTI = {ad: partial(ucgen, a=a, b=b, c=c) for ad, (a, b, c) in HIZ.items()}
MOTOR_KURALLARI = [{"kosullar": [("sicaklik", k)], "sonuc": s} for k, s in KURALLAR]


# --------------------------------------------------------------------------
# El hesabı yardımcıları
# --------------------------------------------------------------------------

def uyelik(x, a, b, c):
    """Üçgen üyelik derecesi ve hangi kenardan, hangi formülle bulunduğu."""
    if x <= a or x >= c:
        return 0.0, f"x = {x:g}, ({a}, {c}) aralığının dışında -> 0"
    if x == b:
        return 1.0, f"x tam tepede ({b}) -> 1"
    if x < b:
        d = (x - a) / (b - a)
        return d, f"{x:g} < {b} (tepenin solu), yükselen kenar: ({x:g} - {a}) / ({b} - {a}) = {d:.4f}"
    d = (c - x) / (c - b)
    return d, f"{x:g} > {b} (tepenin sağı), alçalan kenar: ({c} - {x:g}) / ({c} - {b}) = {d:.4f}"


def kesisimler(P, Q):
    """İki parçalı doğrusal eğrinin (köşe listeleri) kesiştiği (y, mu) noktaları."""
    sonuc = []
    for (y1, m1), (y2, m2) in zip(P[:-1], P[1:]):
        for (y3, n3), (y4, n4) in zip(Q[:-1], Q[1:]):
            if y2 - y1 < 1e-12 or y4 - y3 < 1e-12:
                continue
            e1 = (m2 - m1) / (y2 - y1)
            e2 = (n4 - n3) / (y4 - y3)
            if abs(e1 - e2) < 1e-12:
                continue
            y = (n3 - m1 + e1 * y1 - e2 * y3) / (e1 - e2)
            if max(y1, y3) - 1e-12 <= y <= min(y2, y4) + 1e-12:
                sonuc.append((round(y, 10), m1 + e1 * (y - y1)))
    return sonuc


def zarf(egriler):
    """Kırpılmış kümelerin max'ı (üst zarf) için köşe noktaları ve kesişimler."""
    adaylar = {round(y, 10) for E in egriler for y, _ in E}
    kes = []
    for i in range(len(egriler)):
        for j in range(i + 1, len(egriler)):
            kes += kesisimler(egriler[i], egriler[j])
    adaylar |= {y for y, _ in kes}
    ys = np.array(sorted(adaylar))
    mus = np.max([np.interp(ys, [p[0] for p in E], [p[1] for p in E]) for E in egriler], axis=0)
    return list(zip(ys.tolist(), mus.tolist())), kes


def parca(m, k, p, q):
    """mu = m*y + k doğrusunun [p, q] üzerindeki alanı ve y*mu momenti."""
    alan = m * (q**2 - p**2) / 2 + k * (q - p)
    moment = m * (q**3 - p**3) / 3 + k * (q**2 - p**2) / 2
    return alan, moment


def alan_denklemi_coz(m, k, p, q, kalan):
    """[p, t] üzerindeki alan = kalan olacak şekilde t'yi bulur (t, [p, q] içinde)."""
    if abs(m) < 1e-12:
        return p + kalan / k
    A, B, C = m / 2, k, -(m / 2 * p**2 + k * p + kalan)
    kok = np.sqrt(B * B - 4 * A * C)
    adaylar = [(-B + kok) / (2 * A), (-B - kok) / (2 * A)]
    return next(t for t in adaylar if p - 1e-9 <= t <= q + 1e-9)


def dogru_parcalari(V):
    """Köşe listesinden doğru parçalarını çıkarır; aynı doğru üstündekileri birleştirir."""
    parcalar = []
    for (y1, m1), (y2, m2) in zip(V[:-1], V[1:]):
        if y2 - y1 < 1e-9:
            continue
        egim = (m2 - m1) / (y2 - y1)
        k = m1 - egim * y1
        if parcalar and abs(parcalar[-1][2] - egim) < 1e-9 and abs(parcalar[-1][3] - k) < 1e-9:
            parcalar[-1][1] = y2
        else:
            parcalar.append([y1, y2, egim, k])
    return parcalar


ROMEN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


# --------------------------------------------------------------------------
# Çözüm
# --------------------------------------------------------------------------

def calistir(x):
    print("=" * 66)
    print(f"ÖRNEK 3 - sıcaklık -> fan hızı, tek girdi, 2 kural   (x = {x:g} °C)")
    print("=" * 66)

    # ----------------------------------------------------------- Adım 1
    print("\nAdım 1  Bulanıklaştırma: x için üyelik dereceleri")
    derece = {}
    for ad, (a, b, c) in SICAKLIK.items():
        derece[ad], metin = uyelik(x, a, b, c)
        print(f"  {ad:<6}: ucgen({a}, {b}, {c})  ->  {metin}")

    # ----------------------------------------------------------- Adım 2
    print("\nAdım 2  Kural değerlendirme (her kuralın tek koşulu var, ateşleme gücü = üyelik)")
    guc = []
    for i, (kosul, sonuc) in enumerate(KURALLAR, start=1):
        guc.append(derece[kosul])
        print(f"  Kural {i}: IF sıcaklık is {kosul:<5} THEN hız is {sonuc:<5} ->  w{i} = {guc[-1]:.4f}")
    if max(guc) == 0:
        print("\n  Hiçbir kural ateşlenmedi: birleşik küme boş, durulaştırma yapılamaz.\n")
        return

    # ----------------------------------------------------------- Adım 3
    print("\nAdım 3  Çıkarım (kırpma): çıkış kümelerini ateşleme gücünde kes")
    egriler = []
    for i, ((_, sonuc), g) in enumerate(zip(KURALLAR, guc), start=1):
        a, b, c = HIZ[sonuc]
        if g == 0:
            print(f"  Kural {i}: w{i} = 0 olduğu için {sonuc} kümesi tamamen yok olur.")
            continue
        sol = a + g * (b - a)
        sag = c - g * (c - b)
        print(f"  Kural {i}: {sonuc} kümesi {g:.4f} seviyesinden kesilir")
        print(f"           sol kenar : {a} + {g:.4f}*({b} - {a}) = {sol:.4f}")
        print(f"           sağ kenar : {c} - {g:.4f}*({c} - {b}) = {sag:.4f}")
        print(f"           köşeler   : ({a}, 0) -> ({sol:.4f}, {g:.4f}) -> ({sag:.4f}, {g:.4f}) -> ({c}, 0)")
        egriler.append([(a, 0.0), (sol, g), (sag, g), (c, 0.0)])

    # ----------------------------------------------------------- Adım 4
    V, kes = zarf(egriler)
    print("\nAdım 4  Birleştirme (max): kırpılmış kümelerin üst zarfı")
    if kes:
        for y, mu in kes:
            print(f"  Kümeler y = {y:.4f} noktasında kesişir (mu = {mu:.4f})")
    else:
        print("  Kırpılmış kümeler kesişmiyor, biri her yerde diğerinin üstünde.")
    parcalar = dogru_parcalari(V)
    print("  Birleşik küme parçalardan oluşur:  mu(y) = m*y + k")

    toplam_alan = toplam_moment = 0.0
    print(f"\n  {'Parça':<7}{'y aralığı':>22}{'mu(y)':>24}{'alan':>10}{'moment':>12}")
    satirlar = []
    for n, (p, q, m, k) in enumerate(parcalar):
        alan, moment = parca(m, k, p, q)
        toplam_alan += alan
        toplam_moment += moment
        mu_metni = f"{k:.4f}" if abs(m) < 1e-9 else f"{m:.4f}*y {k:+.4f}"
        satirlar.append((p, q, m, k, alan))
        print(f"  {ROMEN[n]:<7}{f'[{p:.4f} ; {q:.4f}]':>22}{mu_metni:>24}{alan:>10.4f}{moment:>12.4f}")
    print(f"  {'Toplam':<7}{'':>22}{'':>24}{toplam_alan:>10.4f}{toplam_moment:>12.4f}")

    # ----------------------------------------------------------- Adım 5
    print("\nAdım 5  Durulaştırma: beş yöntem")

    coa = toplam_moment / toplam_alan
    print(f"\n  a) COA (Centroid)  = toplam moment / toplam alan = "
          f"{toplam_moment:.4f} / {toplam_alan:.4f} = {coa:.4f}")

    yari = toplam_alan / 2
    print(f"\n  b) BOA (Bisector)  : toplam alanın yarısı = {yari:.4f}")
    birikim = 0.0
    boa = None
    for n, (p, q, m, k, alan) in enumerate(satirlar):
        if birikim + alan >= yari - 1e-12:
            kalan = yari - birikim
            print(f"     {ROMEN[n]}. parçaya kadar birikim = {birikim:.4f}, yarıya {kalan:.4f} eksik")
            if abs(m) < 1e-9:
                print(f"     Parça düz (mu = {k:.4f}): t = {p:.4f} + {kalan:.4f} / {k:.4f}")
            else:
                print(f"     {m / 2:.4f}*t^2 {k:+.4f}*t {-(m / 2 * p**2 + k * p + kalan):+.4f} = 0  denklemi çözülür")
            boa = alan_denklemi_coz(m, k, p, q, kalan)
            print(f"     t = {boa:.4f}")
            break
        birikim += alan

    en_yuksek = max(mu for _, mu in V)
    tepeler = [y for y, mu in V if mu >= en_yuksek - 1e-9]
    som, lom = min(tepeler), max(tepeler)
    platolar = [(y1, y2) for (y1, m1), (y2, m2) in zip(V[:-1], V[1:])
                if y2 - y1 > 1e-9 and m1 >= en_yuksek - 1e-9 and m2 >= en_yuksek - 1e-9]
    if platolar:
        mom = sum((p + q) / 2 * (q - p) for p, q in platolar) / sum(q - p for p, q in platolar)
    else:
        mom = float(np.mean(tepeler))
    print(f"\n  c) En yüksek üyelik = {en_yuksek:.4f}, y = {som:.4f} ile {lom:.4f} arasında görülüyor")
    print(f"     SOM (maksimumların en küçüğü) = {som:.4f}")
    print(f"     LOM (maksimumların en büyüğü) = {lom:.4f}")
    print(f"     MOM (maksimumların ortalaması) = ({som:.4f} + {lom:.4f}) / 2 = {mom:.4f}")

    # ----------------------------------------------------------- Kontrol
    print("\nKontrol: el hesabı ile bulanik.py'deki genel motor")
    sonuc = mamdani(GIRDI, CIKTI, MOTOR_KURALLARI, {"sicaklik": x}, Y)
    elle = {"COA": coa, "BOA": boa, "MOM": mom, "SOM": som, "LOM": lom}
    print(f"  {'Yöntem':<8}{'el hesabı':>10}{'motor':>10}")
    for yontem, deger in elle.items():
        print(f"  {yontem:<8}{deger:>10.3f}{durulastir(Y, sonuc['birlesik'], yontem):>10.3f}")
    print("  (Motorun ızgara adımı 1e-4 olduğu için son hanede ±1e-4 fark olabilir.)\n")


if __name__ == "__main__":
    for sicaklik in [float(a) for a in sys.argv[1:]] or [28.0, 33.0]:
        calistir(sicaklik)
