# 自己再検証：Swiss Ephemeris の座標系実装について
## ─ 前報（v3）の訂正と正しい検証結果 ─

**Self-Correction: On the Coordinate System Implementation of Swiss Ephemeris**  
**— Correction of Previous Report (v3) and Verified Results —**

---

## 📋 論文情報

- **著者**: Stella.me OS 開発者　志賀高史（Takashi Shiga）
- **発表日**: 2026年（前報公開後、再検証）
- **バージョン**: v4（訂正版）
- **ステータス**: 公開済（査読前プレプリント・訂正版）
- **DOI**: https://doi.org/10.5281/zenodo.18772796
- **訂正元論文（v3）DOI**: https://doi.org/10.5281/zenodo.18767251
- **分類**: 占星術ソフトウェア工学、天体暦システム、座標系解析
- **キーワード**: Swiss Ephemeris, J2000, of-date, 座標系, 歳差運動, Skyfield, フレーム検証, 訂正

---

## ⚠️ 本論文について

本論文は、著者が Zenodo に公開した前報（v3、DOI: https://doi.org/10.5281/zenodo.18767251）の**重大な誤りを訂正する**ものである。

前報は「Swiss Ephemeris の tropical 出力は実際には J2000 座標系である」と主張したが、公開後の自己再検証により、この結論が**検証スクリプトのフレームラベルの誤りに起因する**ことが判明した。

本論文で示す正しい結論は以下の通りである：

> **Swiss Ephemeris はドキュメントに記載されている通り、of-date（tropical）黄道座標を正しく実装している。**

---

## 要旨（Abstract）

### 日本語

前報（v3）において、著者は Swiss Ephemeris の "tropical" 出力が実際には J2000 座標系であると主張した。しかし公開後、検証に使用した Skyfield の座標系フレームのラベルが逆転していたことが判明した。具体的には、Skyfield の `ecliptic_frame`（実際は of-date フレーム）を "J2000" と誤ってラベルし、`ecliptic_latlon()`（J2000 相当の値を返す）を "of-date" と誤ってラベルしていた。

正しいフレームで再検証した結果、Swiss Ephemeris の太陽黄経（1983年7月5日：102.69463°）は Skyfield の `ecliptic_frame`（of-date）と **0.032 秒角以内で一致**し、`ecliptic_J2000_frame`（J2000 固定）とは **846 秒角（17年分の歳差）の差**があることが確認された。

これは Swiss Ephemeris がドキュメント通り of-date 座標系を正しく実装していることを意味する。前報の核心的主張「Swiss = J2000」および関連する「二重補正問題」の記述は誤りであり、ここに訂正する。

また、今回の経験は天文計算ライブラリを用いた座標系検証における重要な教訓を示している。フレーム名が直感に反する命名を持つ場合、ライブラリのドキュメントまたは既知の数値での事前検証が不可欠である。

### English

In the previous report (v3), the author claimed that Swiss Ephemeris's "tropical" output is actually in the J2000 coordinate system. However, after publication, it was discovered that the Skyfield coordinate frame labels used in the verification scripts were reversed. Specifically, Skyfield's `ecliptic_frame` (which is actually an of-date frame) was incorrectly labeled as "J2000", and `ecliptic_latlon()` (which returns J2000-equivalent values) was incorrectly labeled as "of-date".

Re-verification with the correct frame labels confirmed that Swiss Ephemeris's solar longitude (July 5, 1983: 102.69463°) matches Skyfield's `ecliptic_frame` (of-date) **within 0.032 arcseconds**, and differs from `ecliptic_J2000_frame` (J2000 fixed) by **846 arcseconds** (equivalent to 17 years of precession).

This demonstrates that Swiss Ephemeris correctly implements the of-date coordinate system as documented. The central claim of the previous report—"Swiss = J2000"—and the associated description of a "double correction problem" were erroneous and are hereby corrected.

This experience also provides an important lesson for coordinate system verification using astronomical libraries: when frame names have counter-intuitive naming, pre-verification against known numerical values or library documentation is essential.

