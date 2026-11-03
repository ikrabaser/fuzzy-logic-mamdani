"""README'deki sayıların kodla tuttuğunu doğrular.

Çalıştır:  python test_el_hesaplari.py     (veya:  pytest)

scikit-fuzzy kuruluysa durulaştırma sonuçları o kütüphaneyle de çapraz kontrol edilir;
kurulu değilse o testler atlanır.
"""

import math

import numpy as np

from bulanik import (YONTEMLER, agirlikli_ortalama, birlestir, durulastir, gauss,
                     kes, mamdani, ucgen, ve, veya, yamuk)
from ornekler import (CIKTI_1, CIKTI_2, GIRDI_1, GIRDI_2, GIRDI_DEGERI_1,
                      GIRDI_DEGERI_2, KURALLAR_1, KURALLAR_2, Y1, Z2)
import fan_hizi_ornegi as fan

# --------------------------------------------------------------------------
# Üyelik fonksiyonları ve işlemler
# --------------------------------------------------------------------------


def test_yamuk_kenarlar_ve_tepe():
    assert yamuk(10, 10, 20, 30, 40) == 0
    assert yamuk(15, 10, 20, 30, 40) == 0.5
    assert yamuk(25, 10, 20, 30, 40) == 1
    assert yamuk(40, 10, 20, 30, 40) == 0
    assert yamuk(50, 10, 20, 30, 40) == 0


def test_yamuk_dik_omuz():
    # a == b: sol kenar dik; x = a'da değer 1
    assert yamuk(-10, -10, -10, -6, -3) == 1
    assert yamuk(-3.9, -10, -10, -6, -3) > 0
    # c == d: sağ kenar dik
    assert yamuk(100, 65, 80, 100, 100) == 1


def test_ucgen_tepe_ve_taraflar():
    assert ucgen(30, 10, 30, 50) == 1
    assert ucgen(20, 10, 30, 50) == 0.5
    assert ucgen(55, 10, 30, 50) == 0


def test_gauss_sigma_mu_sirasi():
    # gaussian(x; sigma, mu): x = mu'da 1; bir sigma uzakta exp(-0.5)
    assert gauss(50, 10, 50) == 1
    assert math.isclose(float(gauss(60, 10, 50)), math.exp(-0.5))


def test_ve_veya_kes_birlestir():
    assert ve(0.3, 0.8) == 0.3
    assert veya(0.3, 0.8) == 0.8
    assert list(kes(np.array([0.2, 0.9]), 0.5)) == [0.2, 0.5]
    assert list(birlestir([np.array([0.2, 0.9]), np.array([0.6, 0.1])])) == [0.6, 0.9]


def test_agirlikli_ortalama():
    assert math.isclose(agirlikli_ortalama([1, 3], [10, 20]), 17.5)


# --------------------------------------------------------------------------
# Örnek 1: tek girdili, 3 kural (x = -3,9)
# --------------------------------------------------------------------------


def test_ornek1_uyelikler_ve_gucler():
    s = mamdani(GIRDI_1, CIKTI_1, KURALLAR_1, GIRDI_DEGERI_1, Y1)
    u = s["uyelikler"]["x"]
    assert math.isclose(u["Small"], 0.3)
    assert math.isclose(u["Medium"], 0.7)
    assert u["Large"] == 0
    assert np.allclose(s["guclerin"], [0.3, 0.7, 0.0])


def test_ornek1_koselerin_yerleri():
    s = mamdani(GIRDI_1, CIKTI_1, KURALLAR_1, GIRDI_DEGERI_1, Y1)
    mu = s["birlesik"]
    for yk, beklenen in [(1.7518, 0.3), (2.1622, 0.7), (5.5956, 0.7), (7.0, 0.0)]:
        i = int(np.searchsorted(Y1, yk))
        assert abs(mu[i] - beklenen) < 1e-3, (yk, mu[i])


def test_ornek1_durulastirma_sonuclari():
    s = mamdani(GIRDI_1, CIKTI_1, KURALLAR_1, GIRDI_DEGERI_1, Y1)
    beklenen = {"COA": 3.6326, "BOA": 3.7080, "MOM": 3.8789, "SOM": 2.1622, "LOM": 5.5956}
    for yontem, deger in beklenen.items():
        assert abs(durulastir(Y1, s["birlesik"], yontem) - deger) < 1e-4, yontem


