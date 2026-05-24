import os
import re
import json
from typing import List, Dict, Any, Optional
from groq import Groq
from utils.data_loader import get_dataset_json, get_dataset_stats_summary

def get_system_prompt(df) -> str:
    """Generates a compact system prompt with the dataset info (optimized for token limits)."""
    try:
        # Create a compact representation of the dataset
        dataset_info = []
        
        # Check if this is the default dataset or a custom one
        if 'month' in df.columns:
            # Default retail dataset format
            for _, row in df.iterrows():
                dataset_info.append(f"{row['month']}: ${row['sales']:,} sales, {row['customers']} customers, {row['returns']} returns")
        else:
            # Custom dataset - use first few rows as examples
            for idx, (_, row) in enumerate(df.head(5).iterrows()):
                row_str = ", ".join([f"{col}: {row[col]}" for col in df.columns])
                dataset_info.append(f"Row {idx+1}: {row_str}")
            if len(df) > 5:
                dataset_info.append(f"... and {len(df) - 5} more rows")
        
        dataset_summary = f"Dataset has {len(df)} rows, {len(df.columns)} columns: {', '.join(df.columns)}"
        
        prompt = f"""You are a professional data analyst assistant. Analyze the following dataset and answer questions clearly.

DATASET INFO:
{dataset_summary}

SAMPLE DATA:
{chr(10).join(dataset_info[:10])}

When answering:
1. Use exact numbers from the data.
2. Keep explanations under 5 sentences unless detail is requested.
3. If asked to visualize/chart/plot, append a JSON block at the END:
```[CHART_DATA]
{{"type": "bar|line|scatter|pie", "title": "...", "labels": [...], "values": [...], "label": "..."}}
```
Only include [CHART_DATA] when visualization is requested."""
        return prompt
    except Exception as e:
        # Fallback prompt if something goes wrong
        return f"""You are a professional data analyst. The user has uploaded a dataset with {len(df)} rows and columns: {', '.join(df.columns)}.
Answer questions about this data concisely. If asked to visualize, append [CHART_DATA] JSON block."""

def extract_chart_data(text: str):
    """
    Finds a block starting with ```[CHART_DATA] and ending with ``` inside
    the text. Extracts the JSON, parses it, and returns the cleaned text
    and the parsed chart dictionary.
    """
    pattern = r"```\[CHART_DATA\]\s*(\{.*?\})\s*```"
    match = re.search(pattern, text, re.DOTALL)
    
    # Fallback pattern for raw [CHART_DATA] blocks without code fences
    pattern_loose = r"\[CHART_DATA\]\s*(\{.*?\})"
    if not match:
        match = re.search(pattern_loose, text, re.DOTALL)
        
    if match:
        try:
            chart_json = json.loads(match.group(1).strip())
            # Clean up the text by removing the matched chart data blocks
            cleaned_text = re.sub(pattern, "", text, flags=re.DOTALL).strip()
            cleaned_text = re.sub(pattern_loose, "", cleaned_text, flags=re.DOTALL).strip()
            return cleaned_text, chart_json
        except Exception:
            # If parsing fails, return original text
            return text, None
            
    return text, None

def test_groq_key(api_key: str) -> bool:
    """Tests if a Groq API key is valid."""
    try:
        client = Groq(api_key=api_key)
        client.chat.completions.create(
            model="mixtral-8x7b-32768",
            max_tokens=5,
            messages=[{"role": "user", "content": "test"}]
        )
        return True
    except Exception:
        return False

def query_groq(api_key: str, df, messages: List[Dict[str, str]]) -> str:
    """Sends the conversation history and dataset context to Groq API using Mixtral."""
    client = Groq(api_key=api_key)
    system_prompt = get_system_prompt(df)
    
    # Build messages list with system prompt
    groq_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        role = 'user' if msg['role'] == 'user' else 'assistant'
        groq_messages.append({"role": role, "content": msg['content']})
    
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            max_tokens=2000,
            messages=groq_messages
        )
        return response.choices[0].message.content
    except Exception as e:
        error_str = str(e).lower()
        # Handle rate limit or model decommissioned errors
        if 'rate' in error_str or '429' in str(e):
            raise Exception("⏱️ **Rate Limited**: Groq API rate limit reached. Please wait a moment and try again.")
        elif 'decommissioned' in error_str or 'model' in error_str and 'not' in error_str:
            raise Exception("🔄 **Model Issue**: Please wait and try again. If error persists, check Groq console for available models.")
        else:
            raise e
