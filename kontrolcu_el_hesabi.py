"""Örnek 2: iki girdili kontrolcü, 4 kural, x = 55 ve y = 45 (el hesabı).

Önce sonucu adım adım (kapalı formüllerle) bulur, sonra aynı sonucu
bulanik.py'deki genel motorla karşılaştırır.

Çalıştır:  python kontrolcu_el_hesabi.py
"""

import math

from bulanik import durulastir, mamdani
from ornekler import CIKTI_2, GIRDI_2, GIRDI_DEGERI_2, KURALLAR_2, Z2

x = GIRDI_DEGERI_2["x"]
y = GIRDI_DEGERI_2["y"]


def parca(m, k, p, q):
    """mu = m*z + k doğrusunun [p, q] üzerindeki alanı ve z*mu momenti."""
    alan = m * (q**2 - p**2) / 2 + k * (q - p)
    moment = m * (q**3 - p**3) / 3 + k * (q**2 - p**2) / 2
    return alan, moment


print("=" * 66)
print(f"ÖRNEK 2 - Mamdani kontrolcü, 2 girdi, 4 kural   (x = {x:.0f}, y = {y:.0f})")
print("=" * 66)

# --------------------------------------------------------------- Adım 1
print("\nAdım 1  Bulanıklaştırma")
print("  Gauss: mu = exp(-1/2 * ((x - mu0) / sigma)^2)")

x_low = math.exp(-0.5 * ((x - 0) / 10) ** 2)
x_vh = math.exp(-0.5 * ((x - 100) / 10) ** 2)
y_med = math.exp(-0.5 * ((y - 50) / 10) ** 2)

print(f"  x = {x:.0f}:")
print(f"    LOW       gauss(sigma=10, mu=0)    : exp(-0.5*(({x:.0f}-0)/10)^2)   = {x_low:.3e}")
print(f"    MEDIUM    üçgen(10, 30, 50)        : {x:.0f} > 50 olduğu için          = 0")
print(f"    HIGH      yamuk(30, 50, 70, 90)    : min((55-30)/20, 1, (90-55)/20) = min(1.25; 1; 1.75) = 1")
print(f"    VERY HIGH gauss(sigma=10, mu=100)  : exp(-0.5*(({x:.0f}-100)/10)^2) = {x_vh:.3e}")
print(f"  y = {y:.0f}:")
print(f"    LOW       üçgen(0, 0, 40)          : {y:.0f} > 40 olduğu için          = 0")
print(f"    MEDIUM    gauss(sigma=10, mu=50)   : exp(-0.5*(({y:.0f}-50)/10)^2)    = {y_med:.4f}")
print(f"    HIGH      yamuk(65, 80, 100, 100)  : {y:.0f} < 65 olduğu için          = 0")
x_med, x_high, y_low, y_high = 0.0, 1.0, 0.0, 0.0

# --------------------------------------------------------------- Adım 2
print("\nAdım 2  Kural değerlendirme (VEYA -> max)")
w1 = max(x_vh, y_med)
w2 = max(x_med, y_low)
w3 = max(x_med, y_high)
w4 = max(x_low, y_med)
print(f"  Kural 1: x VERY HIGH ({x_vh:.3e}) VEYA y MEDIUM ({y_med:.4f})  -> w1 = {w1:.4f}  -> z HIGH")
print(f"  Kural 2: x MEDIUM (0) VEYA y LOW (0)                       -> w2 = {w2:.4f}  -> z LOW")
print(f"  Kural 3: x MEDIUM (0) VEYA y HIGH (0)                      -> w3 = {w3:.4f}  -> z MEDIUM")
print(f"  Kural 4: x LOW ({x_low:.3e}) VEYA y MEDIUM ({y_med:.4f})    -> w4 = {w4:.4f}  -> z MEDIUM")
w = w1  # w1 = w4 = 0.8825: iki kuralın gücü de aynı

# --------------------------------------------------------------- Adım 3
print("\nAdım 3  Çıkarım (kırpma)")
print(f"  Kural 1: HIGH   kümesi {w:.4f} seviyesinden kırpılır")
print(f"  Kural 4: MEDIUM kümesi {w:.4f} seviyesinden kırpılır")
print("  Kural 2 (LOW) ve Kural 3 (MEDIUM) gücü 0 olduğu için kırpılınca yok olur.")

# --------------------------------------------------------------- Adım 4
z1 = 30 + w * 20           # MEDIUM sol kenar: (z - 30) / 20 = w
z2 = 80 - w * 30           # MEDIUM sağ kenar: (80 - z) / 30 = w
z_vadi = 65.0              # MEDIUM sağ kenar ile HIGH sol kenar kesişir: mu = 0.5
z4 = 50 + w * 30           # HIGH sol kenar: (z - 50) / 30 = w
print("\nAdım 4  Birleştirme (max): kırpılmış MEDIUM ve HIGH'ın üst zarfı")
print(f"  MEDIUM sol kenar  (z-30)/20 = {w:.4f}  ->  z = {z1:.4f}")
print(f"  MEDIUM sağ kenar  (80-z)/30 = {w:.4f}  ->  z = {z2:.4f}")
print(f"  MEDIUM sağ ve HIGH sol kenarı kesişir: (80-z)/30 = (z-50)/30 -> z = {z_vadi:.0f}, mu = 0.5")
print(f"  HIGH sol kenar    (z-50)/30 = {w:.4f}  ->  z = {z4:.4f}")
print("  Birleşik küme 5 parçadan oluşur:")

