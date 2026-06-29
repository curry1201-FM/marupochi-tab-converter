import streamlit as st
from PIL import Image
import io
from make_tab import generate_pdf_score

st.set_page_config(layout="wide")

st.title("🎸 TAB譜 → まるぽち楽譜PDF変換アプリ")
st.write("横に長いTAB譜から、リズム（ハイフンの長さ）や小節線を再現した美しいA4楽譜PDFを自動生成します。")

# リズムや小節線（|）を含んだ、より実践的なサンプルTAB譜
sample_tab = """e|-------0---|-----------0---|-------1---|-----------1---|
B|-----1---1-|-----1---1-----|-----3---3-|-----3---3-----|
G|---0-------|---2---2-------|---2-------|---3---3-------|
D|-----------|---------------|-0---------|---------------|
A|-3---------|-0-------------|-----------|-1-------------|
E|-----------|---------------|-----------|---------------|"""

tab_input = st.text_area("ここにTAB譜をペーストしてください", value=sample_tab, height=200)

if st.button("高品質楽譜PDFを生成する"):
    if tab_input:
        with st.spinner("楽譜レイアウトを自動生成中..."):
            pdf_filename = "my_guitar_score.pdf"
            # PDFとページ画像リストを生成
            result = generate_pdf_score(tab_input, pdf_filename)
            
            if result is None:
                st.error("TAB譜の解析に失敗しました。最低6行のテキスト形式になっているか確認してください。")
            else:
                pages, filename = result
                st.success("✨ 楽譜の生成に成功しました！")
                
                # 1. PDFのダウンロードボタンを設置
                with open(filename, "rb") as f:
                    pdf_data = f.read()
                    
                st.download_button(
                    label="📥 完了した楽譜PDFをダウンロード",
                    data=pdf_data,
                    file_name="guitar_まるぽち譜.pdf",
                    mime="application/pdf"
                )
                
                st.write("---")
                st.subheader("👀 印刷プレビュー (A4サイズ)")
                
                # 2. 生成された楽譜の全ページを画面に縦並びでプレビュー表示
                for page_num, page_img in enumerate(pages):
                    st.image(page_img, caption=f"Page {page_num + 1}", use_container_width=True)
# --- これまでのコードの下に追加 ---
st.write("---")
st.markdown("### 🎸 作者の機材資金を支援する")
st.write("このツールが役に立ったら、ぜひ下のリンクから普段のお買い物をしていただけると、開発者のギター弦代になります！🙏")

# ※ "https://amazon.co.jp/" の部分を、後であなた専用のAmazonアソシエイトリンクに差し替えます。
# --- これまでのコードの下（支援セクション）を以下に書き換えます ---
st.write("---")
st.markdown("### 🎸 作者の機材資金を支援する")
st.write("このツールが役に立ったら、ぜひ下のリンクから普段の消耗品等をお買い求めいただけると、開発者のギター弦代（活動資金）になります！🙏")

# あなたが発行した3つのリンクをここに配置します
st.markdown("👉 **[作者おすすめの定番ギター弦（アコギ用など）はこちら](https://amzn.to/4xW7J6p)**")
st.markdown("👉 **[初心者にもおすすめの人気ギター弦はこちら](https://amzn.to/4aYVQmh)**")
st.markdown("👉 **[レビュー多数の定番アクセサリー・ピックはこちら](https://amzn.to/3QFddBP)**")
