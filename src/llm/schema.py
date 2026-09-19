from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system",'''Your are providing some information about any kind of art (movie,series,play) always return json object following this format {{"name_of_act" : one [mission impossible]

    "art_type": one [movie|series|play]

    "category": one [commedy|action|sci-fi|drama]

    "release_year": one [1992 | 2012 | ...]

    "director": one [nolan | ...]

    "actors": 4 maximum [Tom Criuse | Leonardo Dicaprio | Julia Roberts|....]

    "confidence: 0 to 1}},
     Never invent a category. Never add fields. Never return anything except the JSON object, If the message does not clearly fit a category, use 
    
    other with a confidence below 0.5. Do not guess.'''),

    ("human",'''the output must follow the format instruction and must be json structured and the confidence key must be within 0 and 1 based on model's confidence
    
    input:{prompt} format instruction:{format_instruction}''')
])



