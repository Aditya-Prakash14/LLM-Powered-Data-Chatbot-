# Product Requirements Document (PRD)
## DataBot — LLM-Powered Data Analyst Chatbot

---

| Field | Details |
|---|---|
| **Project Name** | DataBot — LLM-Powered Data Analyst Chatbot |
| **Role** | Data Analyst Intern |
| **Version** | v1.0 |
| **Status** | In Development |
| **Author** | [Your Name] |
| **Date** | May 2026 |
| **Timeline** | 6 Weeks |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Goals & Objectives](#3-goals--objectives)
4. [Target Users](#4-target-users)
5. [Scope](#5-scope)
6. [Functional Requirements](#6-functional-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [System Architecture](#8-system-architecture)
9. [Tech Stack](#9-tech-stack)
10. [Data Requirements](#10-data-requirements)
11. [Feature Breakdown & User Stories](#11-feature-breakdown--user-stories)
12. [Project Timeline (6 Weeks)](#12-project-timeline-6-weeks)
13. [KPIs & Success Metrics](#13-kpis--success-metrics)
14. [Risks & Mitigations](#14-risks--mitigations)
15. [Out of Scope](#15-out-of-scope)
16. [Deliverables](#16-deliverables)
17. [Appendix](#17-appendix)

---

## 1. Executive Summary

DataBot is a natural language interface built on top of a structured retail sales dataset, powered by a Large Language Model (LLM) API. It allows non-technical business users and analysts to query data, discover insights, and generate visualizations simply by typing plain English questions — without writing a single line of SQL or Python.

This project demonstrates end-to-end data analyst skills including data cleaning, EDA, LLM integration, visualization, and deployment, making it a strong internship portfolio piece.

---

## 2. Problem Statement

Business users and junior analysts often struggle to extract insights from raw datasets because:

- They lack SQL or Python skills to write queries themselves.
- Dashboards are static and cannot answer ad hoc questions.
- Requesting reports from the data team creates bottlenecks and delays.

**DataBot** solves this by enabling anyone to have a conversation with their data using plain English, instantly receiving insights, statistics, and charts.

---

## 3. Goals & Objectives

### Primary Goals

- Build a working chatbot that accepts natural language questions and returns accurate data insights.
- Integrate an LLM API (Claude / OpenAI) with a structured dataset as context.
- Render dynamic visualizations (bar, line charts) based on user queries.

### Secondary Goals

- Allow users to upload their own CSV datasets.
- Provide a clean, shareable web interface built with Streamlit or React.
- Document the full pipeline for reproducibility and portfolio presentation.

### Non-Goals (for v1.0)

- Real-time database connectivity.
- Multi-user authentication.
- Advanced ML predictions.

---

## 4. Target Users

| User Type | Description | Pain Point |
|---|---|---|
| **Business Analyst (intern)** | Analyzing sales data during internship | Slow feedback loop from senior team |
| **Non-technical Manager** | Wants quick answers from monthly reports | Cannot write SQL or use Python |
| **Data Analyst** | Exploring datasets for EDA | Wants faster iteration on ad hoc questions |
| **Student / Intern** | Building a portfolio project | Needs a tangible, deployable AI project |

**Primary User for this project:** Data Analyst Intern (you, the builder and demonstrator).

---

## 5. Scope

### In Scope (v1.0)

- Natural language Q&A over a 12-month retail sales dataset.
- Chart generation (bar and line) triggered by user intent.
- Suggestion prompts for common analyst questions.
- Dataset viewer (expandable table).
- CSV upload for custom datasets.
- Deployable web app (Streamlit or React).

### Out of Scope (v1.0)

- Real-time data feeds or database connections.
- User login and authentication.
- Multi-dataset joins or relational queries.
- Export to PDF or Excel.
- Scheduled report generation.

---

## 6. Functional Requirements

### FR-01: Natural Language Chat Interface

- The system shall accept free-text questions from the user via a chat input box.
- The system shall display messages in a conversation thread (user on right, bot on left).
- The system shall show a loading indicator while the LLM is processing.
- The system shall handle follow-up questions using conversation history.

### FR-02: LLM Integration

- The system shall call the Claude or OpenAI API with a system prompt that includes the full dataset.
- The system shall pass the last N messages as conversation history to maintain context.
- The system shall parse the LLM response to extract both text answers and chart instructions.

### FR-03: Chart Generation

- The system shall detect when the user requests a visualization (keywords: chart, plot, visualize, graph, show me).
- The system shall render a bar chart or line chart inline in the chat based on LLM-returned chart data.
- Charts shall include labels, values, and a title.

### FR-04: Suggestion Prompts

- The system shall display pre-built suggestion buttons for common analyst questions.
- Clicking a suggestion shall auto-send the question to the chatbot.
- Suggestions shall include: best month for sales, trend over time, average customers, Q1 vs Q4 comparison, most returns.

### FR-05: Dataset Viewer

- The system shall display a collapsible table of the full dataset.
- The table shall show month, sales, customers, and returns columns.
- The table shall be read-only.

### FR-06: CSV Upload (v1.1)

- The system shall allow users to upload a custom CSV file.
- The system shall parse and validate the CSV (check for required columns or allow dynamic column detection).
- The system shall replace the default dataset with the uploaded data for the session.

---

## 7. Non-Functional Requirements

### Performance

- LLM response time should be under 5 seconds for typical queries.
- Chart rendering should be near-instantaneous (client-side).

### Usability

- The interface shall be usable without any training or documentation.
- Suggestion prompts shall be visible on first load to guide new users.

### Reliability

- The system shall gracefully handle API errors and display a user-friendly error message.
- The system shall not crash if the LLM returns an unexpected format.

### Security

- The LLM API key shall not be exposed in the frontend code.
- API calls shall be routed through a backend proxy or environment variable (in production).

### Portability

- The project shall be deployable on Streamlit Cloud, Vercel, or Render with minimal configuration.
- A `requirements.txt` (Python) or `package.json` (Node/React) shall be provided.

---

## 8. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    User Interface                   │
│         (React / Streamlit Web App)                 │
│                                                     │
│  ┌──────────────┐   ┌──────────────┐               │
│  │  Chat Input  │   │ Chart Render │               │
│  └──────┬───────┘   └──────▲───────┘               │
│         │                  │                        │
└─────────┼──────────────────┼────────────────────────┘
          │ User Message     │ Chart Data (JSON)
          ▼                  │
┌─────────────────────────────────────────────────────┐
│                  Application Logic                  │
│                                                     │
│  1. Append user message to conversation history     │
│  2. Inject dataset as system prompt context         │
│  3. Call LLM API (Claude / OpenAI)                  │
│  4. Parse response → extract text + CHART_DATA      │
│  5. Render text in chat + chart if detected         │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                  LLM API Layer                      │
│         (Anthropic Claude / OpenAI GPT)             │
│                                                     │
│  System Prompt: Dataset JSON + instructions         │
│  Messages: Full conversation history                │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                   Data Layer                        │
│                                                     │
│  Default: Hardcoded 12-month retail CSV (in-memory) │
│  Optional: User-uploaded CSV (session state)        │
└─────────────────────────────────────────────────────┘
```

---

## 9. Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| **Frontend** | React.js or Streamlit | React for portfolio quality; Streamlit for speed |
| **LLM API** | Anthropic Claude (`claude-sonnet`) | Powerful, large context window |
| **Data Processing** | Python (Pandas) | Industry standard for data analysis |
| **Visualization** | Recharts (React) or Plotly (Streamlit) | Clean, interactive charts |
| **State Management** | React useState / Streamlit session_state | Manage conversation history |
| **Deployment** | Vercel (React) or Streamlit Cloud | Free tier available |
| **Version Control** | GitHub | Portfolio visibility |
| **Documentation** | Markdown + Jupyter Notebook | EDA walkthrough |

---

## 10. Data Requirements

### Default Dataset — Retail Sales (12 Months)

| Column | Type | Description |
|---|---|---|
| `month` | String | Month name (Jan–Dec) |
| `sales` | Integer | Total revenue in USD |
| `customers` | Integer | Number of unique customers |
| `returns` | Integer | Number of product returns |

**Sample Records:**

| month | sales | customers | returns |
|---|---|---|---|
| Jan | 42,000 | 320 | 12 |
| Jun | 72,000 | 530 | 21 |
| Dec | 105,000 | 790 | 31 |

### Dataset Assumptions

- All sales values are in USD.
- The dataset represents a single retail store or product line.
- No missing values in the default dataset.
- For uploaded CSVs: at minimum one numeric column is required.

### Data Sources for Expansion

- [Kaggle — Retail Sales Dataset](https://www.kaggle.com/datasets/manjeetsingh/retaildataset)
- [Kaggle — Superstore Sales](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
- [UCI ML Repository](https://archive.ics.uci.edu/ml/index.php)

---

## 11. Feature Breakdown & User Stories

### Epic 1: Core Chatbot

| ID | User Story | Priority | Status |
|---|---|---|---|
| US-01 | As a user, I want to type a question and receive a text answer from the AI | P0 | Done |
| US-02 | As a user, I want to see a loading indicator while the AI is thinking | P0 | Done |
| US-03 | As a user, I want my conversation history to persist in the session | P1 | Done |
| US-04 | As a user, I want the AI to remember my previous questions | P1 | Done |

### Epic 2: Visualization

| ID | User Story | Priority | Status |
|---|---|---|---|
| US-05 | As a user, I want to say "show me a chart" and see a bar/line chart | P0 | Done |
| US-06 | As a user, I want charts to appear inline in the chat thread | P1 | Done |
| US-07 | As a user, I want charts to be labeled clearly with axis titles | P2 | In Progress |

### Epic 3: Dataset Management

| ID | User Story | Priority | Status |
|---|---|---|---|
| US-08 | As a user, I want to see the full dataset in a collapsible table | P1 | Done |
| US-09 | As a user, I want to upload my own CSV and ask questions about it | P2 | Planned |
| US-10 | As a user, I want the system to detect column names from my CSV automatically | P2 | Planned |

### Epic 4: UX & Polish

| ID | User Story | Priority | Status |
|---|---|---|---|
| US-11 | As a user, I want suggestion buttons to guide me on what to ask | P1 | Done |
| US-12 | As a user, I want to see a clear error message if the API fails | P1 | Done |
| US-13 | As a user, I want to reset the conversation | P2 | Planned |

---

## 12. Project Timeline (6 Weeks)

### Week 1 — Setup & Data Exploration

- Set up GitHub repo and project structure.
- Explore and clean the retail sales dataset in a Jupyter notebook.
- Perform EDA: distributions, trends, correlations.
- Document findings in `EDA.ipynb`.

**Deliverable:** Clean dataset + EDA notebook with 5+ key insights.

---

### Week 2 — LLM Integration (Core Engine)

- Set up API access (Anthropic Claude or OpenAI).
- Write the system prompt that injects the dataset as context.
- Build the basic chat loop: send message → receive response → display.
- Handle conversation history (pass last 10 messages).

**Deliverable:** Working CLI or basic UI chatbot that answers questions.

---

### Week 3 — Chart Generation

- Design the `CHART_DATA:` parsing protocol in the system prompt.
- Implement chart rendering (bar and line) using Recharts or Plotly.
- Test with 10+ chart-triggering prompts and validate output.
- Handle edge cases: missing values, unexpected LLM output format.

**Deliverable:** Chatbot that generates charts on demand.

---

### Week 4 — UI / Frontend Polish

- Build the full chat interface (React or Streamlit).
- Add suggestion prompt buttons.
- Add collapsible dataset viewer.
- Add loading states and error handling.
- Responsive design for different screen sizes.

**Deliverable:** Clean, polished web UI.

---

### Week 5 — CSV Upload & Extended Features

- Implement CSV file upload and parsing.
- Dynamically update the system prompt with user-uploaded data.
- Add column auto-detection and validation.
- Add conversation reset button.
- Performance testing and bug fixes.

**Deliverable:** Working CSV upload feature.

---

### Week 6 — Deployment & Documentation

- Deploy to Vercel (React) or Streamlit Cloud.
- Write `README.md` with setup instructions, screenshots, and demo GIF.
- Record a 2-minute walkthrough video for portfolio.
- Prepare 5-slide summary deck for internship presentation.
- Final testing and bug fixes.

**Deliverable:** Live deployed app + complete documentation.

---

## 13. KPIs & Success Metrics

| Metric | Target | How to Measure |
|---|---|---|
| **Answer Accuracy** | >85% correct answers on test questions | Manual QA with 20 test queries |
| **Response Time** | <5 seconds per query | Browser DevTools network timing |
| **Chart Trigger Rate** | Charts generated for >90% of chart-intent queries | Test with 10 chart prompts |
| **Error Rate** | <5% unhandled errors | App error logging |
| **User Task Completion** | User can answer 5 business questions without help | Usability test with 1 peer |
| **GitHub Stars / Views** | Portfolio visibility | GitHub Insights |

---

## 14. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM API rate limits or costs | Medium | High | Use free tier; cache repeated queries |
| LLM returns malformed CHART_DATA | Medium | Medium | Wrap parsing in try/catch; fallback to text-only |
| API key exposed in frontend | High | High | Use environment variables; backend proxy in production |
| Dataset too small for complex queries | Low | Medium | Use Kaggle dataset (50k+ rows) for advanced version |
| Deployment issues on free tier | Medium | Low | Test locally first; document setup clearly |
| LLM hallucinating wrong numbers | Medium | High | Include exact data in system prompt; validate key answers manually |

---

## 15. Out of Scope

The following features are explicitly excluded from v1.0 to maintain scope and timeline:

- Real-time database connections (PostgreSQL, MySQL, BigQuery).
- User authentication and multi-user sessions.
- Scheduled automated reports.
- Export to PDF, Excel, or PowerPoint.
- Mobile native app (iOS/Android).
- Fine-tuning or custom model training.
- Multi-dataset joins or relational analysis.
- Advanced ML models (forecasting, clustering) beyond basic stats.

These may be considered for a v2.0 roadmap.

---

## 16. Deliverables

### Code & Technical

- [ ] GitHub repository (public, well-documented)
- [ ] `EDA.ipynb` — Exploratory Data Analysis notebook
- [ ] `app.py` or `src/` — Full application source code
- [ ] `requirements.txt` / `package.json` — Dependency file
- [ ] `.env.example` — Environment variable template
- [ ] `README.md` — Setup guide with screenshots

### Documentation

- [ ] This PRD (Product Requirements Document)
- [ ] Architecture diagram
- [ ] API integration guide
- [ ] Known issues & limitations log

### Presentation

- [ ] Live deployed app URL
- [ ] Demo walkthrough video (2 min)
- [ ] Internship presentation deck (5 slides)
- [ ] Portfolio write-up (LinkedIn post or personal site)

---

## 17. Appendix

### A. Sample Test Questions

Use these to validate the chatbot during QA:

1. Which month had the highest sales?
2. What is the total annual revenue?
3. What is the average number of customers per month?
4. Which month had the fewest returns?
5. Show me a bar chart of monthly sales.
6. Compare Q1 and Q4 performance.
7. Is there a correlation between customers and returns?
8. What was the growth rate from January to December?
9. Show the customer trend as a line chart.
10. Which was the worst performing month overall?

---

### B. System Prompt Template

```
You are a smart data analyst assistant. You have access to a retail sales
dataset with monthly data. Here is the full dataset in JSON:

[DATASET_JSON]

When the user asks a question:
1. Analyze the data carefully and give a clear, concise answer.
2. Always mention specific numbers from the data.
3. If asked about trends, compare relevant months.
4. Keep answers under 5 sentences unless detail is requested.
5. If the user asks to visualize something, add at the END of your reply:
   CHART_DATA:{"type":"bar"|"line","labels":[...],"values":[...],"label":"..."}

Only include CHART_DATA when the user explicitly asks to chart or visualize.
```

---

### C. Glossary

| Term | Definition |
|---|---|
| **LLM** | Large Language Model — AI model trained on text (e.g. Claude, GPT) |
| **EDA** | Exploratory Data Analysis — initial investigation of a dataset |
| **System Prompt** | Instructions given to the LLM before the conversation starts |
| **Context Window** | Maximum amount of text the LLM can process in one request |
| **Chart Intent** | When the user's message implies they want a visualization |
| **PRD** | Product Requirements Document — defines what and why to build |
| **KPI** | Key Performance Indicator — measurable success metric |

---

### D. References & Resources

- [Anthropic Claude API Docs](https://docs.anthropic.com)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Recharts Library](https://recharts.org)
- [Kaggle Retail Datasets](https://www.kaggle.com/search?q=retail+sales)
- [Plotly Python Docs](https://plotly.com/python/)

---

*Document version 1.0 · Last updated May 2026 · DataBot Internship Project*
