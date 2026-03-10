# hotline_core
ショートストーリーとZenodo公開論文の原文を保管するリポジトリ。

## 目的
- ショートストーリーを作品単位で管理する
- Zenodo公開論文の原文と付随情報を論文単位で管理する

## ディレクトリ構成

```text
hotline_core/
├── stories/   
└── papers/
```

## 運用ルール
- 1作品/1論文ごとにフォルダを作る
- Markdown本文と画像・図表を同じフォルダ配下に置く
- 画像参照は相対パスを使う
- 公開済み論文は `papers/<paper-slug> DOI と URL を記録する

## 目次

papers/Coordinate_System_Misconception
→ v4："Self-Correction: Swiss Ephemeris Coordinate System 自己再検証：Swiss Ephemeris の座標系実装について"

## ライセンス
- 詳細は `LICENSE.md` を参照

## 更新履歴

2026/03/08：ディレクトリ構成を変更。
2026/03/10：papers/Coordinate_System_Misconception 追加
