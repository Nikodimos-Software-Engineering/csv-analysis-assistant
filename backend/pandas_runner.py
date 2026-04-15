import pandas as pd
import io
import re
from contextlib import redirect_stdout, redirect_stderr

class PandasRunner:
    def __init__(self, df):
        self.df = df.copy()
    
    def clean_pandas_command(self, command):
        if not command or not isinstance(command, str):
            return None
        
        command = re.sub(r'```python\s*', '', command)
        command = re.sub(r'```\s*', '', command)
        command = command.strip()
        
        if command.startswith('print('):
            command = re.search(r'print\((.*)\)', command)
            if command:
                command = command.group(1)
        
        if command in ['df', 'self.df']:
            return 'df'
        
        return command
    
    def execute_command(self, pandas_command):
        try:
            cleaned_command = self.clean_pandas_command(pandas_command)
            
            if not cleaned_command:
                return {
                    'success': False,
                    'result': None,
                    'result_type': None,
                    'stdout': '',
                    'error': 'Empty or invalid pandas command'
                }
            
            local_vars = {'df': self.df, 'pd': pd}
            f = io.StringIO()
            
            with redirect_stdout(f), redirect_stderr(f):
                try:
                    result = eval(cleaned_command, {"__builtins__": {}}, local_vars)
                except SyntaxError:
                    exec(cleaned_command, {"__builtins__": {}}, local_vars)
                    result = local_vars.get('result', None)
                    if result is None:
                        result = "Command executed successfully (no return value)"
            
            if isinstance(result, pd.DataFrame):
                output = result.to_dict('records')
                if len(output) > 100:
                    output = output[:100]
                    output.append({"note": f"Truncated: Showing first 100 of {len(result)} rows"})
            elif isinstance(result, pd.Series):
                output = result.to_dict()
            elif isinstance(result, (int, float, str, bool)):
                output = result
            elif isinstance(result, dict):
                output = result
            elif isinstance(result, list):
                output = result[:100] if len(result) > 100 else result
            else:
                output = str(result)
            
            return {
                'success': True,
                'result': output,
                'result_type': type(result).__name__,
                'stdout': f.getvalue(),
                'error': None
            }
            
        except SyntaxError as e:
            return {
                'success': False,
                'result': None,
                'result_type': None,
                'stdout': '',
                'error': f"Syntax error: {str(e)}. Command was: {pandas_command}"
            }
        except Exception as e:
            return {
                'success': False,
                'result': None,
                'result_type': None,
                'stdout': '',
                'error': f"Execution error: {str(e)}"
            }