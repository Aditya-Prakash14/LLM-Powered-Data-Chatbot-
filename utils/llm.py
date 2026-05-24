import os
import re
import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from anthropic import Anthropic
from openai import OpenAI
from utils.data_loader import get_dataset_json, get_dataset_stats_summary

def get_system_prompt(df) -> str:
    """Generates the unified system prompt with the dataset JSON and descriptive stats injected."""
    dataset_json = get_dataset_json(df)
    dataset_summary = get_dataset_stats_summary(df)
    
    prompt = f"""You are a smart, professional data analyst assistant. You are analyzing a structured dataset.

Here is the full dataset in JSON format:
{dataset_json}

Here is a quick summary of the dataset schema and basic statistics:
{dataset_summary}

When the user asks a question:
1. Analyze the data carefully, compute the correct answers, and provide a clear, concise explanation.
2. Always refer to specific numbers and details from the dataset.
3. If asked about trends, compare relevant segments (e.g. months, categories).
4. Keep explanations clear and readable. If a question is simple, keep the answer under 5 sentences unless a detailed breakdown is requested.
5. If the user explicitly asks to visualize, chart, plot, or graph something, or if the question directly requires a visual representation, append a structured JSON block at the very end of your response inside a markdown code block tagged with `[CHART_DATA]`:
```[CHART_DATA]
{{
  "type": "bar" | "line" | "scatter" | "pie",
  "title": "A descriptive title for the chart",
  "labels": ["Label1", "Label2", ...],
  "values": [Value1, Value2, ...],
  "label": "Y-axis or Metric Label"
}}
```

Ensure that:
- The `labels` array contains the strings/categories for the X-axis (e.g. months "Jan", "Feb" or categories).
- The `values` array contains corresponding numeric values for the Y-axis.
- The `type` is exactly one of "bar", "line", "scatter", "pie".
- The `[CHART_DATA]` block is at the absolute end of your response, starting with ```[CHART_DATA] and ending with ```.
- Only generate the chart block when visual rendering is requested or strongly implied.
"""
    return prompt

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

def test_gemini_key(api_key: str) -> bool:
    """Tests if a Gemini API key is valid."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        model.generate_content("test", generation_config={"max_output_tokens": 5})
        return True
    except Exception:
        return False

def test_anthropic_key(api_key: str) -> bool:
    """Tests if an Anthropic API key is valid."""
    try:
        client = Anthropic(api_key=api_key)
        client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=5,
            messages=[{"role": "user", "content": "test"}]
        )
        return True
    except Exception:
        return False

def test_openai_key(api_key: str) -> bool:
    """Tests if an OpenAI API key is valid."""
    try:
        client = OpenAI(api_key=api_key)
        client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=5,
            messages=[{"role": "user", "content": "test"}]
        )
        return True
    except Exception:
        return False

def query_gemini(api_key: str, df, messages: List[Dict[str, str]]) -> str:
    """Sends the conversation history and dataset context to Gemini API."""
    genai.configure(api_key=api_key)
    system_prompt = get_system_prompt(df)
    
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=system_prompt
    )
    
    contents = []
    for msg in messages:
        role = 'user' if msg['role'] == 'user' else 'model'
        contents.append({"role": role, "parts": [msg['content']]})
        
    response = model.generate_content(contents)
    return response.text

def query_anthropic(api_key: str, df, messages: List[Dict[str, str]]) -> str:
    """Sends the conversation history and dataset context to Anthropic Claude API."""
    client = Anthropic(api_key=api_key)
    system_prompt = get_system_prompt(df)
    
    claude_messages = []
    for msg in messages:
        role = 'user' if msg['role'] == 'user' else 'assistant'
        claude_messages.append({"role": role, "content": msg['content']})
        
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        system=system_prompt,
        messages=claude_messages
    )
    return response.content[0].text

def query_openai(api_key: str, df, messages: List[Dict[str, str]]) -> str:
    """Sends the conversation history and dataset context to OpenAI GPT API."""
    client = OpenAI(api_key=api_key)
    system_prompt = get_system_prompt(df)
    
    openai_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        role = 'user' if msg['role'] == 'user' else 'assistant'
        openai_messages.append({"role": role, "content": msg['content']})
        
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=2000,
        messages=openai_messages
    )
    return response.choices[0].message.content
