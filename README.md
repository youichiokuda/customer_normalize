# 医療機関向け 顧客履歴管理システム（複数ファイル対応・表記揺れ正規化・セキュア版）

このアプリは、医療機関の顧客名における表記揺れ（名前の違い）を正規化し、複数のExcelファイルを統合して履歴情報を安全に管理・表示するためのツールです。Streamlitで構築され、ユーザー認証とファイル暗号化にも対応しています。

## 主な機能

- **顧客名の正規化**
  - 顧客名の表記揺れに対応し、正規化された名称に統一
  - 類似度による自動マッチング（RapidFuzz を使用）
  - 正規化辞書（CSVまたはYAML）に基づく一致処理

- **複数ファイル対応**
  - 複数のExcelファイルを一括アップロード
  - 全データを結合して正規化・分析

- **履歴管理とフィルタ**
  - 顧客・日付・アクションによる履歴データのフィルタと表示
  - フィルタ後のデータをExcel形式でダウンロード可能

- **セキュリティ**
  - `streamlit-authenticator` によるログイン機能
  - アップロードファイルの暗号化/復号処理（`cryptography` モジュール使用）
  - アクセスログの記録

---

## インストール方法

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
pip install -r requirements.txt
```

---

## 起動方法

```bash
streamlit run app.py
```

---

## 必要なファイル

- `normalization.csv`  
  正規化の辞書ファイル（以下のような形式）：

  ```csv
  variant,normalized
  京都中央病院,京都中央医療センター
  京中病院,京都中央医療センター
  ```

- Excelファイル（複数可）  
  以下の列が必要です：
  - `顧客名`
  - `日付`
  - `アクション`

---

## 使用ライブラリ

- `streamlit`
- `pandas`
- `cryptography`
- `streamlit-authenticator`
- `rapidfuzz`
- `openpyxl`（Excel出力用）

---

## 注意事項

- 暗号キーは実運用時には環境変数などで安全に管理してください。
- パスワードは適切にハッシュ化されていますが、本番環境では多要素認証やHTTPSを組み合わせることを推奨します。

---

## 開発・メンテナンス

開発者: [Your Name]  
ライセンス: MIT
