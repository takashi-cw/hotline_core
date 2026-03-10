# 検証スクリプト

本論文「占星術ソフトウェアにおける座標系の誤解」の検証を再現するための Python スクリプト集です。

## 📋 必要な環境

- **Python**: 3.8 以上
- **OS**: macOS, Linux, Windows（Pythonが動作する環境）
- **ディスク空き容量**: 約4GB（DE440s天体暦データのダウンロードに必要）

## 🔧 インストール

### 1. リポジトリのクローン

```bash
git clone https://github.com/[your-repo]/coordinate-systems-paper.git
cd coordinate-systems-paper/scripts/
```

### 2. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
```

## 📦 必要なパッケージ

- `skyfield >= 1.45` - JPL DE440s を直接使用する天文計算ライブラリ
- `pyswisseph >= 2.10.3` - Swiss Ephemeris のPythonラッパー
- `numpy >= 1.20.0` - 数値計算ライブラリ
- `pytz` - タイムゾーン処理

**注意:** flatlib は一部のスクリプトで必要ですが、インストールが複雑な場合があります。
該当スクリプトを実行しない場合は不要です。

## 🚀 使い方

### スクリプト一覧

| ファイル | 説明 | 重要度 |
|---------|------|--------|
| `1_verify_j2000_vs_ofdate.py` | Skyfield で J2000 と of-date を比較 | ⭐⭐⭐ |
| `2_verify_swiss_ephemeris.py` | Swiss Ephemeris の実装を検証 | ⭐⭐⭐ |
| `3_compare_all_engines.py` | 全エンジンの計算結果を比較 | ⭐⭐⭐ |
| `4_sidereal_springpoint_verification.py` | サイデリアル春分点の二重補正問題を検証（最重要） | ⭐⭐⭐⭐⭐ |

### 1. J2000 vs of-date の検証

```bash
python 1_verify_j2000_vs_ofdate.py
```

**期待される出力:**
```
☀️ 太陽黄経 (J2000):   102.69464°
☀️ 太陽黄経 (of-date): 102.92582°
📊 差分: 0.23118° (832.25 秒角)
🔬 理論値: 0.23749°
```

### 2. Swiss Ephemeris の検証

```bash
python 2_verify_swiss_ephemeris.py
```

**期待される出力:**
```
☀️ Swiss Ephemeris: 102.69462°
📋 座標系表記: Cancer 12.69462°
```

### 3. 全エンジンの比較

```bash
python 3_compare_all_engines.py
```

**期待される出力:**
```
============================================================
座標系比較検証
============================================================
エンジン                 座標系            黄経 (°)    
------------------------------------------------------------
Skyfield             J2000           102.69464   
Skyfield             of-date         102.92582   
Swiss Ephemeris      (表記: of-date) 102.69462   
============================================================

📊 差分分析:
  Swiss vs Skyfield J2000:  0.00002° (0.07秒角) → ほぼ一致 ✅
  Swiss vs Skyfield of-date: 0.23120° (832.32秒角) → 大きな差 ⚠️

🔬 結論:
  Swiss Ephemeris の 'of-date' 表記は
  実際には J2000 座標系で計算されている
```

### 4. サイデリアル春分点の検証（最重要）

```bash
python 4_sidereal_springpoint_verification.py
```

**期待される結果:**
- J2000ベース: Swiss Ephemeris と 0.0002° 以内で一致 ✅
- of-dateベース: Swiss Ephemeris と 0.35° ズレる ❌

これにより、二重補正問題が実証的に証明されます。

## ⚠️ 初回実行時の注意

### DE440s の自動ダウンロード

初回実行時、Skyfield が自動的に JPL DE440s 天体暦（約3.3GB）をダウンロードします。

```
実行例:
$ python 1_verify_j2000_vs_ofdate.py

[#################################] 100% de440s.bsp
ダウンロード中... （数分かかります）
```

- **所要時間**: 回線速度により 5〜15分程度
- **保存場所**: `~/.skyfield/` フォルダ
- **2回目以降**: ダウンロード不要（キャッシュを使用）

### Swiss Ephemeris データについて

pyswisseph パッケージには基本的な天体データが含まれているため、
**追加のデータファイルのダウンロードは不要**です。

- 太陽、月、主要惑星：パッケージに内蔵 ✅
- 小惑星、恒星等：必要に応じて別途ダウンロード（本検証では不要）

もし「SwissEph file not found」エラーが出る場合は、
トラブルシューティングのセクションを参照してください。

### 軽量版を使いたい場合

DE421（約17MB）を使用することもできます：

```python
# スクリプト内の load('de440s.bsp') を以下に変更
eph = load('de421.bsp')  # 軽量版（精度は若干低下）
```

## 📊 検証結果の解釈

### 成功例

```
✅ J2000ベース: Swiss Ephemerisと0.0002°以内で一致
   → Swiss EphemerisがJ2000を使用していることの証明

✅ 差分が理論値（0.23°前後）と一致
   → 歳差運動による差であることの証明
```

### 失敗例

```
❌ 差分が大きすぎる（1°以上）
   → 計算エラーまたは設定ミスの可能性

❌ J2000とof-dateの差がない（0°に近い）
   → スクリプトのバグまたは座標系の誤設定
```

## 🐛 トラブルシューティング

### エラー: `ModuleNotFoundError: No module named 'skyfield'`

```bash
# パッケージの再インストール
pip install -r requirements.txt
```

### エラー: `SwissEph file not found`

Swiss Ephemeris のデータファイルが見つからない場合：

```python
# スクリプト冒頭で天体暦パスを設定
import swisseph as swe
swe.set_ephe_path('/path/to/swisseph/')  # 適切なパスに変更
```

または、システムに Swiss Ephemeris データをインストール：

```bash
# macOS (Homebrew)
brew install swisseph

# Linux
sudo apt-get install libswe-dev
```

### エラー: `flatlib` のインストールに失敗

flatlib は PyPI での管理が不安定な場合があります：

```bash
# GitHubから直接インストール
pip install git+https://github.com/flatangle/flatlib.git
```

flatlib を使用しないスクリプト（1, 4）は問題なく動作します。

## 🔬 カスタマイズ

### 日時・場所を変更する

各スクリプトの冒頭部分を編集：

```python
# 日時の変更（例: 2025年1月1日）
date = ts.utc(2025, 1, 1, 0, 0)

# 場所の変更（例: 東京）
location = wgs84.latlon(35.6762, 139.6503)
```

### 他の天体で検証

```python
# 太陽の代わりに月で検証
sun = eph['sun']    # 変更前
moon = eph['moon']  # 変更後
```

## 📧 質問・フィードバック

- **GitHub Issues**: [リンク]
- **Email**: [準備中]

検証結果の報告やバグ報告は Issues でお願いします。

## 📝 ライセンス

本スクリプトは論文と同じく CC BY-NC-SA 4.0 ライセンスで提供されます。

## 🙏 謝辞

- Brandon Rhodes 氏（Skyfield 開発者）
- Astrodienst AG（Swiss Ephemeris 提供）
- NASA JPL（DE440s 天体暦提供）

