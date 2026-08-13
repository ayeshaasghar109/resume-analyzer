from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq()
job_description = """We are looking for a Backend Developer with 2+ years of
professional experience.

Required skills:
Python, FastAPI, PostgreSQL, Docker and REST APIs.

The candidate should have a Bachelor's degree in Computer
Science or Software Engineering.

AWS certification is preferred."""
response_format={
    "type":"json_schema",
    "json_schema":{
        "name":"job_requirements",
        "schema":{
            "type":"object",
            "properties":{
                "skills":{
                    "type":"array",
                    "items":{
                        "type":"string"
                    }
                    
                },
                "experience":{
                     "type":"array",
                     "items":{
                        "type":"string"
                   }
                },
                "certifications":{
                     "type":"array",
                     "items":{
                    "type":"string"
                    }

                },
                "education":{
                    "type":"array",
                    "items":{
                     "type":"string"
                     }
                }
            },
                "required":[
                        "skills",
                        "experience",
                        "certifications",
                        "education"
                      ],
                     "additionalProperties":False
               }

         },
   
}

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "system",
            "content": "Extract skills, experience, education, and certifications from the job description."
        },
        {
            "role":"user",
            "content":job_description
        }
    ],
    response_format=response_format
)


print(response.choices[0].message.content)