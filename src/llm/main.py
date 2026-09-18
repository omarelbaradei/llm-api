import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from fastapi import FastAPI 
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel ,Field
from pathlib import Path
from .schema import template

load_dotenv()


client = ChatOpenAI(model="openrouter/free",api_key=os.getenv('api_key'),base_url=os.getenv('base_url'))

prompt=Path("prompts/last_match-v1.md").read_text(encoding="utf-8")


class Actor(BaseModel):

    name:str

class OutputFormat(BaseModel):

    "information about a movie, series or play "

    name_of_act:str = Field(description="the name of the play or movie or series")

    art_type:str = Field(description="is this art a series, movie or play")

    category:str = Field(description="the category that this art is under")

    release_year: int = Field(description="the art's year of release")

    director:str = Field(description="the  art's director's name")

    actors:list[Actor] = Field(description="the biggest four actors that contributed in this art")

    confidence:float = Field(description=" how confident the model is about its answer")


class ArtRequest(BaseModel):

     name: str = Field(min_length=2,max_length=400)



parser = JsonOutputParser(pydantic_object=OutputFormat)

format_instructions=parser.get_format_instructions()

template=template.partial(format_instruction=format_instructions)


chain = template | client 


app = FastAPI()

@app.post("/art_info")

def matches_history(art_name:ArtRequest):

    if os.getenv("LLM_STUB") == "1":
        return {
            "name_of_act": "The Godfather",
            "art_type": "movie",
            "category": "crime drama",
            "year": 1972,
            "director": "Francis Ford Coppola",
            "actors": [
                {"name": "Marlon Brando"},
                {"name": "Al Pacino"},
                {"name": "James Caan"},
                {"name": "Robert Duvall"}
            ],
            "confidence": 1.0
        }

    formatted_prompt = prompt.format(artname = art_name.name)

    response = chain.invoke({"prompt":formatted_prompt})    
    
    return response.content

