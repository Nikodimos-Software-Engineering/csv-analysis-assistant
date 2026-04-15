from fastapi import FastAPI, UploadFile, File, Form
from typing import List, Dict, Any
import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
import numpy as np

from llm_client import get_analysis_commands
from pandas_runner import PandasRunner

app = FastAPI()

def generate_visualization(matplotlib_code, df, execution_result):

    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        local_vars = {
            'df': df,
            'plt': plt,
            'pd': pd,
            'np': np,
            'ax': ax,
            'fig': fig,
            'result': execution_result.get('result')
        }
        
        exec(matplotlib_code, {"__builtins__": {}}, local_vars)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        
        image_base64 = base64.b64encode(buf.read()).decode()
        plt.close(fig)
        
        return image_base64
        
    except Exception as e:
        print(f"Visualization error: {e}")
        return None

@app.post("/analyze-with-file")
async def analyze_with_file(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        columns = df.columns.tolist()
        sample_rows = df.head(3).to_dict('records')
        
        commands_dict = get_analysis_commands(question, columns, sample_rows)
        
        print(f"Commands dict: {commands_dict}")
        
        if not commands_dict:
            return {
                'success': False,
                'error': 'Failed to get commands from LLM',
                'result': None,
                'visualization': None,
                'pandas_command': None,
                'matplotlib_code': None
            }
        
        pandas_command = commands_dict.get('pandas', '')
        matplotlib_code = commands_dict.get('matplotlib', '')
        
        print(f"Pandas command: {pandas_command}")
        print(f"Matplotlib code: {matplotlib_code}")
        
        runner = PandasRunner(df)
        execution_result = runner.execute_command(pandas_command)
        
        if not execution_result['success']:
            return {
                'success': False,
                'error': execution_result['error'],
                'result': None,
                'visualization': None,
                'pandas_command': pandas_command,
                'matplotlib_code': matplotlib_code
            }
        
        visualization_base64 = None
        if matplotlib_code and matplotlib_code.strip():
            visualization_base64 = generate_visualization(
                matplotlib_code, 
                df, 
                execution_result
            )
            if not visualization_base64:
                matplotlib_code = "Failed to generate visualization"
        
        response_data = {
            'success': True,
            'result': execution_result['result'],
            'visualization': visualization_base64,
            'pandas_command': pandas_command,
            'matplotlib_code': matplotlib_code if matplotlib_code else "No visualization generated",
            'error': None
        }
        
        return response_data
        
    except Exception as e:
        print(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'result': None,
            'visualization': None,
            'pandas_command': None,
            'matplotlib_code': None
        }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}