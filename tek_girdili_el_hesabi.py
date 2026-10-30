"""Örnek 1: tek girdili Mamdani modeli, 3 kural, x = -3,9 (el hesabı).

Önce sonucu adım adım kâğıt-kalem mantığıyla (kapalı formüllerle) bulur,
sonra aynı sonucu bulanik.py'deki genel motorla karşılaştırır.

Çalıştır:  python tek_girdili_el_hesabi.py
"""

from bulanik import durulastir, mamdani
from ornekler import CIKTI_1, GIRDI_1, GIRDI_DEGERI_1, KURALLAR_1, Y1

x = GIRDI_DEGERI_1["x"]

# Çıkış kümeleri ve girdi kümeleri için kullanılan parametreler
a, b = 1.444, 2.47        # Medium çıkış: sol kenar (0 -> 1)
c, d = 4.9937, 7.0        # Medium çıkış: sağ kenar (1 -> 0)


def doğru(y_a, y_b, mu_a, mu_b):
    """İki noktadan geçen doğrunun m ve k katsayıları: mu = m*y + k."""
    m = (mu_b - mu_a) / (y_b - y_a)
    return m, mu_a - m * y_a


def parca(m, k, p, q):
    """mu = m*y + k doğrusunun [p, q] üzerindeki alanı ve y*mu momenti."""
    alan = m * (q**2 - p**2) / 2 + k * (q - p)
    moment = m * (q**3 - p**3) / 3 + k * (q**2 - p**2) / 2
    return alan, moment


print("=" * 66)
print(f"ÖRNEK 1 - Mamdani, tek girdi, 3 kural   (x = {x})")
print("=" * 66)

# --------------------------------------------------------------- Adım 1
print("\nAdım 1  Bulanıklaştırma: x = -3,9 için üyelik dereceleri")
print("  Small  : yamuk(-10, -10, -6, -3)  ->  (-3 - x) / (-3 - (-6))")
print(f"           = (-3 - ({x})) / 3 = {(-3 - x) / 3:.4f}")
print("  Medium : yamuk(-6, -3, 3, 6)      ->  (x - (-6)) / (-3 - (-6))")
print(f"           = ({x} + 6) / 3 = {(x + 6) / 3:.4f}")
print("  Large  : yamuk(3, 6, 10, 10)      ->  x < 3 olduğu için 0")
w1, w2, w3 = 0.3, 0.7, 0.0

# --------------------------------------------------------------- Adım 2
print("\nAdım 2  Kural değerlendirme (her kuralın tek koşulu var, ateşleme gücü = üyelik)")
print("  Kural 1: IF x is Small  THEN y is Small   ->  w1 = 0.3")
print("  Kural 2: IF x is Medium THEN y is Medium  ->  w2 = 0.7")
print("  Kural 3: IF x is Large  THEN y is Large   ->  w3 = 0   (ateşlenmez)")

# --------------------------------------------------------------- Adım 3
print("\nAdım 3  Çıkarım (kırpma): çıkış kümelerini ateşleme gücünde kes")
print("  Small  kümesi 0.3 seviyesinden, Medium kümesi 0.7 seviyesinden kırpılır.")
print("  Large kümesi w3 = 0 olduğu için tamamen yok olur.")

# --------------------------------------------------------------- Adım 4
y_a = a + w1 * (b - a)                 # Medium sol kenarı 0.3'e ulaştığı nokta
y_b = a + w2 * (b - a)                 # Medium sol kenarı 0.7'ye ulaştığı nokta
y_c = d - w2 * (d - c)                 # Medium sağ kenarı 0.7'ye indiği nokta
m_sol, k_sol = doğru(a, b, 0, 1)
m_sag, k_sag = doğru(c, d, 1, 0)

