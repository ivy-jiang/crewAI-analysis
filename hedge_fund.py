import os
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv

# 1. Load variables
load_dotenv()

# --- THE FIX ---
# CrewAI sometimes checks for an OpenAI key even if you aren't using it.
# We set it to "NA" to bypass that check without crashing.
os.environ["OPENAI_API_KEY"] = "NA"

# We define the model as a string. 
# The "gemini/" prefix tells CrewAI to use Google.
# We use 1.5-flash first to GUARANTEE it works, then you can swap to 2.0/3.0.
# TO THIS:
my_llm = "gemini/gemini-3-flash-preview"

# 2. Define Agents (Using the string, not the object)
analyst = Agent(
    role='Senior Macro Analyst',
    goal='Analyze market sentiment',
    backstory="You are a veteran macro strategist. You digest news to find the signal.",
    verbose=True,
    llm=my_llm,  # <--- Pass the string here!
    allow_delegation=False
)

trader = Agent(
    role='Head of Execution',
    goal='Execute profitable trades',
    backstory="You are a disciplined trader. You focus on risk and reward.",
    verbose=True,
    llm=my_llm,  # <--- Pass the string here!
    allow_delegation=False
)

# 3. Define Tasks
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

# 4. Form the Crew
hedge_fund_crew = Crew(
    agents=[analyst, trader],
    tasks=[task_analysis, task_trade],
    verbose=True,
    process=Process.sequential,
    manager_llm=my_llm # <--- Pass the string here too!
)

# 5. Kickoff
print("🚀 Launching Crew with Gemini Flash...")
result = hedge_fund_crew.kickoff()
print(result)

# Add this to the bottom of hedge_fund.py
from datetime import datetime

# Generate a filename with today's date
filename = f"outputs/trade_plan_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.md"

# Save the result
with open(filename, "w") as file:
    file.write(result.raw) # .raw extracts the clean text

print(f"✅ Report saved to {filename}")