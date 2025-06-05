from pydantic import BaseModel

from src.crews.postcrew.postcrew import postcrew
from src.crews.gmailcrew.gmailcrew import GmailCrew
from src.crews.feedbackcrew.feedbackcrew import feedbackcrew
from dotenv import load_dotenv
from pathlib import Path
from src.state.memory import SharedState


import shutil
import os

load_dotenv()


class youtubeautomationFlow:
    
    def __init__(self):
        self.state = SharedState()
        self.state.set("main_path",str(Path(__file__)))
        self.audio_file_folder=str(Path(__file__).parent) + r"\steps"
        self.clear_folder(self.audio_file_folder)

    
    def clear_folder(self,folder_path):
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # Remove file or link
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # Remove folder
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')

    def generate_blog(self, sent_url: str):

        print(f"Generating blog and post from url {sent_url}")
        self.state.set("youtube_url",f"{sent_url['url']}")
        print(self.state.get("youtube_url"))
        crew = postcrew(self.state)
        inputs={
            "url": self.state.get("youtube_url")
        }
        crew.crew().kickoff(inputs)
        return "Completed preparing post"

    def generate_email(self, mail_id: str):

        print("Creating Draft email")
        self.state.set("gmail_id",f"{mail_id['email']}")
        crew = GmailCrew()
        with open(self.state.get("Blog_output"),"r",encoding="utf-8") as f:
            self.blog=f.read()
        inputs = {
            "body": self.blog,
            "gmail": self.state.get("gmail_id")
        }

        draft_crew = crew.crew().kickoff(inputs)
        print(f"Draft Crew: {draft_crew}")
        return draft_crew
    
    def regenerate_content(self, prompt: str):

        print("Regenrating the post using user prompt")
        self.state.set("prompt",f"{prompt['prompt']}")
        print(self.state.get("prompt"))
        crew = feedbackcrew(self.state)
        with open(self.state.get("post_output"),"r",encoding="utf-8") as f:
            self.post=f.read()
        print(self.post)
        inputs = {
            "post": self.post
        }

        regenerate_crew = crew.crew().kickoff(inputs)
        print(f"regenerate Crew: {regenerate_crew}")
        return regenerate_crew

