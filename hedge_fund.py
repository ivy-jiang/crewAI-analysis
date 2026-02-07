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

my_llm = "gemini/gemini-flash-latest"

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
current_date_str = datetime.now().strftime("%Y-%m-%d")
datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M")

# Create a folder for today's run
output_folder = f"outputs/{current_date_str}"
os.makedirs(output_folder, exist_ok=True)

task_analysis = Task(
    description=f"Analyze the impact of recent SaaS selloff on Tech Stocks. How widespread was it, which sectors most affected and which stocks were 'unfairly' impacted? Specifically what do you think about AMZN, GOOGL, META, MSFT, PLTR? Today is {current_date_str}.",
    expected_output="A risk assessment report.",
    agent=analyst,
    output_file=f'{output_folder}/analysis_report_{datetime_str}.md'
)

task_trade = Task(
    description=f"Based on the analysis, propose a trade (Buy/Sell/Hold). Today is {current_date_str}.",
    expected_output="A structured trade plan.",
    agent=trader,
    output_file=f'{output_folder}/trade_plan_{datetime_str}.md'
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
print(f"🚀 Launching Crew with {my_llm}...")
print(f"📂 Saving outputs to: {output_folder}")
result = hedge_fund_crew.kickoff()
print(result)

print(f"✅ Reports saved in {output_folder}")