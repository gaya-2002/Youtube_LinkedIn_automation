from pydantic import BaseModel

from src.crews.postcrew.postcrew import postcrew
from src.crews.feedbackcrew.feedbackcrew import feedbackcrew
from dotenv import load_dotenv
from pathlib import Path
from src.state.memory import SharedState




load_dotenv()


class youtubeautomationFlow:
    
    def __init__(self,id):
        self.state = SharedState()
        self.chat_id=id

    def generate_blog(self, sent_url: str):

        print(f"Generating blog and post from url {sent_url}")
        self.state.set(self.chat_id,"youtube_url",f"{sent_url['url']}")
        print(self.state.get(self.chat_id,"youtube_url"))
        crew = postcrew(self.state,self.chat_id)
        inputs={
            "url": self.state.get("youtube_url")
        }
        crew.crew().kickoff(inputs)
        return "Completed preparing post"
    
    def regenerate_content(self, prompt: str):

        print("Regenrating the post using user prompt")
        self.state.set(self.chat_id,"prompt",f"{prompt['prompt']}")
        print(self.state.get(self.chat_id,"prompt"))
        crew = feedbackcrew(self.state,self.chat_id)
        with open(self.state.get("post_output"),"r",encoding="utf-8") as f:
            self.post=f.read()
        print(self.post)
        inputs = {
            "post": self.post
        }

        regenerate_crew = crew.crew().kickoff(inputs)
        print(f"regenerate Crew: {regenerate_crew}")
        return regenerate_crew