**Keywords:** astrological software, ephemeris, coordinate systems, J2000, of-date, Swiss Ephemeris, precession, Skyfield, frame verification, erratum

---

## 1. 経緯（Background）

### 1.1 前報（v3）の主張

前報（v3、2026年2月25日公開）において著者は以下を主張した：

1. Swiss Ephemeris の "tropical" 出力は実際には J2000 座標系である
2. Swiss Ephemeris のドキュメントが示す "of-date" という記述は実装と乖離している
3. of-date ベースでサイデリアル計算を行うと「二重補正問題」が発生する

これらの主張は、Skyfield を用いた数値比較に基づいていた。具体的には：

- Skyfield で "J2000" として計算した値：102.69464°
- Swiss Ephemeris の tropical 出力：102.69462°
- 両者の差：0.00002°（ほぼ完全一致）

この一致から「Swiss = J2000」と結論づけた。

### 1.2 問題の発見

前報公開後、著者は検証スクリプトの再点検を行った。その過程で、Skyfield のフレーム定義を改めて調査したところ、**前報で "J2000" とラベルしていた計算が実際には of-date フレームを使用していた**ことが判明した。

**問題のあったコード（v3）:**
```python
from skyfield.framelib import ecliptic_frame  # ← of-dateフレームである

# v3では誤って "J2000" とラベル
j2000_ecliptic = apparent.frame_latlon(ecliptic_frame)   # 実際はof-date
skyfield_j2000 = j2000_ecliptic[1].degrees

# v3では誤って "of-date" とラベル
ofdate_ecliptic = apparent.ecliptic_latlon()              # 実際はJ2000相当
skyfield_ofdate = ofdate_ecliptic[1].degrees
```

Skyfield における各フレームの正しい定義：

| Skyfield API | 正しい定義 | v3でのラベル（誤り） |
|---|---|---|
| `ecliptic_frame` | **of-date**（当代の黄道フレーム、歳差込み） | "J2000"（誤） |
| `ecliptic_J2000_frame` | **J2000 固定**（歳差なし） | 未使用 |
| `ecliptic_latlon()` | **J2000 相当**（`ecliptic_J2000_frame`と同値） | "of-date"（誤） |

この誤りにより、前報では Swiss と "J2000"（実際は of-date）が一致したことを根拠に「Swiss = J2000」と誤結論した。

---

## 2. 正しい検証方法（Corrected Methodology）

### 2.1 フレームの事前検証

Skyfield のフレームを使用する際は、まず**既知の歳差量との整合性を確認する**ことが不可欠である。

2025年1月1日を例に取ると、J2000から25年後の歳差量は：

```
25年 × 50.29"/年 ≈ 1257秒角 ≈ 0.349°
```

この値が各フレームの差分として現れるかを確認する：

```python
from skyfield.framelib import ecliptic_frame, ecliptic_J2000_frame

# 太陽の2025年1月1日の黄経を各フレームで計算
lon_ecliptic_frame    # ecliptic_frame
lon_j2000_frame       # ecliptic_J2000_frame
```

**事前検証結果（2025-01-01 00:00 UTC）：**

| フレーム | 太陽黄経 | 差分 |
|---|---|---|
| `ecliptic_J2000_frame`（J2000固定） | 280.464305° | 基準 |
| `ecliptic_frame`（of-date） | 280.813613° | +0.349308°（≈ 1257秒角） |

差分 0.349° は理論的な歳差量（0.349°）と一致し、`ecliptic_frame` が of-date フレームであることが確認できる。

### 2.2 修正後のスクリプト構成

修正版スクリプトでは以下のフレームを使用する：

```python
from skyfield.framelib import ecliptic_frame, ecliptic_J2000_frame

# of-date（修正版）
ofdate_ecliptic = apparent.frame_latlon(ecliptic_frame)     # of-date
skyfield_ofdate = ofdate_ecliptic[1].degrees

# J2000固定（修正版）
j2000_ecliptic = apparent.frame_latlon(ecliptic_J2000_frame) # J2000
skyfield_j2000 = j2000_ecliptic[1].degrees
```

