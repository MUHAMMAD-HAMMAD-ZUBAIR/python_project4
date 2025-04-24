import streamlit as st  # Import Streamlit for building the web app
import pandas as pd  # Import Pandas for data manipulation (working with CSV/Excel files)
import altair as alt  # Import Altair for creating charts and graphs
from io import BytesIO  # Import BytesIO to handle in-memory file operations
from openpyxl import load_workbook  # Import OpenPyXL to read Excel files
import time  # Import time to simulate processing delays

# Set up the page configuration: Title and layout of the app
st.set_page_config(page_title="📂 File Converter & Cleaner", layout="wide")

# Start of the animation and header section for the page
with st.container():  # This creates a container for the header
    st.markdown("""
        <style>
        .rain-emoji {
            font-size: 40px;
            animation: fall 1.5s infinite;  # Define a rain animation effect for emojis
        }
        @keyframes fall {
            0% { transform: translateY(-40px); opacity: 0; }
            100% { transform: translateY(0px); opacity: 1; }  # Emoji falling effect
        }
        .footer {
            text-align: center;  # Footer content will be centered
            font-size: 14px;  # Set font size for the footer
            color: #888;  # Set footer text color
            padding: 1rem;  # Add padding around the footer
            border-top: 1px solid #ccc;  # Add a top border to the footer
            margin-top: 2rem;  # Add margin on top of the footer
        }
        .emoji-cycle {
            font-size: 36px;  # Set font size for the emoji cycle
            animation: emojiBlink 2s infinite;  # Define animation to blink emojis
        }
        @keyframes emojiBlink {
            0% { opacity: 0.2; }  # Emojis start with low opacity
            50% { opacity: 1; }  # Emojis become fully visible at 50% of the animation
            100% { opacity: 0.2; }  # Emojis fade out again
        }
        .footer-emoji {
            animation: bounce 1.5s infinite;  # Add a bouncing animation to footer emojis
            display: inline-block;  # Display emojis inline with other content
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }  # Emojis bounce up and down
            50% { transform: translateY(-8px); }  # Emojis move up by 8px
        }
        </style>
        <div style='text-align:center;'>  # Center the content of the header
            <div class='emoji-cycle'>📄 🔄 📊 📥 📈</div>  # Display a sequence of emojis with animation
            <h1>📂 File Converter & Cleaner</h1>  # Display the app title
            <p>Clean, convert and visualize your data files with ease 🚀</p>  # Display a description of the app
        </div>
    """, unsafe_allow_html=True)  # Allow raw HTML content for styling

# File uploader: Let the user upload CSV or Excel files
files = st.file_uploader("📁 Upload a CSV or Excel file", type=["csv", "xlsx"], accept_multiple_files=True)

