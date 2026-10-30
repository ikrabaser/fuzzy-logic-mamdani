"""Bulanık mantık (Mamdani) için genel fonksiyonlar.

Bu dosya tek başına çalışmaz; ornekler.py, *_el_hesabi.py, gorseller_uret.py ve
test_el_hesaplari.py buradaki fonksiyonları kullanır.

Bir Mamdani sisteminin 5 adımı ve karşılık gelen fonksiyonlar:

    1. Bulanıklaştırma     ->  ucgen, yamuk, gauss  (net girdi -> üyelik derecesi)
    2. Kural değerlendirme ->  ve (min), veya (max)  (koşulların ateşleme gücü)
    3. Çıkarım (implication) ->  kes  (çıkış kümesini ateşleme gücünde kırp)
    4. Birleştirme (aggregation) ->  birlestir  (kırpılmış kümelerin max'ı)
    5. Durulaştırma        ->  durulastir  (tek bir net değer)
"""

import numpy as np

# numpy 2'de trapz yerine trapezoid kullanılıyor; ikisini de destekle.
_integral = getattr(np, "trapezoid", None) or np.trapz


# --------------------------------------------------------------------------
# 1. Üyelik fonksiyonları
# --------------------------------------------------------------------------

def yamuk(x, a, b, c, d):
    """Yamuk üyelik fonksiyonu.

    a -> b arasında 0'dan 1'e çıkar, b -> c arasında 1'de kalır,
    c -> d arasında 1'den 0'a iner:

        mu(x) = max( min( (x-a)/(b-a), 1, (d-x)/(d-c) ), 0 )

    a == b ise sol kenar dik (omuz), c == d ise sağ kenar diktir.
    """
    x = np.asarray(x, dtype=float)
    sol = (x - a) / (b - a) if b > a else np.where(x >= b, 1.0, 0.0)
    sag = (d - x) / (d - c) if d > c else np.where(x <= c, 1.0, 0.0)
    return np.clip(np.minimum(sol, sag), 0.0, 1.0)


def ucgen(x, a, b, c):
    """Üçgen üyelik fonksiyonu: tepe b'de. Yamuğun b == c özel hâlidir."""
    return yamuk(x, a, b, b, c)


def gauss(x, sigma, mu):
    """Gauss üyelik fonksiyonu: exp( -1/2 * ((x - mu) / sigma)^2 ).

    Parametre sırası (sigma, mu) örnek problemdeki gösterimle aynıdır:
    gaussian(x; 10, 0) -> sigma = 10, mu = 0.
    Desteği sonsuzdur: merkezden uzaklaştıkça 0'a yaklaşır ama hiç 0 olmaz.
    """
    x = np.asarray(x, dtype=float)
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2)


# --------------------------------------------------------------------------
# 2. Kural değerlendirme: VE -> min, VEYA -> max
# --------------------------------------------------------------------------

def ve(*dereceler):
    """VE işlemi (t-norm): en küçük üyelik derecesi."""
    return float(min(dereceler))


def veya(*dereceler):
    """VEYA işlemi (s-norm): en büyük üyelik derecesi."""
    return float(max(dereceler))


# --------------------------------------------------------------------------
# 3. ve 4. Çıkarım (kırpma) ve birleştirme
# --------------------------------------------------------------------------

def kes(uyelik, guc):
    """Çıkarım (Mamdani min): çıkış kümesini ateşleme gücünde kırpar."""
    return np.minimum(uyelik, guc)


def birlestir(kume_listesi):
    """Birleştirme: kırpılmış tüm çıkış kümelerinin nokta nokta max'ı."""
    return np.maximum.reduce([np.asarray(k, dtype=float) for k in kume_listesi])


# --------------------------------------------------------------------------
# 5. Durulaştırma
# --------------------------------------------------------------------------

def _kumulatif_alan(y, mu):
    """Soldan sağa birikimli alan (yamuk kuralı). Uzunluğu len(y) olur."""
    parca = (mu[1:] + mu[:-1]) / 2.0 * np.diff(y)
    return np.concatenate(([0.0], np.cumsum(parca)))


def _tepe_noktalari(y, mu, tolerans=1e-9):
    """Üyeliğin maksimum olduğu y değerleri."""
    return y[mu >= mu.max() - tolerans]


def merkez_ortalamasi(y, mu):
    """COA / Centroid: alanın ağırlık merkezinin y koordinatı.  integral(y*mu) / integral(mu)."""
    alan = _integral(mu, y)
    if alan == 0:
        raise ValueError("Birleşik kümenin alanı 0: hiçbir kural ateşlenmedi.")
    return float(_integral(y * mu, y) / alan)