---

## 3. 再検証結果（Corrected Results）

### 3.1 1983年テストケース（前報と同一条件）

**観測条件：** 1983年7月5日 15:42 JST（06:42 UTC）、千葉県松戸市

**計算結果（修正版）：**

| エンジン | フレーム | 太陽黄経 |
|---|---|---|
| Swiss Ephemeris | tropical | 102.694627° |
| Skyfield | of-date（`ecliptic_frame`） | 102.694636° |
| Skyfield | J2000固定（`ecliptic_J2000_frame`） | 102.929687° |
| Skyfield | `ecliptic_latlon()` | 102.929687° |

**差分分析：**

| 比較 | 差分 | 解釈 |
|---|---|---|
| Swiss − Skyfield of-date | **−0.000009°（−0.032"）** | ほぼ完全一致 ✅ |
| Swiss − Skyfield J2000 | −0.235060°（−846.2"） | 17年分の歳差に相当 |

**理論検証：** 1983年は J2000 より 17 年前であり、歳差量は 17 × 50.29" = 854.9"。実測差分 846.2" と概ね一致する（差は章動等の影響）。

### 3.2 2025年検証（追加検証）

**観測条件：** 2025年1月1日 00:00 UTC

**計算結果：**

| エンジン | フレーム | 太陽黄経 |
|---|---|---|
| Swiss Ephemeris | tropical | 280.813646° |
| Skyfield | of-date（`ecliptic_frame`） | 280.813613° |
| Skyfield | J2000固定（`ecliptic_J2000_frame`） | 280.464305° |

**差分分析：**

| 比較 | 差分 | 解釈 |
|---|---|---|
| Swiss − Skyfield of-date | **+0.000033°（+0.12"）** | ほぼ完全一致 ✅ |
| Swiss − Skyfield J2000 | +0.349341°（+1257.6"） | 25年分の歳差に相当 |

### 3.3 木星・水星での確認（2025年1月1日）

| 天体 | Swiss | Skyfield of-date | 差分 |
|---|---|---|---|
| 太陽 | 280.813646° | 280.813613° | 0.12" |
| 木星 | 73.215459° | 73.215460° | 0.004" |
| 水星 | 259.870023° | 259.869981° | 0.15" |

全天体で Swiss と Skyfield of-date が 0.2 秒角以内で一致。**Swiss Ephemeris は全天体でof-dateを正しく計算していることが確認された。**

---

## 4. 考察（Discussion）

### 4.1 混乱の原因：Skyfield のフレーム命名

今回の誤りの直接原因は、Skyfield の `ecliptic_frame` という名前が「of-date フレーム」であることを直感的に示していないことにある。

通常、"frame" という名称は特定のエポックを想起させない。一方 `ecliptic_J2000_frame` は名称から J2000 固定であることが明確である。この命名の非対称性が混乱を招いた。

**フレーム名の対称的な理解（推奨）：**

```
ecliptic_frame       → "ecliptic_ofdate_frame" と読み替えると直感的
ecliptic_J2000_frame → J2000固定、名称から明確
```

### 4.2 Swiss Ephemeris の実装評価

今回の再検証により、Swiss Ephemeris はドキュメントに記載された通りの動作をしていることが確認された。

- **ドキュメントの記述：** tropical = of-date（当代の春分点基準）
- **実装の実態：** of-date（Skyfield の `ecliptic_frame` と 0.2 秒角以内で一致）
- **評価：** 実装とドキュメントは一致している ✅

前報で主張した「ドキュメントと実装の乖離」は存在しなかった。

### 4.3 前報「二重補正問題」の訂正

前報では、「Swiss が J2000 を使用しているため、サイデリアル計算で二重補正が発生する」と主張した。

しかし Swiss は of-date を正しく実装しているため、標準的なサイデリアル計算：

```
サイデリアル黄経 = Swiss tropical（of-date） − アヤナムサ（of-date定義）
```

は正しい。アヤナムサ自体が of-date フレームで定義されているため、両者のフレームが一致しており、二重補正は発生しない。

