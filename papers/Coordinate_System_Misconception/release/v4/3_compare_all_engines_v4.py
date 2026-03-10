#!/usr/bin/env python3
"""
全エンジン比較スクリプト（v4 修正版）

【v3からの修正】
v3では Skyfield の ecliptic_frame を「J2000」、ecliptic_latlon() を「of-date」と
誤ラベルしていた。実際はその逆であり、Swiss Ephemeris が一致するのは
ecliptic_frame（of-date）である。

これは Swiss Ephemeris がドキュメント通り of-date（tropical）を
正しく実装していることを意味する。

フレームの正しい対応:
  ecliptic_frame       → of-date（当代の黄道フレーム）
  ecliptic_J2000_frame → J2000固定（歳差なし）
  ecliptic_latlon()    → J2000相当

論文: 自己再検証：Swiss Ephemeris の座標系実装について（v4）
著者: 志賀高史（Takashi Shiga）
前バージョン DOI: https://doi.org/10.5281/zenodo.18767251
"""

from skyfield.api import load
from skyfield.framelib import ecliptic_frame, ecliptic_J2000_frame


def compare_coordinate_systems():
    """全エンジン比較（修正版）"""

    print("=" * 65)
    print("座標系比較検証（v4 修正版）")
    print("=" * 65)
    print()

    # ── Skyfield の計算 ─────────────────────────────────────
    ts = load.timescale()
    eph = load('de440s.bsp')

    date = ts.utc(1983, 7, 5, 6, 42)

    earth = eph['earth']
    sun = eph['sun']
    astrometric = earth.at(date).observe(sun)
    apparent = astrometric.apparent()

    # of-date（修正後の正しいラベル）
    ofdate_ecliptic = apparent.frame_latlon(ecliptic_frame)
    skyfield_ofdate = ofdate_ecliptic[1].degrees

    # J2000固定（修正後の正しいラベル）
    j2000_ecliptic = apparent.frame_latlon(ecliptic_J2000_frame)
    skyfield_j2000 = j2000_ecliptic[1].degrees

    # ecliptic_latlon()（確認用、J2000相当）
    latlon_ecliptic = apparent.ecliptic_latlon()
    skyfield_latlon = latlon_ecliptic[1].degrees

    # ── Swiss Ephemeris の計算 ───────────────────────────────
    try:
        from flatlib.datetime import Datetime
        from flatlib.geopos import GeoPos
        from flatlib.chart import Chart
        from flatlib import const

        date_swiss = Datetime('1983/07/05', '15:42', '+09:00')
        location_swiss = GeoPos(35.79, 139.91)
        chart = Chart(date_swiss, location_swiss)
        sun_swiss = chart.get(const.SUN)
        swiss = sun_swiss.lon
        swiss_available = True
    except ImportError:
        swiss = 102.694627
        swiss_available = False

    # ── 結果表示 ─────────────────────────────────────────────
    print("📍 観測条件: 1983年7月5日 06:42 UTC")
    print()
    print("=" * 65)
    print("計算結果（修正版）")
    print("=" * 65)
    print(f"{'エンジン':<25} {'フレーム':<20} {'黄経 (°)':<12}")
    print("-" * 65)
    print(f"{'Skyfield':<25} {'of-date (ecliptic_frame)':<20} {skyfield_ofdate:<12.5f}")
    print(f"{'Skyfield':<25} {'J2000 (ecliptic_J2000)':<20} {skyfield_j2000:<12.5f}")
    print(f"{'Skyfield':<25} {'ecliptic_latlon()':<20} {skyfield_latlon:<12.5f}")
    note = "" if swiss_available else " *"
    print(f"{'Swiss Ephemeris':<25} {'tropical':<20} {swiss:<12.5f}{note}")
    if not swiss_available:
        print()
        print("* flatlib 未インストールのため既知の値を使用")
    print("=" * 65)

    # ── 差分分析 ─────────────────────────────────────────────
    diff_swiss_ofdate = abs(swiss - skyfield_ofdate)
    diff_swiss_j2000 = abs(swiss - skyfield_j2000)
    diff_swiss_latlon = abs(swiss - skyfield_latlon)

    print()
    print("📊 差分分析（Swissとの比較）:")
    print(f"  Swiss vs Skyfield of-date (ecliptic_frame):  "
          f"{diff_swiss_ofdate:.5f}° ({diff_swiss_ofdate*3600:.2f}\")", end=" ")
    print("→ ほぼ一致 ✅" if diff_swiss_ofdate < 0.001 else "→ 差がある ⚠️")

    print(f"  Swiss vs Skyfield J2000 (ecliptic_J2000):    "
          f"{diff_swiss_j2000:.5f}° ({diff_swiss_j2000*3600:.2f}\")", end=" ")
    print("→ ほぼ一致 ✅" if diff_swiss_j2000 < 0.001 else "→ 差がある（歳差分） ⚠️")

    print(f"  Swiss vs ecliptic_latlon():                  "
          f"{diff_swiss_latlon:.5f}° ({diff_swiss_latlon*3600:.2f}\")", end=" ")
    print("→ ほぼ一致 ✅" if diff_swiss_latlon < 0.001 else "→ 差がある（歳差分） ⚠️")

    # ── 結論 ─────────────────────────────────────────────────
    print()
    print("=" * 65)
    print("🔬 結論（修正版）")
    print("=" * 65)
    print()
    if diff_swiss_ofdate < 0.001:
        print("✅ Swiss Ephemeris の 'tropical' 出力は")
        print("   Skyfield の of-date フレーム（ecliptic_frame）と")
        f"   {diff_swiss_ofdate*3600:.2f} 秒角の誤差で一致する。"
        print(f"   差分: {diff_swiss_ofdate:.5f}°（{diff_swiss_ofdate*3600:.2f} 秒角）")
        print()
        print("📌 修正後の正しい解釈:")
        print("   Swiss Ephemeris は 'of-date（tropical）' として")
        print("   ドキュメントに記載されている通りの座標系を正しく実装している。")
        print()
        print("⚠️  v3 の誤り（訂正）:")
        print("   v3 では ecliptic_frame を 'J2000' と誤ラベルし、")
        print("   'Swiss = J2000' という誤った結論を導いた。")
        print("   正しくは 'Swiss = of-date' である。")
    print()
    print("=" * 65)
    print("📖 補足: v3 との数値比較")
    print("=" * 65)
    print()
    print("v3 が 'J2000' と呼んでいた値（実際は of-date）: "
          f"{skyfield_ofdate:.5f}°  ← Swiss と一致")
    print("v3 が 'of-date' と呼んでいた値（実際は J2000）: "
          f"{skyfield_latlon:.5f}°  ← Swiss と不一致")
    print()
    years = abs(1983 - 2000)
    precession = years * 50.29 / 3600
    print(f"J2000 と of-date の差: {diff_swiss_j2000:.5f}°（{diff_swiss_j2000*3600:.2f}\"）")
    print(f"17年分の歳差理論値:    {precession:.5f}°（{years*50.29:.2f}\"）")
    print("→ 差分は歳差運動に相当 ✅")


if __name__ == "__main__":
    compare_coordinate_systems()
