import requests
import json
import re
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_analysis_commands(question, columns, sample_rows):
    
    prompt = f"""Columns: {columns}
Sample Rows: {sample_rows}
Question: {question}

You MUST respond with ONLY a valid JSON dictionary in this exact format:
{{"pandas": "your pandas command here", "matplotlib": "your matplotlib code here"}}

CRITICAL RULES for pandas commands:
1. MUST be a valid Python expression that can be evaluated
2. Use 'df' as the DataFrame variable name
3. Examples of VALID commands:
   - "df['category'].value_counts()"
   - "df['value'].mean()"
   - "df.groupby('category')['value'].sum()"
   - "df[df['value'] > 10]"
4. Do NOT include print statements
5. Do NOT include assignment statements (like 'result = ...')
6. Do NOT include comments

For matplotlib code:
1. Use the existing 'df' DataFrame
2. Include plt.show() or plt.savefig() at the end
3. Set appropriate labels and titles
4. If visualization is NOT possible, set matplotlib to empty string: ""

Examples:
For count question: 
{{"pandas": "df['category'].value_counts()", "matplotlib": "plt.figure(figsize=(10,6)); df['category'].value_counts().plot(kind='bar'); plt.title('Distribution by Category'); plt.xlabel('Category'); plt.ylabel('Count'); plt.xticks(rotation=45); plt.tight_layout()"}}

For mean question: 
{{"pandas": "df['value'].mean()", "matplotlib": "plt.figure(figsize=(8,6)); plt.hist(df['value'], bins=20, edgecolor='black'); plt.title('Value Distribution'); plt.xlabel('Value'); plt.ylabel('Frequency'); plt.grid(True, alpha=0.3)"}}

Return ONLY the JSON dictionary, no other text."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 500
    }

    try:
        response = requests.post(GROQ_URL, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            try:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group()
                commands = json.loads(content)
                
                if 'pandas' not in commands:
                    commands['pandas'] = ''
                if 'matplotlib' not in commands:
                    commands['matplotlib'] = ''
                
                pandas_cmd = commands['pandas']
                pandas_cmd = re.sub(r'^```python\s*', '', pandas_cmd)
                pandas_cmd = re.sub(r'\s*```$', '', pandas_cmd)
                pandas_cmd = pandas_cmd.strip()
                
                if pandas_cmd.startswith('print('):
                    import_match = re.search(r'print\((.*)\)', pandas_cmd)
                    if import_match:
                        pandas_cmd = import_match.group(1)
                
                commands['pandas'] = pandas_cmd
                    
                return commands
            except json.JSONDecodeError:
                return {
                    'pandas': content.strip(),
                    'matplotlib': ''
                }
        else:
            return {
                'pandas': f"Error: {response.status_code}",
                'matplotlib': ''
            }
            
    except Exception:
        return {
            'pandas': "Error: Failed to get response from LLM",
            'matplotlib': ''
        }