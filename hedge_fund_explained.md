# Understanding `hedge_fund.py`

This guide explains what the `hedge_fund.py` script does, step-by-step.

## Does it use the internet?
**No.** This script currently relies **100% on the internal knowledge of the AI model (Gemini)**.

Unlike `rates_strategist_crew.py`, which you set up with `SerperDevTool` (Google Search) and `ScrapeWebsiteTool`, the agents in `hedge_fund.py` have **no tools assigned to them**.

When the analyst is asked to "Analyze the impact of 'AI Regulation' on Tech Stocks", it is using its training data (which cuts off at a certain date depending on the model version) and general reasoning capabilities. It is **not** looking up today's news.

---

## Step-by-Step Breakdown

### 1. Setup & Configuration
```python
import os
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = "NA"
my_llm = "gemini/gemini-3-flash-preview"
```
- **Imports**: Loads the CrewAI framework and environment tools.
- **API Keys**: Loads your keys. The `OPENAI_API_KEY = "NA"` line is a hack to stop CrewAI from crashing because it expects an OpenAI key by default, even though we are using Google Gemini.
- **Model**: Sets the AI model to `gemini-3-flash-preview`.

### 2. The Agents (The "Employees")
```python
analyst = Agent(
    role='Senior Macro Analyst',
    goal='Analyze market sentiment',
    backstory="You are a veteran macro strategist...",
    verbose=True,
    llm=my_llm,
    allow_delegation=False
)

trader = Agent(
    role='Head of Execution',
    goal='Execute profitable trades',
    backstory="You are a disciplined trader...",
    verbose=True,
    llm=my_llm,
    allow_delegation=False
)
```
- **Analyst**: Designed to think like a strategist.
- **Trader**: Designed to take the analyst's output and make a decision.
- **Crucial Detail**: Notice there is no `tools=[]` argument here. This confirms they cannot browse the web.

### 3. The Tasks (The "Work")
```python
current_date = datetime.now().strftime("%Y-%m-%d")

task_analysis = Task(
    description=f"Analyze the impact of 'AI Regulation' on Tech Stocks. Today is {current_date}.",
    expected_output="A risk assessment report.",
    agent=analyst,
    output_file='outputs/analysis_report.md'
)

task_trade = Task(
    description=f"Based on the analysis, propose a trade (Buy/Sell/Hold). Today is {current_date}.",
    expected_output="A structured trade plan.",
    agent=trader,
    output_file='outputs/trade_plan.md'
)
```
- **Dynamic Date**: We inject `Today is 2026-02-07` so the AI knows the date context, even if it can't search for news.
- **Task 1 (Analysis)**: The Analyst writes a report based on its internal knowledge of AI regulation trends.
- **Task 2 (Trade)**: The Trader takes the Analyst's report and turns it into a trade plan.

### 4. The Crew (The "Team")
```python
hedge_fund_crew = Crew(
    agents=[analyst, trader],
    tasks=[task_analysis, task_trade],
    verbose=True,
    process=Process.sequential,
    manager_llm=my_llm
)
```
- **Sequential Process**: This means Task 1 happens first, and its output is automatically passed to Task 2. The Trader effectively "reads" the Analyst's report before working.

### 5. Execution & Saving
```python
result = hedge_fund_crew.kickoff()

filename = f"outputs/trade_plan_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.md"
with open(filename, "w") as file:
    file.write(result.raw)
```
- **Kickoff**: Starts the AI agents.
- **Saving**: Writes the final result to the `outputs/` folder with a timestamped filename.
