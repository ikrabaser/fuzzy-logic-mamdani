"""alistirma.py için testler.

Çalıştır:  python test_alistirma.py     (veya:  pytest)
"""

import builtins
import contextlib
import io
import random

import alistirma


def test_sayi_oku_virgul_ve_nokta():
    assert alistirma.sayi_oku("0,7") == 0.7
    assert alistirma.sayi_oku(" 0.7 ") == 0.7
    assert alistirma.sayi_oku("") is None
    assert alistirma.sayi_oku("abc") is None


def test_soru_uret_ayni_seed_ayni_soru():
    a = [alistirma.soru_uret(random.Random(7)) for _ in range(3)]
    b = [alistirma.soru_uret(random.Random(7)) for _ in range(3)]
    assert a == b


def test_soru_uret_aralik_ve_30_haric():
    rng = random.Random(0)
    for _ in range(300):
        soru = alistirma.soru_uret(rng)
        assert 16 <= soru["x"] <= 44 and soru["x"] != 30
        assert soru["yontem"] in ("COA", "BOA", "MOM", "SOM", "LOM")


def test_soru_uret_yontem_sabitlenebilir():
    assert alistirma.soru_uret(random.Random(1), "BOA")["yontem"] == "BOA"


def test_cevap_hesapla_x28():
    c = alistirma.cevap_hesapla(28.0)
    assert abs(c["Ilık"] - 0.7) < 1e-9 and abs(c["Sıcak"] - 0.3) < 1e-9
    for yontem, deger in {"COA": 60.297, "BOA": 56.2705, "MOM": 50.0, "SOM": 44.0, "LOM": 56.0}.items():
        assert abs(c[yontem] - deger) < 2e-3, yontem


def test_dogru_mu_tolerans():
    assert alistirma.dogru_mu(60.3, 60.297, 0.1)
    assert not alistirma.dogru_mu(61.0, 60.297, 0.1)
    assert not alistirma.dogru_mu(None, 60.297, 0.1)


def _calistir(cevaplar):
    """Alıştırmayı hazır cevaplarla çalıştırır. Döndürür: (skor, ekran çıktısı)."""
    it = iter(cevaplar)
    eski = builtins.input
    builtins.input = lambda mesaj="": next(it)
    try:
        cikti = io.StringIO()
        with contextlib.redirect_stdout(cikti):
            skor = alistirma.alistirma_yap(soru_sayisi=1, yontem="COA", seed=3)
    finally:
        builtins.input = eski
    return skor, cikti.getvalue()


def test_alistirma_butun_cevaplar_dogru():
    x = alistirma.soru_uret(random.Random(3), "COA")["x"]
    c = alistirma.cevap_hesapla(x)
    virgullu = lambda v: f"{v:.3f}".replace(".", ",")      # virgüllü giriş de kabul edilmeli
    skor, cikti = _calistir([virgullu(c["Ilık"]), virgullu(c["Sıcak"]), virgullu(c["COA"])])
    assert skor == (3, 3)
    assert "Hepsi doğru." in cikti


def test_alistirma_bos_cevaplarda_cozum_ozeti_gosterilir():
    skor, cikti = _calistir(["", "", ""])
    assert skor == (0, 3)
    assert "Çözüm özeti" in cikti and "Birleşik küme köşeleri" in cikti


def test_alistirma_girdi_biterse_hata_vermez():
    # EOF -> boş cevap (input() EOFError)
    def bitir(mesaj=""):
        raise EOFError
    eski = builtins.input
    builtins.input = bitir
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            skor = alistirma.alistirma_yap(soru_sayisi=1, yontem="SOM", seed=1)
    finally:
        builtins.input = eski
    assert skor == (0, 3)


if __name__ == "__main__":
    testler = [(ad, f) for ad, f in sorted(globals().items())
               if ad.startswith("test_") and callable(f)]
    for ad, f in testler:
        f()
        print("geçti:", ad)
    print(f"\n{len(testler)} test geçti.")
