import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from fastapi import FastAPI ,HTTPException
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel ,Field,ValidationError
from pathlib import Path
from .schema import template
import json

load_dotenv()


client = ChatOpenAI(model="openrouter/free",api_key=os.getenv('api_key'),base_url=os.getenv('base_url'))

prompt=Path("prompts/artprompt-v1.md").read_text(encoding="utf-8")


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


def validate_output(content:str):

    try:
        data=OutputFormat.model_validate_json(content)

        return {"valid":True,"output":data}

    except (ValidationError, ValueError) as e:

            start = content.find('{')

            end = content.rfind('}')

            if start !=-1 and end!=-1:

                 try:
                      cleaned=content[start:end+1]

                      data=OutputFormat.model_validate_json(cleaned)

                      return {"valid":True,"output":data} 


                 except (ValidationError , ValueError) as e:

                      return {"valid":False,"output":e}

            return {"valid":False,"output":e}              
            

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
            "release_year": 1972,
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

    first_response = chain.invoke({"prompt":formatted_prompt})    
    
    first_content = first_response.content

    validation_trial_1=validate_output(first_content)

    if  not validation_trial_1["valid"] :

        repairing_prompt = f' your_wrong_pervious_output is {first_content}, the error shown {validation_trial_1["output"]} , Your previous answer was rejected for this reason. Return only corrected JSON matching the schema'

        formatted_prompt=formatted_prompt+repairing_prompt

        with open("prompts/artprompt-v2.md",'w',encoding='utf-8') as f:

            f.write(formatted_prompt)

        second_response = chain.invoke({"prompt":formatted_prompt})

        second_content = second_response.content

        validation_trial_2=validate_output(second_content)

        if not validation_trial_2["valid"]:

            waste={"output":second_content,"input":art_name.name,"error":validation_trial_2["output"],"prompt_version":"artprompt-v2"}

            with open("logs/quarantine.jsonl",'a',encoding='utf-8') as f:

                f.write(json.dumps(waste)+"\n")

            raise HTTPException(status_code=442,detail="After trying for the second time there still something going wrong try to add a stronger system messege 💪🏼")

        return validation_trial_2["output"]

    return validation_trial_1["output"]
    

         

