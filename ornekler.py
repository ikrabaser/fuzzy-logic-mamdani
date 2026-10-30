"""İki örnek problemin tanımları (üyelik fonksiyonları ve kurallar).

Her şey tek yerde durur; el hesabı scriptleri, görseller ve testler buradan okur.

ÖRNEK 1  Tek girdili (SISO) Mamdani modeli, 3 kural      x = -3,9
ÖRNEK 2  İki girdili kontrolcü, 4 kural                  x = 55, y = 45

Örnek 1'in girdi kümelerinin kesin parametreleri kaynak örnekte yazmıyor, yalnızca
şekil var. Şekilden okunan şu iki değeri veren yamuklar seçildi:
    x = -3,9  ->  Small = 0,3 ve Medium = 0,7
Çıkış kümelerinin sağ/sol kenarları ise kaynaktaki birleşik şeklin köşe
noktalarından geri çıkarıldı: (1,7518 ; 0,3), (2,1622 ; 0,7), (5,5956 ; 0,7), (7 ; 0).
"""

from functools import partial

import numpy as np

from bulanik import gauss, ucgen, yamuk

# ==========================================================================
# ÖRNEK 1: tek girdili, 3 kurallı Mamdani modeli
# ==========================================================================

# Girdi evreni X = [-10, 10], çıkış evreni Y = [0, 10]
X1 = np.linspace(-10, 10, 200_001)
Y1 = np.linspace(0, 10, 1_000_001)

GIRDI_1 = {
    "x": {
        "Small": partial(yamuk, a=-10, b=-10, c=-6, d=-3),
        "Medium": partial(yamuk, a=-6, b=-3, c=3, d=6),
        "Large": partial(yamuk, a=3, b=6, c=10, d=10),
    }
}

CIKTI_1 = {
    "Small": partial(yamuk, a=0, b=0, c=2, d=4),
    "Medium": partial(yamuk, a=1.444, b=2.47, c=4.9937, d=7.0),
    "Large": partial(yamuk, a=6, b=8, c=10, d=10),
}

KURALLAR_1 = [
    {"kosullar": [("x", "Small")], "sonuc": "Small"},     # Kural 1
    {"kosullar": [("x", "Medium")], "sonuc": "Medium"},   # Kural 2
    {"kosullar": [("x", "Large")], "sonuc": "Large"},     # Kural 3
]

GIRDI_DEGERI_1 = {"x": -3.9}

# ==========================================================================
# ÖRNEK 2: iki girdili kontrolcü, 4 kural
# ==========================================================================

# Üç değişkenin de evreni [0, 100]
X2 = np.linspace(0, 100, 1_000_001)
Z2 = np.linspace(0, 100, 1_000_001)

# gauss(x, sigma, mu): gaussian(x; 10, 0) -> sigma = 10, mu = 0
GIRDI_2 = {
    "x": {
        "LOW": partial(gauss, sigma=10, mu=0),
        "MEDIUM": partial(ucgen, a=10, b=30, c=50),
        "HIGH": partial(yamuk, a=30, b=50, c=70, d=90),
        "VERY HIGH": partial(gauss, sigma=10, mu=100),
    },
    "y": {
        "LOW": partial(ucgen, a=0, b=0, c=40),
        "MEDIUM": partial(gauss, sigma=10, mu=50),
        "HIGH": partial(yamuk, a=65, b=80, c=100, d=100),
    },
}

CIKTI_2 = {
    "LOW": partial(yamuk, a=0, b=0, c=20, d=40),
    "MEDIUM": partial(ucgen, a=30, b=50, c=80),
    "HIGH": partial(yamuk, a=50, b=80, c=100, d=100),
}

KURALLAR_2 = [
    {"kosullar": [("x", "VERY HIGH"), ("y", "MEDIUM")], "islem": "VEYA", "sonuc": "HIGH"},
    {"kosullar": [("x", "MEDIUM"), ("y", "LOW")], "islem": "VEYA", "sonuc": "LOW"},
    {"kosullar": [("x", "MEDIUM"), ("y", "HIGH")], "islem": "VEYA", "sonuc": "MEDIUM"},
    {"kosullar": [("x", "LOW"), ("y", "MEDIUM")], "islem": "VEYA", "sonuc": "MEDIUM"},
]

GIRDI_DEGERI_2 = {"x": 55.0, "y": 45.0}
