from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pathlib import Path
from crewai.agents.agent_builder.base_agent import BaseAgent
from dotenv import load_dotenv
from typing import List

load_dotenv()

@CrewBase
class feedbackcrew():

    """feedbackcrew crew"""
    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self,state,id):
        self.state=state
        self.chat_id=id
    
    @agent
    def rewriter(self) -> Agent:
        return Agent(
            config=self.agents_config['rewriter'],
            verbose=True
        )
    
    @task
    def rewrite(self)->Task:
        self.state.set(self.chat_id,'rewritten_post',str(Path(self.state.get("Blog_output")).parent/"rewritten_post.md"))
        return Task(
            config=self.tasks_config['rewrite'],
            output_file=self.state.get(self.chat_id,"rewritten_post")
        )
    
    @crew
    def crew(self)->crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
