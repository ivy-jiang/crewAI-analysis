import os
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from crewai.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field

# 1. Setup Tools
load_dotenv()
os.environ["OPENAI_API_KEY"] = "NA"

# Initialize base tools
base_search_tool = SerperDevTool()
base_scraping_tool = ScrapeWebsiteTool()
base_fed_tool = ScrapeWebsiteTool(website_url='https://www.federalreserve.gov/newsevents/speeches.htm')

# Define Custom Logging Tools as Classes
class LoggedSearchTool(BaseTool):
    name: str = "Logged Search"
    description: str = "Useful to search the internet for a given topic and return relevant results."
    
    def _run(self, query: str) -> str:
        # 1. Log the query
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SEARCH: {query}\n"
        os.makedirs("rates", exist_ok=True)
        with open("rates/sources_log.txt", "a") as f:
            f.write(log_entry)
        
        # 2. Run the actual tool
        return base_search_tool.run(search_query=query)

class LoggedScrapingTool(BaseTool):
    name: str = "Logged Scraper"
    description: str = "Useful to scrape and read the content of a specific website url."
    
    def _run(self, website_url: str) -> str:
        # 1. Log the URL
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SCRAPE: {website_url}\n"
        os.makedirs("rates", exist_ok=True)
        with open("rates/sources_log.txt", "a") as f:
            f.write(log_entry)

        # 2. Run the actual tool
        return base_scraping_tool.run(website_url=website_url)

# Instantiate the tools
logged_search_tool = LoggedSearchTool()
logged_scraping_tool = LoggedScrapingTool()

# 2. Define specialized Macro Agents
rates_strategist = Agent(
    role='Lead Rates Strategist',
    goal='Analyze UST yield curve shifts and Fed expectations',
    backstory="""You are a former G-10 Rates Trader. You specialize in 
    interpreting CPI/NFP data and its impact on the 10Y Treasury yield.
    You look for 'Quantamental' signals.""",
    tools=[logged_search_tool, logged_scraping_tool], # <--- Wrapped tools
    llm="gemini/gemini-flash-latest",
    max_rpm=10, 
    verbose=True
)

macro_analyst = Agent(
    role='Systematic Macro Analyst',
    goal='Identify cross-asset correlations (USD, Gold, Yields)',
    backstory="""You focus on how US Treasury yields drive global flows. 
    You excel at finding divergences between market pricing and Fed dots.""",
    tools=[logged_search_tool, logged_scraping_tool], # <--- Added scraping!
    llm="gemini/gemini-flash-latest",
    max_rpm=10, 
    verbose=True
)

# 3. Targeted Macro Tasks
current_date = datetime.now().strftime("%Y-%m-%d")

task_yield_analysis = Task(
    description=f"""Search for the latest 2Y and 10Y UST yields using the 'Logged Search'. 
    Analyze the current slope of the curve. Scrape the latest 'Fed speak' 
    from the Federal Reserve website (https://www.federalreserve.gov/newsevents/speeches.htm) using the 'Logged Scraper'.
    Today is {current_date}.""",
    expected_output="A technical memo on the UST curve and terminal rate pricing.",
    agent=rates_strategist
)

task_macro_outlook = Task(
    description="Based on the yield analysis, provide a macro outlook for USD/JPY and Gold.",
    expected_output="A multi-asset strategy report.",
    agent=macro_analyst
)

# 4. Execute
macro_crew = Crew(
    agents=[rates_strategist, macro_analyst],
    tasks=[task_yield_analysis, task_macro_outlook],
    process=Process.sequential
)

result = macro_crew.kickoff()
print(result)

# Generate a filename with today's date
filename = f"rates/rates_strategy_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.md"

# Save the result
with open(filename, "w") as file:
    file.write(result.raw) # .raw extracts the clean text

print(f"✅ Report saved to {filename}")