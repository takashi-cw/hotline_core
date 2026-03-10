#!/usr/bin/env python3
"""
J2000 vs of-date 座標系の検証スクリプト（v4 修正版）

【v3からの修正】
v3では Skyfield の ecliptic_frame を「J2000」とラベルしていたが、
ecliptic_frame は実際には「of-date（当代の黄道）」フレームである。
正しい J2000 固定フレームは ecliptic_J2000_frame を使用する必要があった。
本スクリプトはそのラベルの誤りを修正した訂正版である。

フレームの正しい対応:
  ecliptic_frame       → of-date（歳差を含む当代の黄道フレーム）  ← v3で"J2000"と誤ラベル
  ecliptic_J2000_frame → J2000固定（歳差なし、2000年基準）
  ecliptic_latlon()    → J2000相当（ecliptic_J2000_frameと同値）  ← v3で"of-date"と誤ラベル

論文: 自己再検証：Swiss Ephemeris の座標系実装について（v4）
著者: 志賀高史（Takashi Shiga）
前バージョン DOI: https://doi.org/10.5281/zenodo.18767251
"""

from skyfield.api import load
from skyfield.framelib import ecliptic_frame, ecliptic_J2000_frame


def verify_j2000_vs_ofdate():
    """J2000とof-dateの黄経を比較（修正版）"""

    print("=" * 65)
    print("J2000 vs of-date 座標系の検証（v4 修正版）")
    print("=" * 65)
    print()
    print("【v3からの修正点】")
    print("  v3: ecliptic_frame → 誤って 'J2000' とラベル")
    print("  v4: ecliptic_frame → 正しく 'of-date' とラベル")
    print("  v4: ecliptic_J2000_frame → J2000固定フレームとして追加")
    print()

    ts = load.timescale()
    eph = load('de440s.bsp')

    # 観測条件（v3と同一）
    date = ts.utc(1983, 7, 5, 6, 42)

    print("📍 観測条件:")
    print("  日時: 1983年7月5日 15:42 JST（06:42 UTC）")
    print("  テストケース: v3と同一")

    earth = eph['earth']
    sun = eph['sun']
    astrometric = earth.at(date).observe(sun)
    apparent = astrometric.apparent()

    # ── 修正版フレーム計算 ───────────────────────────────────
    # of-date（当代の黄道フレーム）← v3ではこれを"J2000"と誤ラベルしていた
    ofdate_ecliptic = apparent.frame_latlon(ecliptic_frame)
    ofdate_lon = ofdate_ecliptic[1].degrees

    # J2000固定フレーム ← v3では ecliptic_latlon() を"of-date"と誤ラベルしていた
    j2000_ecliptic = apparent.frame_latlon(ecliptic_J2000_frame)
    j2000_lon = j2000_ecliptic[1].degrees

    # ecliptic_latlon()の確認（J2000相当）
    latlon_ecliptic = apparent.ecliptic_latlon()
    latlon_lon = latlon_ecliptic[1].degrees

    print()
    print("=" * 65)
    print("計算結果（修正版）")
    print("=" * 65)
    print()
    print(f"☀️  太陽黄経 (of-date / ecliptic_frame):       {ofdate_lon:.5f}°")
    print(f"☀️  太陽黄経 (J2000 / ecliptic_J2000_frame):   {j2000_lon:.5f}°")
    print(f"☀️  太陽黄経 (ecliptic_latlon()):              {latlon_lon:.5f}°")
    print()
    print("【v3の誤った出力との対比】")
    print(f"  v3が 'J2000' と呼んでいた値（実際は of-date）: {ofdate_lon:.5f}°")
    print(f"  v3が 'of-date' と呼んでいた値（実際は J2000）: {latlon_lon:.5f}°")

    diff = j2000_lon - ofdate_lon
    diff_arcsec = diff * 3600

    print()
    print(f"📊 差分 (J2000 − of-date): {diff:.5f}° ({diff_arcsec:.2f} 秒角)")

    # 理論的歳差
    years_from_j2000 = abs(1983 - 2000)
    precession_rate = 50.29 / 3600
    expected_diff = years_from_j2000 * precession_rate

    print()
    print("🔬 理論的予測（歳差運動）:")
    print(f"  J2000からの経過年数: {1983 - 2000} 年（絶対値: {years_from_j2000} 年）")
    print(f"  歳差速度: 50.29\"/年 = {precession_rate:.5f}°/年")
    print(f"  予想される差分: {expected_diff:.5f}°")
    print(f"  実測された差分: {abs(diff):.5f}°")
    error = abs(abs(diff) - expected_diff)
    print(f"  理論値との誤差: {error:.5f}°")

    if error < 0.01:
        print("   → 理論値とほぼ一致 ✅")

    print()
    print("=" * 65)
    print("結論（修正版）")
    print("=" * 65)
    print()
    print("J2000 と of-date の差は歳差運動に相当し、")
    print(f"1983年時点では約 {abs(diff):.3f}°（{abs(diff_arcsec):.1f} 秒角）の差がある。")
    print()
    print("v3 の誤り:")
    print("  ecliptic_frame を 'J2000' とラベルしていたが、")
    print("  これは実際には of-date（当代の黄道）フレームである。")
    print()
    print("v4 の正しい解釈:")
    print("  ecliptic_frame  = of-date（歳差込み）")
    print("  ecliptic_J2000_frame = J2000固定（歳差なし）")
    print("  ecliptic_latlon() = J2000相当")


if __name__ == "__main__":
    verify_j2000_vs_ofdate()
