import streamlit as st
import pandas as pd
import io
import streamlit_authenticator as stauth
import logging
from cryptography.fernet import Fernet
import datetime
import os
from rapidfuzz import process

# ログ設定
logging.basicConfig(filename='access.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# 暗号キー（実運用では環境変数から取得推奨）
key = Fernet.generate_key()
cipher = Fernet(key)

# --- ユーザー認証設定 ---
hashed_passwords = stauth.Hasher(['password123']).generate()

credentials = {
    "usernames": {
        "admin": {
            "name": "Admin",
            "password": hashed_passwords[0]
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "customer_app",
    "abcdef",
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login('ログイン', 'main')

if authentication_status:
    authenticator.logout('ログアウト', 'sidebar')
    st.title("医療機関向け 顧客履歴管理システム（表記揺れ対応＋セキュア版）")

    @st.cache_data
    def load_normalization_dict(file_path):
        if file_path.endswith(".csv"):
            df_dict = pd.read_csv(file_path)
            return dict(zip(df_dict['variant'], df_dict['normalized']))
        elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
            import yaml
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return data
        else:
            return {}

    dict_file = "normalization.csv"
    if os.path.exists(dict_file):
        normalization_dict = load_normalization_dict(dict_file)
    else:
        st.error(f"正規化辞書ファイル {dict_file} が見つかりません。")
        normalization_dict = {}

    standard_names = list(set(normalization_dict.values()))

    st.header("1. 顧客データのアップロード")
    uploaded_files = st.file_uploader("Excelファイルをアップロード（複数選択可）", type=["xlsx", "xls"], accept_multiple_files=True)

    if uploaded_files:
        df_list = []
        for uploaded_file in uploaded_files:
            encrypted_data = cipher.encrypt(uploaded_file.read())
            decrypted_data = cipher.decrypt(encrypted_data)
            df_temp = pd.read_excel(io.BytesIO(decrypted_data))
            df_list.append(df_temp)
            logging.info(f"User {username} uploaded: {uploaded_file.name}")

        df = pd.concat(df_list, ignore_index=True)

        st.subheader("アップロード内容（結合済）")
        st.write(df.head())

        if "顧客名" not in df.columns:
            st.error("顧客名という列が見つかりません。列名を確認してください。")
        else:
            st.header("2. 顧客名の表記揺れを正規化")

            def normalize_name(name):
                if pd.isna(name):
                    return ""
                name = name.strip().replace("　", " ")
                if name in normalization_dict:
                    return normalization_dict[name]
                result = process.extractOne(name, standard_names, score_cutoff=80)
                if result is not None:
                    best_match, score = result[:2]
                    return best_match
                else:
                    return name

            df["正規化顧客名"] = df["顧客名"].apply(normalize_name)

            unmatched = df[df["顧客名"] == df["正規化顧客名"]]["顧客名"].unique().tolist()
            if unmatched:
                st.warning(f"正規化辞書に未登録の顧客名があります（{len(unmatched)} 件）:")
                st.write(unmatched)

            st.subheader("正規化結果")
            st.dataframe(df[["顧客名", "正規化顧客名"]])

            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            st.download_button(
                label="正規化結果をダウンロード",
                data=output,
                file_name="正規化後_顧客データ.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.header("3. 顧客単位で履歴を表示（正規化名ベース）")

            df["日付"] = pd.to_datetime(df["日付"], errors='coerce')

            customer_options = sorted(df["正規化顧客名"].unique())
            selected_customers = st.multiselect("正規化された顧客名を選択", customer_options, default=customer_options)

            start_date = st.date_input("開始日", df["日付"].min().date())
            end_date = st.date_input("終了日", df["日付"].max().date())

            actions = df["アクション"].dropna().unique().tolist()
            selected_actions = st.multiselect("アクションで絞り込み", actions, default=actions)

            filtered_df = df[(df["正規化顧客名"].isin(selected_customers)) &
                             (df["日付"].dt.date >= start_date) &
                             (df["日付"].dt.date <= end_date) &
                             (df["アクション"].isin(selected_actions))]

            st.subheader("フィルタ結果：履歴一覧（正規化名ベース）")
            st.dataframe(filtered_df)

            output_filtered = io.BytesIO()
            filtered_df.to_excel(output_filtered, index=False, engine='openpyxl')
            output_filtered.seek(0)

            st.download_button(
                label="フィルタ結果をCSV出力",
                data=output_filtered,
                file_name="フィルタ結果_履歴.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

elif authentication_status is False:
    st.error("ログイン情報が間違っています。")
elif authentication_status is None:
    st.warning("ユーザー名とパスワードを入力してください。")
