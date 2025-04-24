import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
from openpyxl import load_workbook
import time

# Page config
st.set_page_config(page_title="📂 File Converter & Cleaner", layout="wide")

# Start animation and header
with st.container():
    st.markdown("""
        <style>
        .rain-emoji {
            font-size: 40px;
            animation: fall 1.5s infinite;
        }
        @keyframes fall {
            0% { transform: translateY(-40px); opacity: 0; }
            100% { transform: translateY(0px); opacity: 1; }
        }
        .footer {
            text-align: center;
            font-size: 14px;
            color: #888;
            padding: 1rem;
            border-top: 1px solid #ccc;
            margin-top: 2rem;
        }
        .emoji-cycle {
            font-size: 36px;
            animation: emojiBlink 2s infinite;
        }
        @keyframes emojiBlink {
            0% { opacity: 0.2; }
            50% { opacity: 1; }
            100% { opacity: 0.2; }
        }
        .footer-emoji {
            animation: bounce 1.5s infinite;
            display: inline-block;
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }
        </style>
        <div style='text-align:center;'>
            <div class='emoji-cycle'>📄 🔄 📊 📥 📈</div>
            <h1>📂 File Converter & Cleaner</h1>
            <p>Clean, convert and visualize your data files with ease 🚀</p>
        </div>
    """, unsafe_allow_html=True)

# File uploader
files = st.file_uploader("📁 Upload a CSV or Excel file", type=["csv", "xlsx"], accept_multiple_files=True)

if files:
    for file in files:
        ext = file.name.split(".")[-1].lower()

        if ext == "csv":
            df = pd.read_csv(file)
        elif ext == "xlsx":
            excel_data = pd.ExcelFile(file, engine='openpyxl')
            sheet = st.selectbox(f"📄 Select sheet from {file.name}", excel_data.sheet_names, key=file.name)
            df = pd.read_excel(excel_data, sheet_name=sheet)
        else:
            st.error(f"🚫 Unsupported file format: {ext}")
            continue

        st.subheader(f"🔍 Preview: {file.name}")
        st.dataframe(df, use_container_width=True)

        with st.expander(f"🧹 Clean & Transform - {file.name}"):
            if st.checkbox(f"✨ Fill missing values", key=f"fillna_{file.name}"):
                df.fillna(df.select_dtypes(include=["number"]).mean(), inplace=True)
                st.success("✅ Missing values filled!")
                st.dataframe(df, use_container_width=True)

            if st.checkbox(f"🧽 Remove duplicates", key=f"dropdup_{file.name}"):
                before = len(df)
                df.drop_duplicates(inplace=True)
                after = len(df)
                st.info(f"🧼 Removed {before - after} duplicates.")

            if st.checkbox(f"✏️ Rename columns", key=f"rename_{file.name}"):
                for col in df.columns:
                    new_name = st.text_input(f"✏️ Rename column '{col}'", value=col, key=f"rename_{col}_{file.name}")
                    if new_name != col:
                        df.rename(columns={col: new_name}, inplace=True)

        st.markdown("---")

        if not df.select_dtypes(include="number").empty:
            st.subheader("📊 Auto Chart")
            chart = alt.Chart(df.reset_index()).mark_bar().encode(
                x=alt.X(df.select_dtypes(include="number").columns[0], type='quantitative'),
                y=alt.Y(df.select_dtypes(include="number").columns[1], type='quantitative') if len(df.select_dtypes(include="number").columns) > 1 else alt.Y("index", type='ordinal')
            )
            st.altair_chart(chart, use_container_width=True)

        st.subheader("⬇️ Download Processed File")
        format_choice = st.radio(f"🧾 Convert {file.name} to:", ["CSV", "Excel", "JSON"], key=f"format_{file.name}")

        output = BytesIO()
        if format_choice == "CSV":
            df.to_csv(output, index=False)
            mime = "text/csv"
            new_name = file.name.replace(ext, "csv")
        elif format_choice == "Excel":
            df.to_excel(output, index=False, engine='openpyxl')
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            new_name = file.name.replace(ext, "xlsx")
        else:
            df.to_json(output, orient="records")
            mime = "application/json"
            new_name = file.name.replace(ext, "json")

        output.seek(0)
        if st.button(f"🎉 Generate & Download {new_name}", key=f"download_{file.name}"):
            with st.spinner("Generating file... 🎬✨"):
                time.sleep(1.5)
                st.balloons()
                st.download_button(f"📥 Download {new_name}", file_name=new_name, mime=mime, data=output)
                st.success("✅ File ready for download! 🎊")

# Footer
st.markdown("""
    <div class='footer'>
        <span class='footer-emoji'>💡</span> Made with ❤️ using <strong>Streamlit</strong> & <strong>Python</strong> <span class='footer-emoji'>🐍</span><br>
        Developed by <strong>Muhammad Hammad Zubair</strong> <span class='footer-emoji'>🚀</span>
    </div>
""", unsafe_allow_html=True)
