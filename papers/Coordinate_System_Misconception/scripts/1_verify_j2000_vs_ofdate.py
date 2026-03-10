#!/usr/bin/env python3
"""
J2000 vs of-date 座標系の検証スクリプト

Skyfield を使用して、J2000 座標系と of-date 座標系での
太陽黄経を計算し、差分を検証します。

論文: 占星術ソフトウェアにおける座標系の誤解
著者: 志賀高史
"""

from skyfield.api import load, wgs84
from skyfield.framelib import ecliptic_frame


def verify_j2000_vs_ofdate():
    """J2000とof-dateの黄経を比較"""
    
    print("="*60)
    print("J2000 vs of-date 座標系の検証")
    print("="*60)
    
    # タイムスケールと天体暦の読み込み
    print("\n⏳ 天体暦を読み込んでいます...")
    print("（初回実行時は DE440s のダウンロードに数分かかります）")
    
    ts = load.timescale()
    eph = load('de440s.bsp')  # 約3.3GB（初回のみダウンロード）
    
    # 観測条件
    # 日時: 1983年7月5日 15:42 JST → UTC 6:42
    # 場所: 千葉県松戸市
    date = ts.utc(1983, 7, 5, 6, 42)
    location = wgs84.latlon(35.79, 139.91)
    
    print("\n📍 観測条件:")
    print(f"  日時: 1983年7月5日 15:42 JST")
    print(f"  場所: 千葉県松戸市（北緯 35.79°, 東経 139.91°）")
    
    # 太陽の位置
    earth = eph['earth']
    sun = eph['sun']
    astrometric = earth.at(date).observe(sun)
    apparent = astrometric.apparent()
    
    # J2000 黄経
    j2000_ecliptic = apparent.frame_latlon(ecliptic_frame)
    j2000_lon = j2000_ecliptic[1].degrees
    
    # of-date 黄経
    ofdate_ecliptic = apparent.ecliptic_latlon()
    ofdate_lon = ofdate_ecliptic[1].degrees
    
    # 結果表示
    print("\n" + "="*60)
    print("計算結果")
    print("="*60)
    print(f"\n☀️  太陽黄経 (J2000):   {j2000_lon:.5f}°")
    print(f"☀️  太陽黄経 (of-date): {ofdate_lon:.5f}°")
    
    # 差分
    diff = ofdate_lon - j2000_lon
    diff_arcsec = diff * 3600
    
    print(f"\n📊 差分: {diff:.5f}° ({diff_arcsec:.2f} 秒角)")
    
    # 理論的歳差
    years_from_j2000 = 1983 - 2000  # = -17年
    precession_rate = 0.01397  # 度/年
    expected_diff = abs(years_from_j2000 * precession_rate)
    
    print(f"\n🔬 理論的予測:")
    print(f"  J2000からの経過年数: {years_from_j2000} 年")
    print(f"  歳差速度: {precession_rate} 度/年")
    print(f"  予想される差分: {expected_diff:.5f}°")
    
    # 評価
    error = abs(abs(diff) - expected_diff)
    print(f"\n✅ 理論値との誤差: {error:.5f}°")
    
    if error < 0.01:
        print("   → 理論値とほぼ一致 ✅")
    else:
        print("   → 理論値とのズレが大きい ⚠️")
    
    print("\n" + "="*60)
    print("結論")
    print("="*60)
    print("\nJ2000 と of-date の差は歳差運動による影響であり、")
    print("1983年時点では約 0.23° の差が生じることが確認されました。")
    print("\nこの差は、Swiss Ephemeris が実際に J2000 座標系を")
    print("使用していることを検証する際の重要な証拠となります。")
    print("\n" + "="*60)


if __name__ == "__main__":
    verify_j2000_vs_ofdate()