# Check if any files are uploaded
if files:
    for file in files:  # Loop through all uploaded files
        ext = file.name.split(".")[-1].lower()  # Get the file extension (csv or xlsx)

        # If the file is CSV, read it into a DataFrame
        if ext == "csv":
            df = pd.read_csv(file)  # Use Pandas to read CSV data
        # If the file is Excel, read it into a DataFrame
        elif ext == "xlsx":
            excel_data = pd.ExcelFile(file, engine='openpyxl')  # Load Excel data
            sheet = st.selectbox(f"📄 Select sheet from {file.name}", excel_data.sheet_names, key=file.name)  # Let user choose sheet
            df = pd.read_excel(excel_data, sheet_name=sheet)  # Read the selected sheet from Excel
        else:
            st.error(f"🚫 Unsupported file format: {ext}")  # Show an error for unsupported formats
            continue  # Skip this file and move to the next one

        # Show a preview of the data from the file
        st.subheader(f"🔍 Preview: {file.name}")  # Display a subheader
        st.dataframe(df, use_container_width=True)  # Show the file's contents as a table

        # Provide cleaning and transformation options
        with st.expander(f"🧹 Clean & Transform - {file.name}"):  # Add expandable section for cleaning options
            # Option to fill missing values with the mean of numeric columns
            if st.checkbox(f"✨ Fill missing values", key=f"fillna_{file.name}"):
                df.fillna(df.select_dtypes(include=["number"]).mean(), inplace=True)  # Fill missing numeric values with the column mean
                st.success("✅ Missing values filled!")  # Show success message
                st.dataframe(df, use_container_width=True)  # Show updated DataFrame

            # Option to remove duplicate rows
            if st.checkbox(f"🧽 Remove duplicates", key=f"dropdup_{file.name}"):
                before = len(df)  # Record the number of rows before removing duplicates
                df.drop_duplicates(inplace=True)  # Remove duplicate rows
                after = len(df)  # Record the number of rows after removing duplicates
                st.info(f"🧼 Removed {before - after} duplicates.")  # Show how many duplicates were removed

            # Option to rename columns
            if st.checkbox(f"✏️ Rename columns", key=f"rename_{file.name}"):
                for col in df.columns:  # Loop through all columns
                    new_name = st.text_input(f"✏️ Rename column '{col}'", value=col, key=f"rename_{col}_{file.name}")  # Ask for new column name
                    if new_name != col:  # If the new name is different from the old name
                        df.rename(columns={col: new_name}, inplace=True)  # Rename the column

        st.markdown("---")  # Add a separator line

        # If the DataFrame contains numeric data, create a chart
        if not df.select_dtypes(include="number").empty:
            st.subheader("📊 Auto Chart")  # Add a subheader for the chart section
            # Create a bar chart using Altair, plotting numeric data
            chart = alt.Chart(df.reset_index()).mark_bar().encode(
                x=alt.X(df.select_dtypes(include="number").columns[0], type='quantitative'),  # Use the first numeric column for x-axis
                y=alt.Y(df.select_dtypes(include="number").columns[1], type='quantitative') if len(df.select_dtypes(include="number").columns) > 1 else alt.Y("index", type='ordinal')  # Use second numeric column for y-axis, or index if only one numeric column
            )
            st.altair_chart(chart, use_container_width=True)  # Display the chart

        # Provide download options for the processed file
        st.subheader("⬇️ Download Processed File")  # Add a subheader for the download section
        # Radio buttons to choose the format for downloading (CSV, Excel, JSON)
        format_choice = st.radio(f"🧾 Convert {file.name} to:", ["CSV", "Excel", "JSON"], key=f"format_{file.name}")

        output = BytesIO()  # Create an in-memory byte stream to save the output file
        # Depending on the user's format choice, convert and save the file
        if format_choice == "CSV":
            df.to_csv(output, index=False)  # Convert DataFrame to CSV
            mime = "text/csv"
            new_name = file.name.replace(ext, "csv")  # Create new filename with .csv extension
        elif format_choice == "Excel":
            df.to_excel(output, index=False, engine='openpyxl')  # Convert DataFrame to Excel
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            new_name = file.name.replace(ext, "xlsx")  # Create new filename with .xlsx extension
        else:
            df.to_json(output, orient="records")  # Convert DataFrame to JSON
            mime = "application/json"
            new_name = file.name.replace(ext, "json")  # Create new filename with .json extension

        output.seek(0)  # Move the file pointer to the start of the output
        # Button to trigger file download
        if st.button(f"🎉 Generate & Download {new_name}", key=f"download_{file.name}"):
            with st.spinner("Generating file... 🎬✨"):  # Show a loading spinner
                time.sleep(1.5)  # Simulate file generation time
                st.balloons()  # Show celebration balloons when the file is ready
                st.download_button(f"📥 Download {new_name}", file_name=new_name, mime=mime, data=output)  # Provide download button
                st.success("✅ File ready for download! 🎊")  # Show success message

# Footer section with credits
st.markdown("""
    <div class='footer'>
        <span class='footer-emoji'>💡</span> Made with ❤️ using <strong>Streamlit</strong> & <strong>Python</strong> <span class='footer-emoji'>🐍</span><br>
        Developed by <strong>Muhammad Hammad Zubair</strong> <span class='footer-emoji'>🚀</span>
    </div>
""", unsafe_allow_html=True)  # Footer with emojis and developer credits
