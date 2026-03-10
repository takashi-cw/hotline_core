#!/usr/bin/env python3
"""
Swiss Ephemeris の座標系検証スクリプト

flatlib (Swiss Ephemeris) を使用して太陽黄経を計算し、
Swiss Ephemeris が実際にどの座標系を使用しているかを検証します。

注意: このスクリプトには flatlib のインストールが必要です。
     pip install git+https://github.com/flatangle/flatlib.git

論文: 占星術ソフトウェアにおける座標系の誤解
著者: 志賀高史
"""

try:
    from flatlib.datetime import Datetime
    from flatlib.geopos import GeoPos
    from flatlib.chart import Chart
    from flatlib import const
except ImportError:
    print("❌ エラー: flatlib がインストールされていません。")
    print("\n以下のコマンドでインストールしてください:")
    print("pip install git+https://github.com/flatangle/flatlib.git")
    exit(1)


def verify_swiss_ephemeris():
    """Swiss Ephemeris で太陽黄経を計算"""
    
    print("="*60)
    print("Swiss Ephemeris の座標系検証")
    print("="*60)
    
    # 観測条件（JSTで指定）
    date = Datetime('1983/07/05', '15:42', '+09:00')
    location = GeoPos(35.79, 139.91)
    
    print("\n📍 観測条件:")
    print(f"  日時: 1983年7月5日 15:42 JST")
    print(f"  場所: 千葉県松戸市（北緯 35.79°, 東経 139.91°）")
    
    # チャート作成
    print("\n⏳ Swiss Ephemeris で計算中...")
    chart = Chart(date, location)
    sun = chart.get(const.SUN)
    
    # 結果表示
    print("\n" + "="*60)
    print("計算結果")
    print("="*60)
    print(f"\n☀️  Swiss Ephemeris (tropical): {sun.lon:.5f}°")
    print(f"📋 星座表記: {sun.sign} {sun.signlon:.5f}°")
    
    # 度分秒表記
    degrees = int(sun.lon)
    minutes = int((sun.lon - degrees) * 60)
    seconds = ((sun.lon - degrees) * 60 - minutes) * 60
    print(f"📐 度分秒表記: {degrees}° {minutes}' {seconds:.2f}\"")
    
    print("\n" + "="*60)
    print("解釈")
    print("="*60)
    print("\nSwiss Ephemeris は「tropical」として出力していますが、")
    print("この値が J2000 なのか of-date なのかは、")
    print("スクリプト 3 (compare_all_engines.py) で Skyfield と")
    print("比較することで判明します。")
    print("\n期待される結果:")
    print("  Skyfield J2000:   102.69464°")
    print("  Skyfield of-date: 102.92582°")
    print(f"  Swiss Ephemeris:  {sun.lon:.5f}°")
    
    # 判定
    diff_j2000 = abs(sun.lon - 102.69464)
    diff_ofdate = abs(sun.lon - 102.92582)
    
    print(f"\n📊 差分:")
    print(f"  vs J2000:   {diff_j2000:.5f}° ({diff_j2000*3600:.2f} 秒角)")
    print(f"  vs of-date: {diff_ofdate:.5f}° ({diff_ofdate*3600:.2f} 秒角)")
    
    if diff_j2000 < 0.001:
        print("\n✅ Swiss Ephemeris は J2000 座標系を使用しています！")
    elif diff_ofdate < 0.001:
        print("\n⚠️  Swiss Ephemeris は of-date 座標系を使用しています！")
    else:
        print("\n⚠️  予期しない結果です。計算を確認してください。")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    verify_swiss_ephemeris()