**前報の「二重補正問題」の記述はすべて誤りであり、訂正する。**

### 4.4 検証方法論への教訓

本件から得られる教訓：

1. **フレーム定義の事前確認：** 天文計算ライブラリのフレームを使用する際、既知の歳差量と差分が一致するかを事前に確認する
2. **複数エポックでの検証：** 1点のみの比較では一致の方向性を誤りやすい。J2000 より前と後の両方で検証することで、フレームの誤特定を防げる
3. **ライブラリドキュメントの精読：** 名称が直感に反する場合、必ずドキュメントで定義を確認する

---

## 5. 結論（Conclusion）

本論文は前報（v3、DOI: https://doi.org/10.5281/zenodo.18767251）の訂正を目的として執筆した。

**訂正内容：**

1. **前報の主張「Swiss Ephemeris は J2000 を使用している」は誤りである。**  
   Swiss Ephemeris は of-date（tropical）座標系をドキュメント通り正しく実装している。

2. **誤りの原因：** 検証スクリプトにおいて Skyfield の `ecliptic_frame`（of-date）を "J2000" と誤ラベルしたため。

3. **前報の「二重補正問題」の記述はすべて誤りである。**  
   Swiss の tropical 出力（of-date）からアヤナムサを引くサイデリアル計算は正しい。

4. **正しい検証結果：**  
   Swiss Ephemeris と Skyfield の of-date フレーム（`ecliptic_frame`）は 0.2 秒角以内で一致する。

---

## 6. 参考文献（References）

### 6.1 天体暦・座標系

- Folkner, W. M., Williams, J. G., Boggs, D. H., Park, R. S., & Kuchynka, P. (2014). *The planetary and lunar ephemerides DE430 and DE431*. Interplanetary Network Progress Report, 196.
- IAU SOFA Board (2021). *IAU SOFA Software Collection*. http://www.iausofa.org
- Lieske, J. H., et al. (1977). Expressions for the precession quantities based upon the IAU (1976) system of astronomical constants. *Astronomy and Astrophysics*, 58, 1–16.

### 6.2 ソフトウェア・ライブラリ

- Rhodes, B. (2019). *Skyfield: High precision research-grade positions for planets and Earth satellites generator*. Astrophysics Source Code Library, record ascl:1907.024. https://rhodesmill.org/skyfield/
- Dieter Koch & Alois Treindl (1997–). *Swiss Ephemeris*. Astrodienst AG. https://www.astro.com/swisseph/
- Ventura, J. (2016). *flatlib: Traditional Western Astrology with Python*. https://github.com/flatangle/flatlib

### 6.3 前報

- 志賀高史 (2026). *占星術ソフトウェアにおける座標系の誤解：用語と実装の乖離、そして定義の曖昧さ*（v3）. Zenodo. https://doi.org/10.5281/zenodo.18767251

---

## 7. 付録（Appendix）

### 7.1 修正版検証スクリプト

本論文に付属するスクリプトは v3 からの修正版である。

#### A.1 フレームの事前検証スクリプト

```python
#!/usr/bin/env python3
"""フレーム定義の事前検証：ecliptic_frame が of-date であることを確認"""
from skyfield.api import load
from skyfield.framelib import ecliptic_frame, ecliptic_J2000_frame

ts = load.timescale()
eph = load('de440s.bsp')
t = ts.utc(2025, 1, 1, 0, 0, 0)
earth = eph['earth']
sun = eph['sun']
apparent = earth.at(t).observe(sun).apparent()

_, lon_ofdate, _ = apparent.frame_latlon(ecliptic_frame)
_, lon_j2000, _  = apparent.frame_latlon(ecliptic_J2000_frame)

diff = lon_ofdate.degrees - lon_j2000.degrees
print(f"ecliptic_frame  (of-date): {lon_ofdate.degrees:.6f}°")
print(f"ecliptic_J2000_frame (J2000): {lon_j2000.degrees:.6f}°")
print(f"差分: {diff:.6f}°（{diff*3600:.2f}\"）")
print(f"理論歳差量（25年）: {25*50.29/3600:.6f}°（{25*50.29:.2f}\"）")
# 出力例:
# ecliptic_frame  (of-date): 280.813613°
# ecliptic_J2000_frame (J2000): 280.464305°
# 差分: 0.349308°（1257.51"）
# 理論歳差量（25年）: 0.349236°（1257.25"）
```