def alan_ortayi(y, mu):
    """BOA / Bisector: alanı iki eşit parçaya bölen y değeri."""
    kum = _kumulatif_alan(y, mu)
    if kum[-1] == 0:
        raise ValueError("Birleşik kümenin alanı 0: hiçbir kural ateşlenmedi.")
    yari = kum[-1] / 2.0
    i = int(np.searchsorted(kum, yari))          # kum[i-1] < yari <= kum[i]
    if i == 0:
        return float(y[0])
    oran = (yari - kum[i - 1]) / (kum[i] - kum[i - 1])
    return float(y[i - 1] + oran * (y[i] - y[i - 1]))


def maksimumlar_ortalamasi(y, mu):
    """MOM: üyeliğin maksimum olduğu değerlerin ortalaması."""
    return float(np.mean(_tepe_noktalari(y, mu)))


def maksimumlarin_en_kucugu(y, mu):
    """SOM: üyeliğin maksimum olduğu değerlerin en küçüğü."""
    return float(np.min(_tepe_noktalari(y, mu)))


def maksimumlarin_en_buyugu(y, mu):
    """LOM: üyeliğin maksimum olduğu değerlerin en büyüğü."""
    return float(np.max(_tepe_noktalari(y, mu)))


def agirlikli_ortalama(agirliklar, degerler):
    """Ağırlıklı ortalama: sum(w_i * z_i) / sum(w_i)  (Sugeno tipinde kullanılır)."""
    w = np.asarray(agirliklar, dtype=float)
    z = np.asarray(degerler, dtype=float)
    return float(np.sum(w * z) / np.sum(w))


YONTEMLER = {
    "COA": merkez_ortalamasi,
    "BOA": alan_ortayi,
    "MOM": maksimumlar_ortalamasi,
    "SOM": maksimumlarin_en_kucugu,
    "LOM": maksimumlarin_en_buyugu,
}


def durulastir(y, mu, yontem="COA"):
    """Birleşik kümeyi seçilen yöntemle tek bir net değere çevirir."""
    return YONTEMLER[yontem](np.asarray(y, dtype=float), np.asarray(mu, dtype=float))


# --------------------------------------------------------------------------
# Tüm adımları zincirleyen genel Mamdani motoru
# --------------------------------------------------------------------------

def mamdani(girdi_kumeleri, cikti_kumeleri, kurallar, girdiler, y):
    """Tek çıkışlı Mamdani sistemini baştan sona çalıştırır.

    girdi_kumeleri : {"x": {"LOW": fonksiyon, ...}, "y": {...}}
    cikti_kumeleri : {"LOW": fonksiyon, ...}
    kurallar       : [{"kosullar": [("x", "LOW"), ("y", "MEDIUM")],
                       "islem": "VEYA", "sonuc": "HIGH"}, ...]
                     Tek koşullu kuralda "islem" yazmaya gerek yoktur.
    girdiler       : {"x": 55, "y": 45}
    y              : çıkış evreninin ızgarası (np.linspace ile)

    Döndürür (sözlük): "uyelikler" (bulanıklaştırma), "guclerin" (ateşleme
    güçleri), "kesilmis" (kırpılmış çıkış kümeleri), "birlesik" (birleşim).
    """
    y = np.asarray(y, dtype=float)

    # 1. Bulanıklaştırma: her girdinin her kümedeki üyelik derecesi
    uyelikler = {
        degisken: {ad: float(f(girdiler[degisken])) for ad, f in kumeler.items()}
        for degisken, kumeler in girdi_kumeleri.items()
    }

    guclerin, kesilmis = [], []
    for kural in kurallar:
        # 2. Kural değerlendirme: koşulları VE (min) / VEYA (max) ile birleştir
        dereceler = [uyelikler[d][k] for d, k in kural["kosullar"]]
        islem = kural.get("islem", "VE")
        guc = veya(*dereceler) if islem == "VEYA" else ve(*dereceler)
        guclerin.append(guc)

        # 3. Çıkarım: çıkış kümesini ateşleme gücünde kırp
        kesilmis.append(kes(cikti_kumeleri[kural["sonuc"]](y), guc))

    # 4. Birleştirme: kırpılmış kümelerin max'ı
    return {
        "uyelikler": uyelikler,
        "guclerin": guclerin,
        "kesilmis": kesilmis,
        "birlesik": birlestir(kesilmis),
    }
