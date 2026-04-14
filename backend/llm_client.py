import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_analysis_commands(question, columns, sample_rows):
    
    prompt = f"""Columns: {columns}
Sample Rows: {sample_rows}
Question: {question}

You MUST respond with ONLY a valid JSON dictionary in this exact format:
{{"pandas": "your pandas command here", "matplotlib": "your matplotlib code here"}}

Rules:
1. ALWAYS include both pandas and matplotlib keys
2. If visualization is NOT possible, set matplotlib to empty string: ""
3. For count/distribution questions, create a bar chart or pie chart
4. For numeric questions, create a histogram or box plot
5. Return ONLY the JSON, no other text

Examples:
For count question: {{"pandas": "df['category'].value_counts()", "matplotlib": "plt.figure(figsize=(10,6)); df['category'].value_counts().plot(kind='bar'); plt.title('Distribution'); plt.xticks(rotation=45); plt.tight_layout()"}}

For mean question: {{"pandas": "df['age'].mean()", "matplotlib": "plt.figure(figsize=(8,6)); plt.hist(df['age'], bins=20, edgecolor='black'); plt.title('Age Distribution'); plt.xlabel('Age'); plt.ylabel('Frequency'); plt.grid(True, alpha=0.3)"}}

Return ONLY the JSON dictionary, no other text."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 500
    }

    try:
        response = requests.post(GROQ_URL, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            print(f"Raw LLM response: {content}")
            
            # Try to parse as JSON
            try:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group()
                commands = json.loads(content)
                
                # Ensure both keys exist
                if 'pandas' not in commands:
                    commands['pandas'] = ''
                if 'matplotlib' not in commands:
                    commands['matplotlib'] = ''
                    
                return commands
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                return {
                    'pandas': content.strip(),
                    'matplotlib': ''
                }
        else:
            print(f"API error: {response.status_code} - {response.text}")
            return {
                'pandas': f"Error: {response.status_code}",
                'matplotlib': ''
            }
            
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}")
        return {
            'pandas': f"Error: {str(e)}",
            'matplotlib': ''
        }