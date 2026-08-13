from fastapi import FastAPI,HTTPException,UploadFile,File
from pydantic import BaseModel
import sqlite3
from fastapi import Depends
import pdfplumber
from  sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from fastapi import Form
import  json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq()

DB_PATH="resume.db"
def get_db():
      conn=sqlite3.connect(DB_PATH)
      try:
            yield conn
      finally:
            conn.close()


model=SentenceTransformer("all-MiniLM-L6-v2")
# CREATED A TABLE THAT WAS NOT ALREADY EXISTING
def init_db():
      conn=sqlite3.connect(DB_PATH)
      conn.execute("""
CREATE TABLE IF NOT EXISTS resumes(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT
)
"""
)
      conn.commit()
      conn.close()
init_db()
app=FastAPI()
class Resume(BaseModel):
        name:str
        email:str
@app.get('/') 
def home():
    
        return {"message":"API IS RUNNING NOW"}

@app.post("/resumes")
def receive_resume(resume:Resume,db:sqlite3.Connection=Depends(get_db)):
        db.execute(
"INSERT INTO resumes(name,email) VALUES(?,?)",
   (resume.name,resume.email)
)
        db.commit()
        return{"message":"success"}

@app.get("/resumes")
def get_resumes(db:sqlite3.Connection=Depends(get_db)):
        db.execute("SELECT * FROM resumes")
        rows=db.fetchall()
        return rows

@app.get("/resumes/{id}")
def get_resumes_id(id:int,db:sqlite3.Connection=Depends(get_db)):
        db.execute("SELECT * FROM resumes WHERE id=?",(id,))
        row=db.fetchone()
        if(row  is None):
             raise HTTPException(status_code=404, detail="resume not found")
        else:
             return row

@app.delete("/resumes/{id}")
def delete_resume(id:int,db:sqlite3.Connection=Depends(get_db)):
        db.execute("SELECT * FROM resumes WHERE id=?",(id,))
        row=db.fetchone()
        if(row  is None):
                raise HTTPException(status_code=404, detail="resume not found")
        else:
                db.execute("DELETE FROM resumes WHERE id=?", (id,))

                db.commit()
                return{"message":"successfully deleted"}
@app.put("/resumes/{id}")
def update_resume(id:int,resume:Resume,db:sqlite3.Connection=Depends(get_db)):
        db.execute("SELECT * FROM resumes WHERE id=?",(id,))
        row=db.fetchone()
        if(row  is None):
                 raise HTTPException(status_code=404, detail="resume not found")
        else:
           db.execute("UPDATE resumes  SET name=?,email=? WHERE id=?",
            (resume.name,resume.email,id))
           db.commit()
           return{"message":"success"}
# uploading the file
@app.post("/upload_resume")
def upload_resume(file:UploadFile=File(...)):
        if not file.filename.lower().endswith(".pdf"):
              raise HTTPException(status_code=400,detail="only pdf format supported")
        try:
            with(pdfplumber.open(file.file)) as pdf:
             text=""
            for page in pdf.pages:
                    text_page=page.extract_text()
                    
                    if(text_page is None):
                       text+=("")
                    else:
                       text+=text_page
        except Exception as e:
            raise HTTPException(status_code=400,detail=f"Could not read pdf: {e}")
         
        if(not text):
                    raise HTTPException(status_code=404, detail="resume not found")
        else:
                    clean_text=cleaned_text(text)
                    resume_data=extract_resume_info(clean_text)          
        return resume_data
        
#ANALYSIS OF RESUMES AND JOB

@app.post("/analyze")
def analyze_resumes(file:UploadFile=File(...), job_description:str=Form(...)):
       match=skills_match(file,job_description) 
       overall_score=weight_calculation(match)       
       return {
             "analysis":match,
              "overall_score":overall_score
             
       }

#cleaning the text
def cleaned_text(text):
       clean_text=text.strip()
       clean_text=" ".join(clean_text.split())
       return clean_text



#extracting the skills and then generating the embedding for them

def skills_match(file,job_description):
       resume_data=upload_resume(file)
       resume_skills=resume_data["skills"]
       job_data=extract_job_info(job_description)
       job_skills_names=[item["skill"] for item in job_data["skills"]]
       job_skills=job_data["skills"]
       if not resume_skills or not job_skills_names:
            return[]
       resume_skills_embedding=model.encode(resume_skills)
       job_skills_embedding=model.encode(job_skills_names)
       similarity=cosine_similarity(job_skills_embedding,resume_skills_embedding)
       best_match=similarity.argmax(axis=1)
       match=[]
       for i in range(len(job_skills)):
              job_skill=job_skills[i]
              job_importance = job_skills[i]["importance"]
              resume_skill=resume_skills[best_match[i]]
              matching_score=similarity[i][best_match[i]]
              if matching_score>=0.90:
                    category="Very Strong"
              elif  matching_score >=0.75:
                     category="Strong"
              elif matching_score >=0.60:
                     category="Partial"
              elif matching_score >= 0.45:
                     category = "Somewhat Related"
                    
              else:
                    matching_score=0
                    resume_skill="None"
                    category="Missing"

              match_data = {
                    "job_skill": job_skill,
                    "resume_skill": resume_skill,
                    "matching_score": float(matching_score),
                    "category": category,
}
              match.append(match_data)
       return match
       

#calculating the wightage score
def weight_calculation(match):
    weighted_sum = 0
    total_weight = 0
    if not match:
          return {"message":"Insufficient Data"}
    for item in match:

        matching_score = item["matching_score"]
        importance = item["job_skill"]["importance"]

        if importance == "required":
            weight = 2
        elif importance == "preferred":
            weight = 1
        else:
            weight = 1

        weighted_sum += matching_score * weight
        total_weight += weight

    overall_score_percentage = weighted_sum / total_weight

    return overall_score_percentage*100
# structuring the groq thing


response_format_for_job={
    "type":"json_schema",
    "json_schema":{
        "name":"job_requirements",
        "schema":{
            "type":"object",
            "properties":{
                "skills":{
                    "type":"array",
                    "items":{
                        "type":"object",
                        "properties":{
                               "skill":{
                                    "type":"string"
                               },
                                       "importance":{
                                            "type":"string",
                                                "enum":[
                                                    "required",
                                                    "preferred",
                                                    "unspecified"
                                                    ],
                                             },
                                    }
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

def extract_job_info(job_description):
    try:
       response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": "Extract skills, experience, education, and certifications from the job description."
                },
                {
                    "role": "user",
                    "content": job_description
                }
            ],
            response_format=response_format_for_job
        )
    except Exception as e:
          raise HTTPException(status_code=502, detail=f"failed to fetch the requested service: {e}")
    try:
          return json.loads(response.choices[0].message.content)
    except:
          raise HTTPException(status_code=502,detail=f"Extraction service returned malformed data: {e}")


   

response_format_for_resume={
    "type":"json_schema",
    "json_schema":{
        "name":"job_requirements",
        "schema":{
            "type":"object",
            "properties":{
                "skills":{
                    "type":"array",
                    "items":{
                        "type":"string",
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


def extract_resume_info(clean_text):
    try:
       response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": "Extract the candidate's skills, experience, education, and certifications from the resume."
                },
                {
                    "role": "user",
                    "content": clean_text
                }
            ],
            response_format=response_format_for_resume
        )
    except Exception as e:
              raise HTTPException(status_code=502, detail=f"failed to fetch the requested service: {e}")
    try:
              return json.loads(response.choices[0].message.content)
    except:
              raise HTTPException(status_code=502,detail=f"Extraction service returned malformed data: {e}")
    


      



              
              


              

       
       