segmentler = [
    ("I", 30.0, z1, 1 / 20, -30 / 20, f"mu = (z-30)/20"),
    ("II", z1, z2, 0.0, w, f"mu = {w:.4f}"),
    ("III", z2, z_vadi, -1 / 30, 80 / 30, "mu = (80-z)/30"),
    ("IV", z_vadi, z4, 1 / 30, -50 / 30, "mu = (z-50)/30"),
    ("V", z4, 100.0, 0.0, w, f"mu = {w:.4f}"),
]
for ad, p, q, m, k, metin in segmentler:
    print(f"    {ad:<4}[{p:7.4f} ; {q:8.4f}]   {metin}")

# --------------------------------------------------------------- Adım 5
print("\nAdım 5  Durulaştırma")
print("  Her parça için  alan = ∫ mu dz   ve   moment = ∫ z*mu dz")
print(f"  {'Parça':<6}{'alan':>10}{'moment':>12}")
toplam_alan = toplam_moment = 0.0
kumulatif = []
for ad, p, q, m, k, _ in segmentler:
    al, mo = parca(m, k, p, q)
    toplam_alan += al
    toplam_moment += mo
    kumulatif.append((ad, p, q, m, k, al, toplam_alan))
    print(f"  {ad:<6}{al:>10.4f}{mo:>12.4f}")
print(f"  {'Toplam':<6}{toplam_alan:>10.4f}{toplam_moment:>12.4f}")

coa = toplam_moment / toplam_alan
print(f"\n  i)   COA (Centroid) = {toplam_moment:.4f} / {toplam_alan:.4f} = {coa:.4f}")

yari = toplam_alan / 2
print(f"\n  ii)  BOA (Bisector): toplam alanın yarısı = {yari:.4f}")
onceki = 0.0
boa = None
for ad, p, q, m, k, al, kum in kumulatif:
    if kum >= yari:
        # onceki + ∫_p^t (m*z + k) dz = yari   ->   m/2*t^2 + k*t + c0 = 0
        c0 = onceki - (m * p**2 / 2 + k * p) - yari
        if m == 0:
            boa = -c0 / k
        else:
            disk = k**2 - 4 * (m / 2) * c0
            kokler = [(-k + s * math.sqrt(disk)) / m for s in (1, -1)]
            boa = next(r for r in kokler if p <= r <= q)
        print(f"       Yarı alana {ad} parçasında ulaşılır (birikim: {onceki:.4f} -> {kum:.4f}).")
        break
    onceki = kum
print(f"       Denklem çözülünce  z = {boa:.4f}")

print(f"\n  iii) Maksimum üyelik {w:.4f}; iki ayrı düz parçada oluşur: II ve V")
som = z1
lom = 100.0
uzunluk_II, uzunluk_V = z2 - z1, 100.0 - z4
mom = ((z1 + z2) / 2 * uzunluk_II + (z4 + 100.0) / 2 * uzunluk_V) / (uzunluk_II + uzunluk_V)
print(f"       SOM (maksimumların en küçüğü) = {som:.4f}")
print(f"       LOM (maksimumların en büyüğü) = {lom:.4f}")
print(f"       MOM (maksimum noktalarının ortalaması):")
print(f"         II  : orta nokta {(z1 + z2) / 2:.4f}, uzunluk {uzunluk_II:.4f}")
print(f"         V   : orta nokta {(z4 + 100) / 2:.4f}, uzunluk {uzunluk_V:.4f}")
print(f"         MOM = ({(z1 + z2) / 2:.4f}*{uzunluk_II:.4f} + {(z4 + 100) / 2:.4f}*{uzunluk_V:.4f})"
      f" / ({uzunluk_II:.4f} + {uzunluk_V:.4f}) = {mom:.4f}")
print(f"       Not: (SOM + LOM) / 2 = {(som + lom) / 2:.4f} olurdu. Maksimumlar tek parça "
      "olmadığı için iki formül aynı değildir.")

# --------------------------------------------------------------- Doğrulama
print("\nKarşılaştırma: elle hesap  ve  bulanik.py genel motoru (sayısal integral)")
sonuc = mamdani(GIRDI_2, CIKTI_2, KURALLAR_2, GIRDI_DEGERI_2, Z2)
print(f"  Motorun ateşleme güçleri: {[round(g, 4) for g in sonuc['guclerin']]}")
elle = {"COA": coa, "BOA": boa, "MOM": mom, "SOM": som, "LOM": lom}
print("  (Motorun ızgara adımı 1e-4 olduğu için SOM/MOM'da son hanede ±1e-4 fark olabilir;"
      " tablo 3 ondalıkla verildi.)")
print(f"  {'Yöntem':<8}{'elle':>10}{'motor':>10}")
for yontem, deger in elle.items():
    print(f"  {yontem:<8}{deger:>10.3f}{durulastir(Z2, sonuc['birlesik'], yontem):>10.3f}")
