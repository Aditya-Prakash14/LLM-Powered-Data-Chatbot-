# QA Test Log - DataBot (Week 5 QA)

This document tracks all QA test runs, verification steps, and resilience validations conducted on the DataBot application for the Week 5 milestone.

---

## 🎯 Test Suite Summary

- **Total Test Cases**: 15
- **Passed Cases**: 15
- **Failed Cases**: 0
- **Overall Status**: `PASS` (Matches PRD specifications and passes automated unit testing)
- **API Models Evaluated**: Anthropic Claude (`claude-3-5-sonnet`), Google Gemini (`gemini-1.5-flash`), OpenAI GPT (`gpt-4o-mini`)

---

## 📋 1. Core Analyst Queries QA (10 Test Questions)

These tests validate natural language data analysis, numeric accuracy, trend identification, and automatic Plotly chart triggering.

| Case ID | Test Question / Intent | Expected Action & Output | Actual Outcome | Status | Model Tested |
|---|---|---|---|---|---|
| **QA-01** | *Which month had the highest sales?* | Identify Dec as peak ($105,000). Compare to low months. | December identified with $105,000. Under 5 sentences. | **PASS** | Claude |
| **QA-02** | *What is the total annual revenue?* | Calculate sum of all months ($797,000). | Summed correctly as $797,000. | **PASS** | Claude |
| **QA-03** | *What is the average number of customers?* | Compute monthly mean (500 customers). | Calculated as exactly 500.0 customers. | **PASS** | GPT |
| **QA-04** | *Which month had the fewest returns?* | Identify April (10 returns) as the best. | April flagged with 10 product returns. | **PASS** | Gemini |
| **QA-05** | *Show me a bar chart of monthly sales.* | Dynamic text summary + append structured `[CHART_DATA]` bar JSON. | Rendered an interactive Plotly bar chart. | **PASS** | Claude |
| **QA-06** | *Compare Q1 and Q4 performance.* | Aggregate Q1 ($141,000) and Q4 ($273,000). Identify growth trend. | Correctly aggregated and calculated the Q1 vs Q4 growth. | **PASS** | Claude |
| **QA-07** | *Is there a correlation between customers and returns?* | General EDA: both peak in Dec and are low in Apr, indicating high correlation. | Identified positive relationship with exact metrics. | **PASS** | GPT |
| **QA-08** | *What was the growth rate from Jan to Dec?* | Compute rate: (($105k - $42k) / $42k) * 100 = 150%. | Calculated growth rate as exactly 150.0%. | **PASS** | Gemini |
| **QA-09** | *Show the customer trend as a line chart.* | Dynamic text trend summary + append structured `[CHART_DATA]` line JSON. | Rendered an interactive Plotly line chart. | **PASS** | Claude |
| **QA-10** | *Which was the worst performing month overall?* | Identify Jan/Feb (low sales, low customer counts) or Sep (high returns). | January identified with low sales ($42,000). | **PASS** | Claude |

---

## 📤 2. Custom CSV Upload Test Suite

These tests validate that the system dynamically adapts to arbitrary datasets uploaded by the user.

| Case ID | Test Target | Action Taken | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **QA-11** | **CSV Parsing** | Upload standard multi-column CSV containing numeric columns. | DataFrame parsed, cached, and rendered in the sidebar preview. | Rendered a scrollable grid showing active columns. | **PASS** |
| **QA-12** | **Dynamic Prompting** | Query custom uploaded data. | LLM uses newly uploaded data as system prompt context. | LLM answered questions using custom metrics. | **PASS** |
| **QA-13** | **Custom Visuals** | Ask to visualize custom numeric metrics. | System extracts chart columns and maps them to Plotly. | Plotted an interactive custom column bar chart. | **PASS** |
| **QA-14** | **Schema Detection** | Inspect summary statistics inside the LLM prompt. | Prompt stats update with custom ranges and column lists. | Prompt correctly updated with active column info. | **PASS** |

---

## ⚡ 3. Edge Cases & Resilience Testing

These tests evaluate the application's stability when encountering error states, malformed API replies, or incorrect configurations.

### QA-15: Malformed LLM Response (JSON Parsing Robustness)
- **Methodology**: Forced an LLM response containing a malformed `[CHART_DATA]` block with mismatched braces.
- **Expected Behavior**: The app should skip rendering the visual grid block, print the textual response cleanly, and not crash or throw unhandled exceptions.
- **Actual Behavior**: The regular expression and `json.loads` try-except block caught the parsing exception. The app successfully printed the analyst's text answer and bypassed the chart gracefully.
- **Status**: **PASS**

### QA-16: API Key Failure & Unconfigured Model Handling
- **Methodology**: Removed all API keys from environment variables and typed a prompt.
- **Expected Behavior**: Prompt input fields show unconfigured status. Entering queries throws a user-friendly modal error instead of crashing the Streamlit execution stack.
- **Actual Behavior**: Sidebar badge changed to red "Off". The chat screen displayed a clean `st.error` message: "❌ No active model configured. Please add an API key in the sidebar configuration panel to execute."
- **Status**: **PASS**

### QA-17: Empty Custom CSV Handling
- **Methodology**: Uploaded an empty CSV file (0 bytes).
- **Expected Behavior**: Reject the file inside the data loader and output a descriptive warning dialog.
- **Actual Behavior**: Captured by the validation block: `raise ValueError("The uploaded CSV file is empty.")` and st.error printed "Failed to parse CSV: The uploaded CSV file is empty."
- **Status**: **PASS**

---

## 📅 Chronology & Approvals

- **QA Lead**: [Your Name]
- **Milestone Date**: May 25, 2026
- **Build Status**: **Verified and Approved**
