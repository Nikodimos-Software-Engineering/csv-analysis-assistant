import streamlit as st
import requests
import pandas as pd
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import os

load_dotenv()

SERVER_URL = os.getenv("BACKEND_SERVER_URL")
if not SERVER_URL:
    SERVER_URL = "http://localhost:8000"

st.set_page_config(page_title="CSV Analysis Assistant", layout="wide")

st.title("CSV Analysis Assistant")
st.caption("Upload your CSV file and Ask any Analytical Questions")

@st.cache_data
def load_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    return {
        'df': df,
        'columns': df.columns.tolist(),
        'sample_rows': df.head(3).to_dict('records')
    }

uploaded_file = st.file_uploader("Choose a file", type=['csv'])

if uploaded_file is not None:
    data = load_csv(uploaded_file)
    st.success(f"✅ Loaded {len(data['df'])} rows, {len(data['columns'])} columns")
    
    query_question = st.text_input("Ask your question", placeholder="How many text does each category have?")
    
    if st.button("Analyze", type="primary") and query_question:
        with st.spinner("Analyzing your data..."):
            files = {'file': uploaded_file.getvalue()}
            response = requests.post(
                f"{SERVER_URL}/analyze-with-file",
                files=files,
                data={'question': query_question}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result['success']:
                    st.subheader("📊 Analysis Result")
                    if isinstance(result['result'], dict):
                        # Display as simple text/JSON
                        st.json(result['result'])
                    elif isinstance(result['result'], (int, float)):
                        st.metric("Result", result['result'])
                    else:
                        st.write(result['result'])
                    
                    st.subheader("📈 Visualization")
                    if result.get('visualization'):
                        try:
                            image = Image.open(BytesIO(base64.b64decode(result['visualization'])))
                            st.image(image, width=700)
                        except Exception as e:
                            st.error(f"Failed to display visualization: {e}")
                    else:
                        st.info("⚠️ Cannot generate visualization for this query")
                    
                    with st.expander("View Generated Code"):
                        st.code(f"# Pandas Command\n{result.get('pandas_command', 'N/A')}", language='python')
                        st.code(f"# Matplotlib Code\n{result.get('matplotlib_code', 'N/A')}", language='python')
                else:
                    st.error(f"Analysis failed: {result.get('error')}")
            else:
                st.error(f"Backend error: {response.status_code}")