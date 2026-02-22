# Rates Strategist Crew (`rates_strategist_crew.py`) Explained

This document provides a comprehensive breakdown of how the `rates_strategist_crew.py` script works, its inputs, and how it leverages the **CrewAI** agentic framework to perform autonomous financial research and analysis.

---

## 1. High-Level Summary: What Does It Do?

The script simulates a micro-hedge fund research team specializing in macroeconomic analysis. Its primary goal is to **analyze US Treasury yield curve shifts, interpret Federal Reserve communications ("Fed speak"), and predict the impact on global assets (like USD/JPY and Gold).**

When you run the script, it:
1.  **Searches the live internet** for today's 2-Year and 10-Year Treasury yields.
2.  **Scrapes the official Federal Reserve website** to read the latest speeches and policy notes.
3.  **Analyzes this combined data** to formulate a technical memo.
4.  **Hands off that memo** to a second agent, who uses it to create a specific multi-asset trading outlook.
5.  **Saves the final output** in a timestamped markdown report in the `rates/` folder, while keeping a precise audit log of every URL it visited in `rates/sources_log.txt`.

---

## 2. The Agentic Framework (CrewAI)

The script uses **CrewAI**, a framework designed to make AI models work together like a real human team. In an agentic framework, you give the AI a role, a set of tools, and an objective, and it figures out *how* to achieve that objective autonomously.

There are four core pillars of the CrewAI framework used in this script:

### A. Tools (The Agent's "Hands")
Agents cannot access the internet out-of-the-box. We give them tools.
*   **`LoggedSearchTool` (SerperDevTool):** Allows the agent to use Google Search. We wrapped it in a custom class so that every time the agent searches for something, the exact query is silently logged to `rates/sources_log.txt`.
*   **`LoggedScrapingTool` (ScrapeWebsiteTool):** Allows the agent to read the full HTML text of any specific webpage URL it finds. This is also wrapped to log the URL.

### B. Agents (The "Employees")
Agents define *who* is doing the work. They are given distinct personalities and domain expertise, which shapes how the underlying LLM (Gemini) generates text.

1.  **Lead Rates Strategist:**
    *   **Role:** The deep-in-the-weeds data analyst.
    *   **Backstory:** "Former G-10 Rates Trader... looks for 'Quantamental' signals."
    *   **Tools:** Search and Scraping. 
    *   **Job:** Go get the raw yield data, read the boring Fed speeches, and synthesize them into a curve analysis.
2.  **Systematic Macro Analyst:**
    *   **Role:** The big-picture strategist.
    *   **Backstory:** "Focus on how US Treasury yields drive global flows."
    *   **Tools:** Search and Scraping.
    *   **Job:** Take the Strategist's memo and figure out how it affects Gold and the US Dollar.

### C. Tasks (The "To-Do List")
Tasks define *what* needs to be done. They are assigned to specific agents.
*   **`task_yield_analysis`:** Explicitly tells the Rates Strategist to use its tools to find yields and scrape the Fed's URL. The expected output is a "technical memo".
*   **`task_macro_outlook`:** Tells the Macro Analyst to take the first task's output and create a strategy report for Gold and USD/JPY.

### D. The Crew (The "Manager")
The `Crew` binds everything together.
*   It takes the list of agents and tasks.
*   `process=Process.sequential` tells the Crew: "The Rates Strategist must finish `task_yield_analysis` completely before the Macro Analyst is allowed to start `task_macro_outlook`."

---

## 3. The Inputs

The script relies on a few key inputs to function correctly:

1.  **API Keys (via `.env`):**
    *   `GEMINI_API_KEY`: Powers the "brain" of the agents (using `gemini-flash-latest`).
    *   `SERPER_API_KEY`: Powers the Google Search tool.
    *   *(Note: `OPENAI_API_KEY = "NA"` is just a hack to prevent CrewAI from crashing, as it natively expects OpenAI even when we use Gemini).*
2.  **Hardcoded URLs:** The Federal Reserve Speeches page (`https://www.federalreserve.gov/newsevents/speeches.htm`) is explicitly provided in the task description.
3.  **Timestamp (`current_date`):** The script injects Python's `datetime.now()` into the prompt. This solves the "knowledge cutoff" problem. By telling the agent "Today is Feb 7, 2026," the agent knows exactly what timeframe of news to search for.

---

## 4. Why This Approach is Powerful

If you just asked standard ChatGPT: *"What's the macro outlook based on today's Fed speeches?"* it might hallucinate or give you outdated information. 

By using an **Agentic Framework**, the LLM is forced to:
1.  Realize it doesn't know the answer.
2.  Write a search query.
3.  Read the search snippets.
4.  Decide which exact URL to scrape to read the full speech.
5.  Extract the relevant quotes.
6.  Pass that verified data to a distinct "persona" for final synthesis.

And because we implemented the custom `Logged` tools, you maintain a 100% transparent audit trail (`sources_log.txt`) of exactly how the AI arrived at its conclusions.
