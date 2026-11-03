"""gorseller/ klasöründeki PNG'leri üretir.

Çalıştır:  python gorseller_uret.py

Renkler: kümeler için sırayla mavi, turuncu, yeşil-mavi, sarı (kümenin kimliği);
birleşik küme ve durulaştırma çizgileri nötr gri/koyu tonlarda.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from bulanik import YONTEMLER, durulastir, mamdani
from ornekler import (CIKTI_1, CIKTI_2, GIRDI_1, GIRDI_2, GIRDI_DEGERI_1,
                      GIRDI_DEGERI_2, KURALLAR_1, KURALLAR_2, Y1, Z2)
from fan_hizi_ornegi import CIKTI as CIKTI_3, GIRDI as GIRDI_3
from fan_hizi_ornegi import MOTOR_KURALLARI as KURALLAR_3, Y as Y3

KLASOR = "gorseller"
os.makedirs(KLASOR, exist_ok=True)

YUZEY = "#fcfcfb"
YAZI = "#0b0b0b"
YAZI_2 = "#52514e"
IZGARA = "#e4e3df"
RENK = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]   # küme 1, 2, 3, 4
BIRLESIK = "#52514e"

plt.rcParams.update({
    "figure.facecolor": YUZEY, "axes.facecolor": YUZEY, "savefig.facecolor": YUZEY,
    "axes.edgecolor": IZGARA, "axes.labelcolor": YAZI_2, "text.color": YAZI,
    "xtick.color": YAZI_2, "ytick.color": YAZI_2, "axes.grid": True,
    "grid.color": IZGARA, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 10, "axes.titlesize": 11,
    "axes.titleweight": "bold", "axes.titlelocation": "left",
})


def kaydet(fig, ad):
    yol = os.path.join(KLASOR, ad)
    fig.savefig(yol, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print("yazıldı:", yol)


def kumeleri_ciz(ax, kumeler, evren, renkler=None, kalin=1.8):
    """Her kümeyi kendi renginde çizer ve kümenin adını çizginin yanına yazar."""
    for i, (ad, f) in enumerate(kumeler.items()):
        mu = f(evren)
        ax.plot(evren, mu, color=RENK[i] if renkler is None else renkler[i], lw=kalin)


def etiket_yaz(ax, kumeler, evren, konumlar):
    """Doğrudan etiket: kümenin adı, belirtilen x konumunda çizginin üstüne yazılır."""
    for i, ((ad, f), xk) in enumerate(zip(kumeler.items(), konumlar)):
        ax.text(xk, 1.07, ad, color=RENK[i], fontsize=9,
                fontweight="bold", ha="center", va="bottom")


def eksen_duzenle(ax, xlabel, ylabel="Üyelik derecesi"):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_ylim(-0.03, 1.28)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])


# ==========================================================================
# 01  Örnek 1: üyelik fonksiyonları
# ==========================================================================
x_cizim = np.linspace(-10, 10, 2001)
y_cizim = np.linspace(0, 10, 2001)
x1 = GIRDI_DEGERI_1["x"]
sonuc1 = mamdani(GIRDI_1, CIKTI_1, KURALLAR_1, GIRDI_DEGERI_1, Y1)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
kumeleri_ciz(a1, GIRDI_1["x"], x_cizim)
etiket_yaz(a1, GIRDI_1["x"], x_cizim, [-8.2, 0, 8.2])
a1.axvline(x1, color=YAZI, lw=1, ls="--")
for ad, mu in sonuc1["uyelikler"]["x"].items():
    if mu > 0:
        a1.plot([x1], [mu], "o", color=YAZI, ms=6, mec=YUZEY, mew=1.5)
        a1.text(x1 + 0.25, mu, f"{ad} = {mu:.1f}", fontsize=9, va="center")
a1.set_title("Girdi kümeleri ve x = -3,9")
eksen_duzenle(a1, "x")
kumeleri_ciz(a2, CIKTI_1, y_cizim)
etiket_yaz(a2, CIKTI_1, y_cizim, [1.0, 4.2, 8.5])
a2.set_title("Çıkış kümeleri")
eksen_duzenle(a2, "y")
kaydet(fig, "01_ornek1_uyelik_fonksiyonlari.png")

# ==========================================================================
# 02  Örnek 1: kırpma ve birleştirme
# ==========================================================================
fig = plt.figure(figsize=(11, 5.2))
gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.3], hspace=0.55, wspace=0.22)
adlar = list(CIKTI_1)
for i in range(2):
    ax = fig.add_subplot(gs[i, 0])
    f = CIKTI_1[adlar[i]]
    guc = sonuc1["guclerin"][i]
    ax.plot(y_cizim, f(y_cizim), color=RENK[i], lw=1.2, alpha=0.45)
    kesik = np.minimum(f(y_cizim), guc)
    ax.fill_between(y_cizim, kesik, color=RENK[i], alpha=0.35, lw=0)
    ax.plot(y_cizim, kesik, color=RENK[i], lw=2)
    ax.axhline(guc, color=YAZI, lw=1, ls="--")
    ax.text(9.9, guc + 0.04, f"w{i + 1} = {guc:.1f}", ha="right", fontsize=9)
    ax.set_title(f"Kural {i + 1}: IF x is {adlar[i]} THEN y is {adlar[i]}")
    eksen_duzenle(ax, "y")
ax = fig.add_subplot(gs[:, 1])
ax.fill_between(Y1[::500], sonuc1["birlesik"][::500], color=BIRLESIK, alpha=0.25, lw=0)
ax.plot(Y1[::500], sonuc1["birlesik"][::500], color=BIRLESIK, lw=2)
for i in range(2):
    ax.plot(y_cizim, np.minimum(CIKTI_1[adlar[i]](y_cizim), sonuc1["guclerin"][i]),
            color=RENK[i], lw=1.2, ls=":")
for xk, yk in [(1.7518, 0.3), (2.1622, 0.7), (5.5956, 0.7), (7.0, 0.0)]:
    ax.plot([xk], [yk], "o", color=YAZI, ms=5, mec=YUZEY, mew=1.2)
    ax.text(xk, yk + 0.05, f"({xk:g} ; {yk:g})", fontsize=8.5, ha="center")
ax.set_title("Birleştirme: iki kırpılmış kümenin max'ı")
eksen_duzenle(ax, "y")
kaydet(fig, "02_ornek1_kirpma_ve_birlestirme.png")


# ==========================================================================
# Durulaştırma çizgilerini etiketleyen ortak çizim
# ==========================================================================
def durulastirma_ciz(ax, evren, birlesik, etiket_satirlari, tavan):
    """etiket_satirlari: {yontem: (satir, hizalama)}"""
    ax.fill_between(evren[::500], birlesik[::500], color=BIRLESIK, alpha=0.22, lw=0)
    ax.plot(evren[::500], birlesik[::500], color=BIRLESIK, lw=2)
    degerler = {m: durulastir(evren, birlesik, m) for m in YONTEMLER}
    stil = {"COA": "-", "BOA": "--", "MOM": "-.", "SOM": ":", "LOM": ":"}
    for m, v in degerler.items():
        satir, hiza = etiket_satirlari[m]
        ust = tavan - 0.16 * satir
        ax.plot([v, v], [0, ust - 0.015], color=YAZI, lw=1.1, ls=stil[m])
        ax.text(v + (0.4 if hiza == "left" else -0.4) * tavan_olcek(ax), ust,
                f"{m} {v:.4f}", fontsize=9, ha=hiza, va="center", fontweight="bold")
    return degerler


def tavan_olcek(ax):
    """Metni çizgiden küçük bir mesafe uzaklaştırmak için x ekseninin yüzde biri."""
    a, b = ax.get_xlim()
    return (b - a) / 40.0


# ==========================================================================
# 03  Örnek 1: durulaştırma
# ==========================================================================
fig, ax = plt.subplots(figsize=(10, 4))
ax.set_xlim(0, 10)
ax.set_ylim(-0.03, 1.28)
satirlar = {"SOM": (0, "right"), "COA": (0, "right"), "BOA": (0, "left"),
            "MOM": (1, "left"), "LOM": (0, "left")}
durulastirma_ciz(ax, Y1, sonuc1["birlesik"], satirlar, 1.2)
ax.set_title("Örnek 1: aynı birleşik küme, beş durulaştırma yöntemi")
ax.set_xlabel("y")
ax.set_ylabel("Üyelik derecesi")
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
kaydet(fig, "03_ornek1_durulastirma.png")

# ==========================================================================
# 04  Örnek 1: girdi-çıktı eğrisi (x'in her değeri için COA)
# ==========================================================================
y_kaba = np.linspace(0, 10, 20_001)
xs = np.linspace(-10, 10, 201)
ciktilar = []
for xv in xs:
    s = mamdani(GIRDI_1, CIKTI_1, KURALLAR_1, {"x": xv}, y_kaba)
    ciktilar.append(durulastir(y_kaba, s["birlesik"], "COA"))
fig, ax = plt.subplots(figsize=(7.5, 4))
ax.plot(xs, ciktilar, color=RENK[0], lw=2)
nokta = durulastir(Y1, sonuc1["birlesik"], "COA")
ax.plot([x1], [nokta], "o", color=YAZI, ms=7, mec=YUZEY, mew=1.5)
ax.annotate(f"x = {x1}  ->  y = {nokta:.4f}", (x1, nokta), xytext=(-9.3, 7.2),
            fontsize=9.5, arrowprops=dict(arrowstyle="-", color=YAZI_2, lw=0.8))
ax.set_title("Örnek 1: x'in her değeri için net çıkış (COA)")
ax.set_xlabel("x")
ax.set_ylabel("y")
kaydet(fig, "04_ornek1_girdi_cikti_egrisi.png")

# ==========================================================================
# 05  Örnek 2: üyelik fonksiyonları
# ==========================================================================
sonuc2 = mamdani(GIRDI_2, CIKTI_2, KURALLAR_2, GIRDI_DEGERI_2, Z2)
v = np.linspace(0, 100, 2001)
fig, (b1, b2, b3) = plt.subplots(1, 3, figsize=(14, 3.8))

kumeleri_ciz(b1, GIRDI_2["x"], v)
etiket_yaz(b1, GIRDI_2["x"], v, [8, 30, 64, 88])
b1.axvline(55, color=YAZI, lw=1, ls="--")
b1.plot([55], [1.0], "o", color=YAZI, ms=6, mec=YUZEY, mew=1.5)
b1.set_title("Girdi x")
eksen_duzenle(b1, "x = 55:  HIGH = 1,  LOW = 2,7e-7,  VERY HIGH = 4,0e-5")

kumeleri_ciz(b2, GIRDI_2["y"], v)
etiket_yaz(b2, GIRDI_2["y"], v, [10, 60, 90])
b2.axvline(45, color=YAZI, lw=1, ls="--")
mu_y = sonuc2["uyelikler"]["y"]["MEDIUM"]
b2.plot([45], [mu_y], "o", color=YAZI, ms=6, mec=YUZEY, mew=1.5)
b2.set_title("Girdi y")
eksen_duzenle(b2, f"y = 45:  MEDIUM = {mu_y:.4f},  LOW = 0,  HIGH = 0")

kumeleri_ciz(b3, CIKTI_2, v)
etiket_yaz(b3, CIKTI_2, v, [10, 50, 90])
b3.set_title("Çıkış z")
eksen_duzenle(b3, "z")
kaydet(fig, "05_ornek2_uyelik_fonksiyonlari.png")

# ==========================================================================
# 06  Örnek 2: kırpma, birleştirme ve durulaştırma
# ==========================================================================
w = sonuc2["guclerin"][0]
fig, (c1, c2) = plt.subplots(1, 2, figsize=(14, 4.2), gridspec_kw={"width_ratios": [1, 1.5]})
for ad, f, i in [("MEDIUM", CIKTI_2["MEDIUM"], 1), ("HIGH", CIKTI_2["HIGH"], 2)]:
    c1.plot(v, f(v), color=RENK[i], lw=1.2, alpha=0.45)
    kesik = np.minimum(f(v), w)
    c1.fill_between(v, kesik, color=RENK[i], alpha=0.35, lw=0)
    c1.plot(v, kesik, color=RENK[i], lw=2)
c1.axhline(w, color=YAZI, lw=1, ls="--")
c1.text(2, w + 0.025, f"w1 = w4 = {w:.4f}", fontsize=9)
c1.text(30, 1.07, "Kural 4: MEDIUM", color=RENK[1], fontsize=9, fontweight="bold", ha="center")
c1.text(86, 1.07, "Kural 1: HIGH", color=RENK[2], fontsize=9, fontweight="bold", ha="center")
c1.set_title("Kırpma: Kural 1 ve Kural 4 (2 ve 3'ün gücü 0)")
eksen_duzenle(c1, "z")

c2.set_xlim(0, 100)
c2.set_ylim(-0.03, 1.5)
satirlar2 = {"SOM": (0, "right"), "COA": (0, "right"), "BOA": (0, "left"),
             "MOM": (1, "left"), "LOM": (2, "right")}
durulastirma_ciz(c2, Z2, sonuc2["birlesik"], satirlar2, 1.38)
c2.set_title("Birleştirme ve durulaştırma")
c2.set_xlabel("z")
c2.set_ylabel("Üyelik derecesi")
c2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
kaydet(fig, "06_ornek2_birlestirme_ve_durulastirma.png")


# ==========================================================================
# 07  Örnek 3: üyelik fonksiyonları (sıcaklık -> fan hızı, x = 28)
# ==========================================================================
x3 = 28.0
sonuc3 = mamdani(GIRDI_3, CIKTI_3, KURALLAR_3, {"sicaklik": x3}, Y3)
s_cizim = np.linspace(0, 50, 2001)
h_cizim = np.linspace(0, 100, 2001)

fig, (d1, d2) = plt.subplots(1, 2, figsize=(11, 3.8))
kumeleri_ciz(d1, GIRDI_3["sicaklik"], s_cizim)
etiket_yaz(d1, GIRDI_3["sicaklik"], s_cizim, [22, 38])
d1.axvline(x3, color=YAZI, lw=1, ls="--")
for ad, mu in sonuc3["uyelikler"]["sicaklik"].items():
    if mu > 0:
        d1.plot([x3], [mu], "o", color=YAZI, ms=6, mec=YUZEY, mew=1.5)
        d1.text(x3 + 0.8, mu, f"{ad} = {mu:.1f}", fontsize=9, va="center")
d1.set_title("Girdi kümeleri ve x = 28 °C")
eksen_duzenle(d1, "sıcaklık (°C)")
kumeleri_ciz(d2, CIKTI_3, h_cizim)
etiket_yaz(d2, CIKTI_3, h_cizim, [50, 75])
d2.set_title("Çıkış kümeleri")
eksen_duzenle(d2, "fan hızı (y)")
kaydet(fig, "07_ornek3_uyelik_fonksiyonlari.png")

# ==========================================================================
# 08  Örnek 3: kırpma ve birleştirme
# ==========================================================================
fig = plt.figure(figsize=(11, 5.2))
gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.3], hspace=0.55, wspace=0.22)
adlar3 = list(CIKTI_3)
for i in range(2):
    ax = fig.add_subplot(gs[i, 0])
    f = CIKTI_3[adlar3[i]]
    guc = sonuc3["guclerin"][i]
    ax.plot(h_cizim, f(h_cizim), color=RENK[i], lw=1.2, alpha=0.45)
    kesik = np.minimum(f(h_cizim), guc)
    ax.fill_between(h_cizim, kesik, color=RENK[i], alpha=0.35, lw=0)
    ax.plot(h_cizim, kesik, color=RENK[i], lw=2)
    ax.axhline(guc, color=YAZI, lw=1, ls="--")
    ax.text(99, guc + 0.04, f"w{i + 1} = {guc:.1f}", ha="right", fontsize=9)
    kosul = KURALLAR_3[i]["kosullar"][0][1]
    ax.set_title(f"Kural {i + 1}: IF {kosul} THEN {KURALLAR_3[i]['sonuc']}")
    eksen_duzenle(ax, "fan hızı (y)")
ax = fig.add_subplot(gs[:, 1])
ax.fill_between(Y3[::500], sonuc3["birlesik"][::500], color=BIRLESIK, alpha=0.25, lw=0)
ax.plot(Y3[::500], sonuc3["birlesik"][::500], color=BIRLESIK, lw=2)
for i in range(2):
    ax.plot(h_cizim, np.minimum(CIKTI_3[adlar3[i]](h_cizim), sonuc3["guclerin"][i]),
            color=RENK[i], lw=1.2, ls=":")
for xk, yk, hiza in [(44, 0.7, "right"), (56, 0.7, "left"), (64, 0.3, "left"), (92.5, 0.3, "center")]:
    ax.plot([xk], [yk], "o", color=YAZI, ms=5, mec=YUZEY, mew=1.2)
    kayma = {"left": 1, "right": -1, "center": 0}[hiza]
    ax.text(xk + kayma, yk + 0.05, f"({xk:g} ; {yk:g})", fontsize=8.5, ha=hiza)
ax.set_title("Birleştirme: iki kırpılmış kümenin max'ı")
eksen_duzenle(ax, "fan hızı (y)")
kaydet(fig, "08_ornek3_kirpma_ve_birlestirme.png")

# ==========================================================================
# 09  Örnek 3: durulaştırma (x = 28)
# ==========================================================================
fig, ax = plt.subplots(figsize=(10, 4))
ax.set_xlim(20, 105)
ax.set_ylim(-0.03, 1.28)
satirlar3 = {"LOM": (0, "right"), "BOA": (0, "left"), "MOM": (1, "right"),
             "COA": (1, "left"), "SOM": (2, "right")}
durulastirma_ciz(ax, Y3, sonuc3["birlesik"], satirlar3, 1.2)
ax.set_title("Örnek 3: aynı birleşik küme, beş durulaştırma yöntemi (x = 28 °C)")
ax.set_xlabel("fan hızı (y)")
ax.set_ylabel("Üyelik derecesi")
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
kaydet(fig, "09_ornek3_durulastirma.png")

# ==========================================================================
# 10  Örnek 3: x'in her değeri için beş yöntemin çıkışı
# ==========================================================================
y_kaba3 = np.linspace(0, 100, 10_001)
xs3 = np.linspace(16, 44, 113)
egriler3 = {m: [] for m in YONTEMLER}
for xv in xs3:
    s = mamdani(GIRDI_3, CIKTI_3, KURALLAR_3, {"sicaklik": xv}, y_kaba3)
    for m in YONTEMLER:
        deger = durulastir(y_kaba3, s["birlesik"], m)
        # x = 30'da iki kuralın gücü eşit: maksimum yöntemleri burada bir kümeden
        # ötekine atlar. Atlama çizgisi çizilmesin diye o noktada çizgi kesilir.
        egriler3[m].append(np.nan if (m in ("MOM", "SOM", "LOM") and xv == 30) else deger)

fig, ax = plt.subplots(figsize=(9, 4.6))
stil3 = {"COA": ("-", RENK[0]), "BOA": ("--", RENK[1]), "MOM": ("-.", RENK[2]),
         "SOM": (":", RENK[3]), "LOM": (":", YAZI)}
for m, (ls, renk) in stil3.items():
    ax.plot(xs3, egriler3[m], ls=ls, color=renk, lw=2, label=m)
ax.axvline(x3, color=YAZI_2, lw=1, ls="--")
ax.text(x3 - 0.3, 96, "x = 28", fontsize=9, color=YAZI_2, ha="right")
ax.set_title("Örnek 3: x'in her değeri için net çıkış, beş yöntem")
ax.set_xlabel("sıcaklık x (°C)")
ax.set_ylabel("fan hızı (y)")
ax.legend(loc="lower right", ncol=5, frameon=False, fontsize=9)
kaydet(fig, "10_ornek3_yontem_karsilastirma.png")