def test_ornek1_alan():
    s = mamdani(GIRDI_1, CIKTI_1, KURALLAR_1, GIRDI_DEGERI_1, Y1)
    alan = np.trapezoid(s["birlesik"], Y1) if hasattr(np, "trapezoid") else np.trapz(s["birlesik"], Y1)
    assert abs(alan - 3.6257) < 1e-4


def test_ornek1_x_taramasi_tam_kapsama():
    # x'in hiçbir değerinde tüm kurallar susmamalı (kapsama): her x için bir sonuç çıkar
    y = np.linspace(0, 10, 2001)
    for xv in np.linspace(-10, 10, 81):
        s = mamdani(GIRDI_1, CIKTI_1, KURALLAR_1, {"x": xv}, y)
        assert max(s["guclerin"]) > 0, xv


# --------------------------------------------------------------------------
# Örnek 2: iki girdili kontrolcü (x = 55, y = 45)
# --------------------------------------------------------------------------


def test_ornek2_uyelikler():
    s = mamdani(GIRDI_2, CIKTI_2, KURALLAR_2, GIRDI_DEGERI_2, Z2)
    ux, uy = s["uyelikler"]["x"], s["uyelikler"]["y"]
    assert abs(ux["LOW"] - 2.70e-7) < 1e-9
    assert ux["MEDIUM"] == 0
    assert ux["HIGH"] == 1
    assert abs(ux["VERY HIGH"] - 4.01e-5) < 1e-7
    assert uy["LOW"] == 0
    assert abs(uy["MEDIUM"] - 0.8825) < 1e-4
    assert uy["HIGH"] == 0


def test_ornek2_kural_gucleri():
    s = mamdani(GIRDI_2, CIKTI_2, KURALLAR_2, GIRDI_DEGERI_2, Z2)
    g = s["guclerin"]
    assert abs(g[0] - 0.8825) < 1e-4      # Kural 1: HIGH
    assert g[1] == 0                      # Kural 2: LOW
    assert g[2] == 0                      # Kural 3: MEDIUM
    assert abs(g[3] - 0.8825) < 1e-4      # Kural 4: MEDIUM


def test_ornek2_durulastirma_sonuclari():
    s = mamdani(GIRDI_2, CIKTI_2, KURALLAR_2, GIRDI_DEGERI_2, Z2)
    beklenen = {"COA": 69.572, "BOA": 71.416, "MOM": 80.714, "SOM": 47.650, "LOM": 100.0}
    for yontem, deger in beklenen.items():
        assert abs(durulastir(Z2, s["birlesik"], yontem) - deger) < 2e-3, yontem


def test_ornek2_mom_ile_som_lom_ortasi_ayni_degil():
    # Maksimumlar iki ayrı parçada olduğu için MOM != (SOM + LOM) / 2
    s = mamdani(GIRDI_2, CIKTI_2, KURALLAR_2, GIRDI_DEGERI_2, Z2)
    mom = durulastir(Z2, s["birlesik"], "MOM")
    orta = (durulastir(Z2, s["birlesik"], "SOM") + durulastir(Z2, s["birlesik"], "LOM")) / 2
    assert abs(mom - orta) > 5


# --------------------------------------------------------------------------
# Örnek 3: sıcaklık -> fan hızı, tek girdili, 2 kural (x = 28 ve x = 33)
# --------------------------------------------------------------------------


def _fan(x):
    return mamdani(fan.GIRDI, fan.CIKTI, fan.MOTOR_KURALLARI, {"sicaklik": x}, fan.Y)


def test_ornek3_uyelikler_ve_gucler():
    s = _fan(28.0)
    u = s["uyelikler"]["sicaklik"]
    assert math.isclose(u["Ilık"], 0.7)
    assert math.isclose(u["Sıcak"], 0.3)
    assert np.allclose(s["guclerin"], [0.7, 0.3])


def test_ornek3_uyelik_aciklamasi_kenari_dogru_secer():
    assert fan.uyelik(28, 15, 25, 35)[0] == 0.7      # tepenin sağı: alçalan kenar
    assert fan.uyelik(28, 25, 35, 45)[0] == 0.3      # tepenin solu: yükselen kenar
    assert fan.uyelik(25, 15, 25, 35)[0] == 1.0      # tam tepe
    assert fan.uyelik(10, 15, 25, 35)[0] == 0.0      # aralığın dışı


