import pandas as pd
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

class PandasRunner:
    def __init__(self, df):
        self.df = df.copy()
    
    def execute_command(self, pandas_command):
        try:
            local_vars = {'df': self.df, 'pd': pd}
            
            f = io.StringIO()
            with redirect_stdout(f), redirect_stderr(f):
                result = eval(pandas_command, {"__builtins__": {}}, local_vars)
            
            if isinstance(result, pd.DataFrame):
                result_type = 'dataframe'
                output = result.to_dict('records')
            elif isinstance(result, pd.Series):
                result_type = 'series'
                output = result.to_dict()
            else:
                result_type = 'value'
                output = result
            
            return {
                'success': True,
                'result': output,
                'result_type': result_type,
                'stdout': f.getvalue(),
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'result': None,
                'result_type': None,
                'stdout': '',
                'error': str(e)
            }