print("\nAdım 4  Birleştirme (max): kırpılmış iki kümenin üst zarfı")
print("  Medium sol kenar : mu(y) = %.4f*y %+.4f" % (m_sol, k_sol))
print("  Medium sağ kenar : mu(y) = %.4f*y %+.4f" % (m_sag, k_sag))
print(f"  Sol kenar 0.3'e ulaşır: y = {y_a:.4f}")
print(f"  Sol kenar 0.7'ye ulaşır: y = {y_b:.4f}")
print(f"  Sağ kenar 0.7'den iner : y = {y_c:.4f}   (0'a iniş noktası y = {d})")
print("  Birleşik küme 4 parçadan oluşur:")
print(f"    I   [0 ; {y_a:.4f}]          mu = 0.3 (Small'ın kırpılmış hâli)")
print(f"    II  [{y_a:.4f} ; {y_b:.4f}]  mu = {m_sol:.4f}*y {k_sol:+.4f}")
print(f"    III [{y_b:.4f} ; {y_c:.4f}]  mu = 0.7")
print(f"    IV  [{y_c:.4f} ; {d}]            mu = {m_sag:.4f}*y {k_sag:+.4f}")

segmentler = [
    ("I", 0.0, y_a, 0.0, 0.3),
    ("II", y_a, y_b, m_sol, k_sol),
    ("III", y_b, y_c, 0.0, 0.7),
    ("IV", y_c, d, m_sag, k_sag),
]

# --------------------------------------------------------------- Adım 5
print("\nAdım 5  Durulaştırma")
print("  Her parça için  alan = ∫ mu dy   ve   moment = ∫ y*mu dy")
print(f"  {'Parça':<6}{'alan':>10}{'moment':>12}")
toplam_alan = toplam_moment = 0.0
kumulatif = []
for ad, p, q, m, k in segmentler:
    # I ve III sabit (m = 0), k sabit değeri verir
    al, mo = parca(m, k, p, q)
    toplam_alan += al
    toplam_moment += mo
    kumulatif.append((ad, p, q, m, k, al, toplam_alan))
    print(f"  {ad:<6}{al:>10.4f}{mo:>12.4f}")
print(f"  {'Toplam':<6}{toplam_alan:>10.4f}{toplam_moment:>12.4f}")

coa = toplam_moment / toplam_alan
print(f"\n  a) COA (Centroid)  = toplam moment / toplam alan = "
      f"{toplam_moment:.4f} / {toplam_alan:.4f} = {coa:.4f}")

yari = toplam_alan / 2
print(f"\n  b) BOA (Bisector)  : toplam alanın yarısı = {yari:.4f}")
onceki = 0.0
for ad, p, q, m, k, al, kum in kumulatif:
    if kum >= yari:
        # Bu parçanın içinde: onceki + ∫_p^t (m*y+k) dy = yari  denklemini çöz
        # (sabit parçada m = 0 olduğu için doğrusal denklem)
        t = p + (yari - onceki) / k if m == 0 else None
        print(f"     Yarı alana {ad} parçasında ulaşılır (birikim: {onceki:.4f} -> {kum:.4f}).")
        print(f"     {onceki:.4f} + 0.7*(t - {p:.4f}) = {yari:.4f}  ->  t = {t:.4f}")
        boa = t
        break
    onceki = kum

maks = max(w1, w2)
print(f"\n  c) Birleşik kümenin maksimumu {maks} ve III. parçada sabit.")
som, lom = y_b, y_c
print(f"     SOM (maksimumların en küçüğü) = {som:.4f}")
print(f"     LOM (maksimumların en büyüğü) = {lom:.4f}")
print(f"     MOM (maksimumların ortalaması) = ({som:.4f} + {lom:.4f}) / 2 = {(som + lom) / 2:.4f}")

# --------------------------------------------------------------- Doğrulama
print("\nKarşılaştırma: elle hesap  ve  bulanik.py genel motoru (sayısal integral)")
sonuc = mamdani(GIRDI_1, CIKTI_1, KURALLAR_1, GIRDI_DEGERI_1, Y1)
elle = {"COA": coa, "BOA": boa, "MOM": (som + lom) / 2, "SOM": som, "LOM": lom}
print(f"  {'Yöntem':<8}{'elle':>10}{'motor':>10}")
for yontem, deger in elle.items():
    print(f"  {yontem:<8}{deger:>10.4f}{durulastir(Y1, sonuc['birlesik'], yontem):>10.4f}")