def test_ornek3_komsu_kumelerin_toplami_1():
    # 25 ile 35 arasında Ilık ve Sıcak birbirini tamamlar: w1 + w2 = 1
    for xv in np.linspace(25, 35, 41):
        s = _fan(float(xv))
        assert math.isclose(sum(s["guclerin"]), 1.0, abs_tol=1e-9), xv


def test_ornek3_koselerin_yerleri():
    mu = _fan(28.0)["birlesik"]
    for yk, beklenen in [(30, 0.0), (44, 0.7), (56, 0.7), (64, 0.3), (92.5, 0.3), (100, 0.0)]:
        i = int(np.searchsorted(fan.Y, yk))
        assert abs(mu[i] - beklenen) < 1e-3, (yk, mu[i])


def test_ornek3_durulastirma_sonuclari():
    beklenen = {
        28.0: {"COA": 60.2970, "BOA": 56.2705, "MOM": 50.0, "SOM": 44.0, "LOM": 56.0},
        33.0: {"COA": 70.2242, "BOA": 72.4375, "MOM": 75.0, "SOM": 70.0, "LOM": 80.0},
    }
    for x, sonuclar in beklenen.items():
        s = _fan(x)
        for yontem, deger in sonuclar.items():
            assert abs(durulastir(fan.Y, s["birlesik"], yontem) - deger) < 2e-3, (x, yontem)


def test_ornek3_alan():
    # Birleşik kümenin alanı: x = 28 için 26,975; x = 33 için 28,1
    for x, alan_beklenen in [(28.0, 26.975), (33.0, 28.1)]:
        mu = _fan(x)["birlesik"]
        alan = np.trapezoid(mu, fan.Y) if hasattr(np, "trapezoid") else np.trapz(mu, fan.Y)
        assert abs(alan - alan_beklenen) < 1e-3, x


def test_ornek3_elle_hesap_yardimcilari_motorla_ayni():
    # fan_hizi_ornegi.py'nin kapalı formüllü köşe/alan hesabı, genel motorla aynı sonucu vermeli
    for x, g1, g2 in [(28.0, 0.7, 0.3), (33.0, 0.2, 0.8)]:
        egriler = []
        for g, (a, b, c) in [(g1, fan.HIZ["Orta"]), (g2, fan.HIZ["Hızlı"])]:
            egriler.append([(a, 0.0), (a + g * (b - a), g), (c - g * (c - b), g), (c, 0.0)])
        V, _ = fan.zarf(egriler)
        alan = sum(fan.parca(m, k, p, q)[0] for p, q, m, k in fan.dogru_parcalari(V))
        mu = _fan(x)["birlesik"]
        motor = np.trapezoid(mu, fan.Y) if hasattr(np, "trapezoid") else np.trapz(mu, fan.Y)
        assert abs(alan - motor) < 1e-3, x


# --------------------------------------------------------------------------
# scikit-fuzzy ile çapraz kontrol (isteğe bağlı)
# --------------------------------------------------------------------------


def _skfuzzy_var_mi():
    try:
        import skfuzzy  # noqa: F401
        return True
    except Exception:
        return False


def test_skfuzzy_capraz_kontrol():
    if not _skfuzzy_var_mi():
        print("  (scikit-fuzzy kurulu değil, çapraz kontrol atlandı)")
        return
    import skfuzzy as fuzz

    for evren, girdi_k, cikti_k, kurallar, girdi in [
        (Y1, GIRDI_1, CIKTI_1, KURALLAR_1, GIRDI_DEGERI_1),
        (Z2, GIRDI_2, CIKTI_2, KURALLAR_2, GIRDI_DEGERI_2),
    ]:
        s = mamdani(girdi_k, cikti_k, kurallar, girdi, evren)
        kaba = evren[::100]                 # skfuzzy yavaş olmasın diye seyrelt
        mu_kaba = s["birlesik"][::100]
        for yontem, ad in [("COA", "centroid"), ("BOA", "bisector"),
                           ("MOM", "mom"), ("SOM", "som"), ("LOM", "lom")]:
            kendi = durulastir(evren, s["birlesik"], yontem)
            ref = fuzz.defuzz(kaba, mu_kaba, ad)
            assert abs(kendi - ref) < 5e-3, (yontem, kendi, ref)


if __name__ == "__main__":
    testler = [(ad, f) for ad, f in sorted(globals().items())
               if ad.startswith("test_") and callable(f)]
    for ad, f in testler:
        f()
        print("geçti:", ad)
    print(f"\n{len(testler)} test geçti.")
