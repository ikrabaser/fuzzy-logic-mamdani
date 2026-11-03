"""sugeno_ornegi.py için testler.

Çalıştır:  python test_sugeno.py     (veya:  pytest)
"""

import math

import fan_hizi_ornegi as fan
from bulanik import agirlikli_ortalama, mamdani
from sugeno_ornegi import SABITLER, mamdani_coa, sugeno


def test_sabitler_cikis_kumelerinin_tepesi():
    assert SABITLER == [50, 75]


def test_sugeno_sonuclari():
    beklenen = {20.0: 50.0, 25.0: 50.0, 28.0: 57.5, 30.0: 62.5, 33.0: 70.0, 35.0: 75.0, 40.0: 75.0}
    for x, z in beklenen.items():
        assert math.isclose(sugeno(x)[2], z, abs_tol=1e-9), x


def test_sugeno_agirlikli_ortalamadir():
    guc, sabit, z = sugeno(28.0)
    assert math.isclose(z, agirlikli_ortalama(guc, sabit))
    assert math.isclose(z, (0.7 * 50 + 0.3 * 75) / (0.7 + 0.3))


def test_sugeno_gucleri_mamdani_motoruyla_ayni():
    for x in [18.0, 28.0, 33.0, 42.0]:
        s = mamdani(fan.GIRDI, fan.CIKTI, fan.MOTOR_KURALLARI, {"sicaklik": x}, fan.Y)
        guc = sugeno(x)[0]
        assert all(abs(a - b) < 1e-9 for a, b in zip(guc, s["guclerin"])), x


def test_sugeno_hicbir_kural_ateslenmezse_hata():
    try:
        sugeno(10.0)
    except ValueError:
        return
    raise AssertionError("x = 10'da ValueError beklenirdi")


def test_tek_kural_ateslenince_sugeno_ve_mamdani_ayni():
    for x in [18.0, 22.0, 25.0, 35.0, 38.0, 42.0]:
        assert abs(sugeno(x)[2] - mamdani_coa(x)) < 1e-3, x


def test_iki_kural_ateslenince_mamdani_biraz_daha_yuksek():
    # Hızlı kümesi daha geniş olduğu için COA, Sugeno'dan büyük çıkar (25 < x < 35)
    for x in [26.0, 28.0, 30.0, 33.0]:
        assert mamdani_coa(x) > sugeno(x)[2], x


if __name__ == "__main__":
    testler = [(ad, f) for ad, f in sorted(globals().items())
               if ad.startswith("test_") and callable(f)]
    for ad, f in testler:
        f()
        print("geçti:", ad)
    print(f"\n{len(testler)} test geçti.")
