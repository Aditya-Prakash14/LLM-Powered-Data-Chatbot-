import sys
import json
from utils.data_loader import get_default_df, get_dataset_stats_summary, get_dataset_json
from utils.llm import extract_chart_data
from utils.charts import render_plotly_chart

def test_data_manager():
    print("--- Testing Data Manager ---")
    df = get_default_df()
    assert len(df) == 12, f"Expected 12 months, got {len(df)}"
    assert list(df.columns) == ["month", "sales", "customers", "returns"], "Columns mismatch"
    
    summary = get_dataset_stats_summary(df)
    print("Generated summary:")
    print(summary)
    assert "sales" in summary, "Summary should contain sales statistics"
    assert "105,000" in summary, "Summary should contain max sales details"
    
    json_str = get_dataset_json(df)
    data = json.loads(json_str)
    assert len(data) == 12, "JSON export mismatch"
    print("✅ Data Manager tests passed successfully!")

def test_chart_parsing():
    print("\n--- Testing Chart Data Parsing ---")
    
    # 1. Strict pattern test
    raw_text_1 = """Based on the dataset, December had the highest sales of $105,000. Here is a bar chart visualizing this.
```[CHART_DATA]
{
  "type": "bar",
  "title": "Monthly Retail Sales",
  "labels": ["Jan", "Jun", "Dec"],
  "values": [42000, 72000, 105000],
  "label": "Sales in USD"
}
```
Thank you!"""
    
    cleaned_1, chart_1 = extract_chart_data(raw_text_1)
    print("Cleaned text 1:")
    print(cleaned_1)
    print("Chart data 1:", chart_1)
    
    assert "December had the highest sales" in cleaned_1, "Original text missing"
    assert "```[CHART_DATA]" not in cleaned_1, "Chart block not stripped"
    assert chart_1 is not None, "Chart data failed to parse"
    assert chart_1["type"] == "bar", "Chart type mismatch"
    assert chart_1["values"] == [42000, 72000, 105000], "Chart values mismatch"
    
    # 2. Loose pattern test
    raw_text_2 = """Here is the scatter plot.
[CHART_DATA] {"type": "scatter", "title": "Customer Scatter", "labels": [1, 2], "values": [10, 20]}
Let me know if you need more."""
    
    cleaned_2, chart_2 = extract_chart_data(raw_text_2)
    print("Cleaned text 2:")
    print(cleaned_2)
    print("Chart data 2:", chart_2)
    
    assert "Here is the scatter plot." in cleaned_2, "Original text missing"
    assert "[CHART_DATA]" not in cleaned_2, "Loose chart block not stripped"
    assert chart_2 is not None, "Loose chart data failed to parse"
    assert chart_2["type"] == "scatter", "Loose chart type mismatch"
    
    print("✅ Chart Parsing tests passed successfully!")

def test_plotly_rendering():
    print("\n--- Testing Plotly Render Configurations ---")
    
    chart_info = {
        "type": "line",
        "title": "Interactive Line Chart Test",
        "labels": ["A", "B", "C"],
        "values": [10, 25, 15],
        "label": "Metric Test"
    }
    
    fig = render_plotly_chart(chart_info)
    assert fig is not None, "Plotly figure returned None"
    assert fig.layout.title.text == "Interactive Line Chart Test", "Plotly title layout mismatch"
    assert fig.layout.xaxis.showgrid is True, "X-axis grid line deactivated"
    print("✅ Plotly rendering test passed successfully!")

if __name__ == "__main__":
    try:
        test_data_manager()
        test_chart_parsing()
        test_plotly_rendering()
        print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
    except AssertionError as e:
        print(f"\n❌ Assertion Failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}")
        sys.exit(1)
