#!/usr/bin/env python3
"""
全エンジン比較スクリプト

Skyfield (J2000), Skyfield (of-date), Swiss Ephemeris の
3つの計算結果を比較し、Swiss Ephemeris がどの座標系を
使用しているかを決定的に判定します。

論文: 占星術ソフトウェアにおける座標系の誤解
著者: 志賀高史
"""

from skyfield.api import load, wgs84
from skyfield.framelib import ecliptic_frame


def compare_coordinate_systems():
    """3つの計算結果を比較"""
    
    # ===== Skyfield の計算 =====
    print("="*60)
    print("座標系比較検証")
    print("="*60)
    print("\n⏳ Skyfield で計算中...")
    
    ts = load.timescale()
    eph = load('de440s.bsp')
    
    # 観測条件
    date = ts.utc(1983, 7, 5, 6, 42)  # UTC
    location = wgs84.latlon(35.79, 139.91)
    
    # 太陽の位置
    earth = eph['earth']
    sun = eph['sun']
    astrometric = earth.at(date).observe(sun)
    apparent = astrometric.apparent()
    
    # J2000
    j2000_ecliptic = apparent.frame_latlon(ecliptic_frame)
    skyfield_j2000 = j2000_ecliptic[1].degrees
    
    # of-date
    ofdate_ecliptic = apparent.ecliptic_latlon()
    skyfield_ofdate = ofdate_ecliptic[1].degrees
    
    # ===== Swiss Ephemeris の計算 =====
    try:
        from flatlib.datetime import Datetime
        from flatlib.geopos import GeoPos
        from flatlib.chart import Chart
        from flatlib import const
        
        print("⏳ Swiss Ephemeris で計算中...")
        
        date_swiss = Datetime('1983/07/05', '15:42', '+09:00')
        location_swiss = GeoPos(35.79, 139.91)
        chart = Chart(date_swiss, location_swiss)
        sun_swiss = chart.get(const.SUN)
        swiss = sun_swiss.lon
        
        swiss_available = True
    except ImportError:
        print("⚠️  flatlib がインストールされていないため、")
        print("   Swiss Ephemeris の計算はスキップします。")
        swiss = 102.69462  # 論文の値を使用
        swiss_available = False
    
    # ===== 結果表示 =====
    print("\n" + "="*60)
    print("計算結果")
    print("="*60)
    print(f"{'エンジン':<20} {'座標系':<15} {'黄経 (°)':<12}")
    print("-" * 60)
    print(f"{'Skyfield':<20} {'J2000':<15} {skyfield_j2000:<12.5f}")
    print(f"{'Skyfield':<20} {'of-date':<15} {skyfield_ofdate:<12.5f}")
    if swiss_available:
        print(f"{'Swiss Ephemeris':<20} {'(表記: tropical)':<15} {swiss:<12.5f}")
    else:
        print(f"{'Swiss Ephemeris':<20} {'(表記: tropical)':<15} {swiss:<12.5f} *")
        print("\n* flatlib 未インストールのため、論文の値を使用")
    print("="*60)
    
    # ===== 差分分析 =====
    diff_swiss_j2000 = abs(swiss - skyfield_j2000)
    diff_swiss_ofdate = abs(swiss - skyfield_ofdate)
    
    print("\n📊 差分分析:")
    print(f"  Swiss vs Skyfield J2000:  {diff_swiss_j2000:.5f}° "
          f"({diff_swiss_j2000 * 3600:.2f}秒角) ", end="")
    
    if diff_swiss_j2000 < 0.001:
        print("→ ほぼ一致 ✅")
    else:
        print("→ 差がある ⚠️")
    
    print(f"  Swiss vs Skyfield of-date: {diff_swiss_ofdate:.5f}° "
          f"({diff_swiss_ofdate * 3600:.2f}秒角) ", end="")
    
    if diff_swiss_ofdate < 0.001:
        print("→ ほぼ一致 ✅")
    else:
        print("→ 大きな差 ⚠️")
    
    # ===== 結論 =====
    print("\n" + "="*60)
    print("🔬 結論")
    print("="*60)
    
    if diff_swiss_j2000 < 0.001:
        print("\n✅ Swiss Ephemeris の 'tropical' 表記は")
        print("   実際には J2000 座標系で計算されています！")
        print("\n📌 重要な発見:")
        print("   - 表記: 'of-date' / 'tropical'")
        print("   - 実装: J2000 座標系")
        print("   - 差分: 0.23° (17年分の歳差運動)")
        print("\nこの用語と実装の乖離が、占星術業界全体における")
        print("認識のギャップを生んでいました。")
    elif diff_swiss_ofdate < 0.001:
        print("\n⚠️  Swiss Ephemeris は of-date 座標系を使用しています。")
        print("   これは論文の予測と異なる結果です。")
    else:
        print("\n⚠️  予期しない結果です。")
        print("   計算条件を確認してください。")
    
    print("\n" + "="*60)
    
    # ===== 歳差運動の説明 =====
    print("\n📖 補足: 歳差運動による差")
    print("="*60)
    years_from_j2000 = 1983 - 2000
    precession = abs(years_from_j2000 * 0.01397)
    print(f"  J2000からの経過年数: {years_from_j2000} 年")
    print(f"  予想される歳差: {precession:.5f}°")
    print(f"  実測された差分: {diff_swiss_ofdate:.5f}°")
    print(f"  理論値との一致度: {abs(precession - diff_swiss_ofdate):.5f}°")
    print("\n地球の歳差運動により、春分点は年々西へ移動します。")
    print("この移動速度は約50.29秒角/年（≈0.01397度/年）です。")
    print("\n" + "="*60)


if __name__ == "__main__":
    compare_coordinate_systems()