#### A.2 Swiss Ephemeris vs Skyfield 比較スクリプト（修正版）

修正されたスクリプトは本論文と同じフォルダの以下のファイルを参照：

- `1_verify_j2000_vs_ofdate_v4.py` — J2000 と of-date の差の検証（修正版）
- `3_compare_all_engines_v4.py` — Swiss vs Skyfield の全フレーム比較（修正版）

**実行方法：**
```bash
# 事前準備
pip install skyfield flatlib

# 実行
python 1_verify_j2000_vs_ofdate_v4.py
python 3_compare_all_engines_v4.py
```

### 7.2 v3との主要な数値比較

| 比較 | v3の記述（誤） | v4の正しい値 |
|---|---|---|
| Swiss vs "J2000" | 0.00002°（一致） | 0.000009°（of-dateとの一致） |
| Swiss vs "of-date" | 0.231°（不一致） | 0.235°（J2000との差分） |
| 結論 | Swiss = J2000 | Swiss = of-date ✅ |

### 7.3 用語集

| 用語 | 定義 |
|---|---|
| J2000 | 2000年1月1.5日（J2000.0）を基準エポックとする固定座標系。春分点方向が固定。 |
| of-date | 観測時点の春分点を基準とする座標系。歳差運動により基準方向が年々変化する。 |
| tropical | 占星術における "of-date" に相当。季節（春分点）基準の黄道座標。 |
| 歳差運動 | 地球の自転軸の向きが約26,000年周期で変化する現象。春分点は年約50.3" 西へ移動。 |
| アヤナムサ | トロピカル（of-date）春分点からサイデリアル春分点（固定恒星基準）までの角度。|
| ecliptic_frame | Skyfield のフレーム。**of-date 黄道**を使用（名称に注意）。 |
| ecliptic_J2000_frame | Skyfield のフレーム。**J2000 固定黄道**を使用。 |

---

## 謝辞（Acknowledgments）

本訂正論文の執筆にあたり、Stella.me OS の開発において使用した以下のオープンソースソフトウェアに謝意を表する。

- Brandon Rhodes 氏による **Skyfield** ライブラリ（https://rhodesmill.org/skyfield/）
- NASA JPL による **DE440s** 惑星暦
- Dieter Koch & Alois Treindl による **Swiss Ephemeris**（https://www.astro.com/swisseph/）

---

## 連絡先（Contact）

- **Email**: shigatakashi.cw@gmail.com
- **Stella.me OS**: 独自天文計算エンジン（JPL DE440s + Skyfield ベース）

---

## 📄 ライセンス

本論文は **CC BY 4.0**（Creative Commons Attribution 4.0 International）の下で公開する。

引用形式（APA）:  
志賀高史 (2026). *自己再検証：Swiss Ephemeris の座標系実装について — 前報（v3）の訂正と正しい検証結果*（v4）. Zenodo. https://doi.org/10.5281/zenodo.18772796

前報引用:  
志賀高史 (2026). *占星術ソフトウェアにおける座標系の誤解：用語と実装の乖離、そして定義の曖昧さ*（v3）. Zenodo. https://doi.org/10.5281/zenodo.18767251

---

## 📝 更新履歴（Change Log）

### Version 4.0（訂正版）
- v3 の核心的誤り（フレームラベルの逆転）を訂正
- 正しいフレームを用いた再検証結果を掲載
- 「二重補正問題」の記述を全面訂正
- 修正版検証スクリプトを付属

### Version 3.0（訂正元）
- DOI: https://doi.org/10.5281/zenodo.18767251
- 主張：Swiss Ephemeris は J2000 を使用（**本訂正論文により撤回**）
