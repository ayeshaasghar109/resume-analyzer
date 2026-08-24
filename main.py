from fastapi import FastAPI,HTTPException,UploadFile,File
from pydantic import BaseModel
import sqlite3
from fastapi import Depends
import pdfplumber
from  sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from fastapi import Form
from datetime import datetime
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
        cursor=db.execute(
"INSERT INTO resumes(name,email) VALUES(?,?)",
   (resume.name,resume.email)
)
        db.commit()
        return{"message":"success"}

@app.get("/resumes")
def get_resumes(db:sqlite3.Connection=Depends(get_db)):
        cursor=db.execute("SELECT * FROM resumes")
        rows=cursor.fetchall()
        return rows

@app.get("/resumes/{id}")
def get_resumes_id(id:int,db:sqlite3.Connection=Depends(get_db)):
        cursor=db.execute("SELECT * FROM resumes WHERE id=?",(id,))
        row=cursor.fetchone()
        if(row  is None):
             raise HTTPException(status_code=404, detail="resume not found")
        else:
             return row

@app.delete("/resumes/{id}")
def delete_resume(id:int,db:sqlite3.Connection=Depends(get_db)):
        cursor=db.execute("SELECT * FROM resumes WHERE id=?",(id,))
        row=cursor.fetchone()
        if(row  is None):
                raise HTTPException(status_code=404, detail="resume not found")
        else:
                cursor.execute("DELETE FROM resumes WHERE id=?", (id,))

                db.commit()
                return{"message":"successfully deleted"}
@app.put("/resumes/{id}")
def update_resume(id:int,resume:Resume,db:sqlite3.Connection=Depends(get_db)):
        cursor=db.execute("SELECT * FROM resumes WHERE id=?",(id,))
        row=cursor.fetchone()
        if(row  is None):
                 raise HTTPException(status_code=404, detail="resume not found")
        else:
           cursor.execute("UPDATE resumes  SET name=?,email=? WHERE id=?",
            (resume.name,resume.email,id))
           db.commit()
           return{"message":"success"}
# uploading the file
@app.post("/upload_resume")
def parse_resume(file:UploadFile=File(...)):
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
                    raise HTTPException(status_code=422, detail="resume not found")
        else:
                    clean_text=cleaned_text(text)
                    resume_data=extract_resume_info(clean_text)          
        return resume_data
        
#ANALYSIS OF RESUMES AND JOB

@app.post("/analyze")
def analyze_resumes(file:UploadFile=File(...), job_description:str=Form(...)):
       match=skills_match(file,job_description) 
       analysis=match["analysis"]
       summary=match["summary"]
       overall_score=weight_calculation(analysis) 
       skill_breakdown=match["skill_breakdown"]    
       return {
            "analysis":analysis,
            "summary":summary,
            "skill_breakdown":skill_breakdown,
            "overall_score":overall_score,  
       }

#cleaning the text
def cleaned_text(text):
       clean_text=text.strip()
       clean_text=" ".join(clean_text.split())
       return clean_text


def verify_skill(job_skill,resume_skill):
    try:
      response=client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
              {
                "role":"system",
                "content":"""
                    You are verifying whether a candidate's resume skill satisfies a required job skill.

                    Return true ONLY when the resume skill demonstrates that the candidate has the job skill.

                    Do not consider skills merely related, complementary, or prerequisites as matches.

                    Examples:
                    Python → Pandas = false
                    Python → NumPy = false
                    Algorithms → Machine Learning = false
                    HTML → CSS = false
                    SQL → SQLite = false
                    JS → JavaScript = true
                    React → React.js = true

                    Return JSON only:
                    {
                        "is_match": true or false
                    }

                 """
              },
              {
                "role":"user",
                "content":f"""
                    job_skill={job_skill}
                    resume_skill={resume_skill}
                """
                
              }
        ]
      )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"failed to fetch the requested service: {e}")
    try:
        result= json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Verification service returned malformed data: {e}")
    return result["is_match"]


#normalize skill

def normalize_skill(skill):
     skill=skill.strip().lower
     skill=" ".join(skill.split())
     return skill

#extracting the skills and  generating the embedding for them

def skills_match(file, job_description):
    resume_data = parse_resume(file)
    resume_skills = resume_data["skills"]
    job_data = extract_job_info(job_description)
    job_skills_names = [item["skill"] for item in job_data["skills"]]
    print(resume_skills)
    job_skills = job_data["skills"]
    print(job_data)
    used_skills = []
    match = []

    if not resume_skills or not job_skills_names:
        return []

    for i in range(len(job_skills)):
        found_match = False
        matched_resume_skill = None
        job_skill = job_skills[i]
        alternative_job_skills = job_skill["skill"].split("/")
        for m in range(len(alternative_job_skills)):
            for j in range(len(resume_skills)):
                if normalize_skill(alternative_job_skills[m]) == normalize_skill(resume_skills[j]):
                    found_match = True
                    matched_resume_skill = resume_skills[j]
                    used_skills.append(resume_skills[j])
                    break
        if found_match:
            matching_score = 1
            category = "Very Strong"
            resume_skill = matched_resume_skill
        else:
            available_resume_skills = []
            for k in range(len(resume_skills)):
                skill_used = False
                for l in range(len(used_skills)):
                    if resume_skills[k] == used_skills[l]:
                        skill_used = True
                if not skill_used:
                    available_resume_skills.append(resume_skills[k])
            if not available_resume_skills:
                matching_score = 0
                category = "Missing"
                resume_skill = None
            else:
                job_skill_embedding = model.encode([job_skill["skill"]])
                resume_skills_embedding = model.encode(available_resume_skills)
                similarity = cosine_similarity(job_skill_embedding, resume_skills_embedding)

                best_match = similarity.argmax()
                resume_skill = available_resume_skills[best_match]
                matching_score = float(min(similarity[0][best_match],1.0))
                is_match=verify_skill(job_skill["skill"],resume_skill)
                if not is_match:
                    resume_skill = None
                    matching_score = 0
                    category = "Missing"
                else:
                    if matching_score >= 0.90:
                        category = "Very Strong"
                    elif matching_score >= 0.75:
                        category = "Strong"
                    elif matching_score >= 0.60:
                        category = "Partial"
                    elif matching_score >= 0.45:
                        category = "Somewhat Related"
                    else:
                        matching_score = 0
                        resume_skill = None
                        category = "Missing"

                if resume_skill:
                    used_skills.append(resume_skill) 
        match_data = {
            "job_skill": job_skill,
            "resume_skill": resume_skill,
            "matching_score": float(matching_score),
            "category": category,
            "experience_months":verify_experience(job_skill["skill"],resume_data["experiences"])
        }
        match.append(match_data)
    matched_skills=[]
    missing_skills=[]
    related_skills=[]
    required_missing_skills=[]
    preferred_missing_skills=[]
    required_total=0
    required_match=0
    preferred_total=0
    preferred_match=0
    unspecified_total=0
    unspecified_match=0
    for item in match:
        category=item["category"]
        importance=item["job_skill"]["importance"]
        if importance=="required":
            required_total+=1
        elif importance == "preferred":
            preferred_total += 1
        elif importance == "unspecified":
            unspecified_total += 1
            
        if category in ["Very Strong","Strong", "Partial"]:
            matched_skills.append(item)
            if importance=="required":
                required_match+=1
            elif importance == "preferred":
                preferred_match += 1
            elif importance == "unspecified":
                unspecified_match += 1
        elif category=="Somewhat Related":
            related_skills.append(item)
        elif category=="Missing":
            missing_skills.append(item)
            if importance=="required":
                required_missing_skills.append(item)
            elif importance=="preferred":
                preferred_missing_skills.append(item)
    skill_breakdown={
        "required_skills":{
            "total":required_total,
            "matched":required_match,
            "missing":len(required_missing_skills)    
        },
        "preferred_skills":{
            "total":preferred_total,
            "matched":preferred_match,
            "missing":len(preferred_missing_skills)
        },
        "unspecified_skills":{
            "total":unspecified_total,
            "matched":unspecified_match,
            "missing":unspecified_total-unspecified_match,

        }
    }
    summary={
            "matched_skills":matched_skills,
            "required_missing_skills":required_missing_skills,
            "preferred_missing_skills":preferred_missing_skills,
            "missing_skills":missing_skills,
            "related_skills":related_skills
    }

    return {
          "analysis":match,
          "summary":summary,
          "skill_breakdown":skill_breakdown
    }

#calculating the experience month
def calculate_experience(start_date,end_date):
    if start_date=="unknown":
        return None
    start=datetime.strptime(start_date,"%Y-%m")
    if end_date=="Present":
       end= datetime.now()
    elif end_date=="unknown":
        return None
    else:
        end=datetime.strptime(end_date,"%Y-%m")
    gap=end-start
    total_months=(end.year-start.year)*12+(end.month-start.month)
    return total_months
# calculating the xperience

def verify_experience(job_skill,resume_experiences):
    total_months=0
    for item in resume_experiences:
        print(item)
        if job_skill in item["domain"]:
            months=calculate_experience(item["start_date"],item["end_date"])
            if months is not None:
                total_months+=months
    return total_months
          


  
             
       
     
#calculating the wightage score
def weight_calculation(match):
    required_score=[]
    preferred_score=[]
    if not match:
        return None
    for item in match:
            matching_score = item["matching_score"]
            importance = item["job_skill"]["importance"]
            if importance == "required":
                required_score.append(matching_score)
            if importance == "preferred":
                preferred_score.append(matching_score)
    if not required_score and not preferred_score:
                return None
    elif preferred_score and not required_score:
        preferred_average=np.mean(preferred_score)
        result=preferred_average
        return result*100
    elif required_score and not preferred_score:
        required_average=np.mean(required_score)
        result=required_average
        return result*100
    else:
        required_average=np.mean(required_score)
        preferred_average=np.mean(preferred_score)
        result=(required_average*0.80 )+ (preferred_average*0.20)
        return result*100
      
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
                                        "min_years":{
                                             "type":"integer"
                                        }
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
                    "content": """Extract each independently identifiable skill as a separate item in the skills array.

                    SKILL EXTRACTION RULES:
                    1. Extract only the skill name itself.
                    Remove surrounding qualifier phrases such as:
                    - "strong proficiency in"
                    - "experience with"
                    - "solid understanding of"
                    - "familiarity with"
                    - "knowledge of"
                    Examples:
                    "Strong proficiency in Python" → "Python"
                    "Familiarity with Docker" → "Docker"
                    2. If multiple distinct skills are connected using "/" or "&", separate them.
                    Examples:
                    "SQL/SQLite" → "SQL", "SQLite"
                    "Git & GitHub" → "Git", "GitHub"
                    3. Do NOT split skills joined by "or".
                    "or" indicates alternatives where either skill is acceptable.
                    Example:
                    "FastAPI or Flask" → "FastAPI/Flask"
                    4. Keep established combined technical concepts together.
                    Example:
                    "CI/CD" → "CI/CD"
                    IMPORTANCE CLASSIFICATION RULES:
                    For every extracted skill, assign exactly ONE of these values:
                    - "required"
                    - "preferred"
                    - "unspecified"
                    Determine importance ONLY from the wording and context of the job description.
                    Do NOT infer importance from how technically important or common a skill is.

                    REQUIRED:
                    Assign "required" when the job description explicitly indicates that the skill is necessary, mandatory, or expected as a core requirement.
                    Examples of wording that indicates "required":
                    - "required"
                    - "must have"
                    - "must know"
                    - "mandatory"
                    - "essential"
                    - "necessary"
                    - "should have"
                    - "the candidate should have"
                    - "the candidate needs"
                    - "we require"
                    - "strong experience with" when presented as a core qualification
                    Example:
                    "The candidate must have Python and SQL experience."
                    → Python: required
                    → SQL: required

                    PREFERRED:
                    Assign "preferred" when the job description explicitly indicates that the skill is desirable but not mandatory.

                    Examples of wording that indicates "preferred":
                    - "preferred"
                    - "nice to have"
                    - "nice-to-have"
                    - "bonus"
                    - "additional advantage"
                    - "additional benefit"
                    - "would be an advantage"
                    - "would be beneficial"
                    - "desirable"
                    - "plus"
                    - "a plus"

                    Example:
                    "Experience with Docker is preferred."
                    → Docker: preferred
                    Example:
                    "Knowledge of Redis and AWS would be an additional advantage."
                    → Redis: preferred
                    → AWS: preferred

                    UNSPECIFIED:
                    Assign "unspecified" when a skill is mentioned in the job description but there is no explicit indication that it is required or preferred.

                    Do NOT assume that a mentioned skill is required simply because it appears in the job description.

                    Example:
                    "The role involves Python, SQL, and Redis."
                    Python: unspecified
                    SQL: unspecified
                    Redis: unspecified

                    CONTEXT RULE:

                    Importance applies according to the context in which the skill is mentioned.

                    Example:
                    "Python and FastAPI are required. Docker is preferred. Redis is mentioned as a technology used by the team."

                    Python: required
                    FastAPI: required
                    Docker: preferred
                    Redis: unspecified
                    IMPORTANT:

                    Do not randomly assign "required" or "preferred".
                    Do not infer importance from the skill itself.
                    Use the explicit wording and surrounding context of the job description.

                    For every skill, return exactly one importance value:
                    "required", "preferred", or "unspecified".
                    SKILL NORMALIZATION RULES:

                    Normalize formatting differences in skill names without changing their meaning.

                    Preserve the standard readable form of established technical skills.

                    Examples:
                    "RESTAPIs" → "REST APIs"
                    "REST API" → "REST APIs"
                    "rest apis" → "REST APIs"
                    "RESTful APIs" → "REST APIs"
                    "React.js" → "React.js"
                    "Java Script" → "JavaScript"
                    "Git Hub" → "GitHub"

                    Do not remove meaningful spaces from multi-word technical skills.

                    For example:
                    "REST APIs" must remain "REST APIs", not "RESTAPIs".
                    "Machine Learning" must remain "Machine Learning".
                    "Software Architecture" must remain "Software Architecture".

                    MIN_YEARS EXTRACTION RULES:
                    For every skill, also extract the minimum number of years of experience required, if stated.

                    If the job description gives a range (e.g. "3-5 years"), use the lower number.
                    If it says "X+ years" or "at least X years", use X.
                    If no number of years is mentioned for a skill, set min_years to 0.

                    Examples:
                    "2+ years Python experience" → Python: min_years = 2
                    "at least 2 years of SQL" → SQL: min_years = 2
                    "3-5 years of backend development experience" → min_years = 3
                    "Familiarity with Docker" (no years mentioned) → Docker: min_years = 0
"""
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
    except Exception as e:
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
                "experiences":{
                        "type":"array",
                        "items":{
                        "type":"object",
                        "properties":{
                            "experience":{
                                "type":"string" 
                            },
                            "title":{
                                "type":"string",
                            },
                            "type":{
                                "type":"string",
                                "enum":[
                                    "work",
                                    "project"
                                     
                                ]
                            },
                            "start_date":{
                               "type":"string"
                                },
                            "end_date":{
                               "type":"string"
                                },
                           "domain":{
                               "type":"array",  
                                  "items":{
                                    "type":"string"
                                }
                            }
                        },
                        "required":[
                            "experience",
                            "title",
                            "type",
                            "start_date",
                            "end_date",
                            "domain"

                        ],
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
                    "experiences",
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
                    "content": """Extract the candidate's skills, experience, education, and certifications from the resume.

                        Extract each independently identifiable skill as a separate item in the skills array.

                        If multiple distinct skills are written together using /, &, or and, separate them when they represent distinct skills.

                        Keep established combined technical concepts such as CI/CD as one skill.

                        Examples:
                        HTML/AJAX → HTML, AJAX
                        Git & GitHub → Git, GitHub
                        SQL/SQLite → SQL, SQLite
                        CI/CD → CI/CD
                        EXPERIENCE EXTRACTION RULES:
                        For each entry in the experiences array, extract title, start_date, end_date, and domain.

                        DATE FORMAT:
                        Always format start_date and end_date as "YYYY-MM".
                        Example: "Mar 2026" → "2026-03"
                        Example: "Nov 2022" → "2022-11"

                        ONGOING ROLES:
                        If the entry says "Present" or otherwise indicates the role/project is still ongoing,
                        set end_date to the literal string "Present" (do not guess a date).

                        UNKNOWN DATES:
                        If no date is mentioned at all for start_date or end_date, set that field to "unknown".
                        Do not invent or estimate a date that is not stated in the text.

                        DOMAIN:
                        List the skill(s) this experience entry involves, using the same normalized skill names
                        you use in the top-level skills array (apply the same qualifier-stripping and "/" or "&"
                        splitting rules described above) — not the raw phrasing from the sentence.
                        Example: "Built a system in Python (TCP sockets)" → domain: ["Python"]
                        Example: "Using Flutter for the client and Python for backend logic" → domain: ["Flutter", "Python"]

                        EXPERIENCE INCLUDES WORK AND PROJECTS:

                        Treat both formal work experience and relevant projects as experience entries.

                        Include:
                        - paid employment
                        - internships
                        - freelance work
                        - tutoring or other professional work
                        - personal software projects
                        - academic software projects
                        - university projects
                        - technical projects listed under sections such as "CURRENT PROJECTS",
                        "EARLIER PROJECTS", "PROJECTS", or similar headings

                        Do NOT ignore a project merely because it is not paid employment.

                        For every work or project entry, create one object in the experiences array.

                        Set:
                        - type = "work" for employment, internship, freelance work, tutoring, or similar professional work
                        - type = "project" for personal, academic, university, or portfolio projects

                        Example:
                        "Home Tutor, Jan 2025 - Present" → type: "work"

                        "FAQ Assistant, Python, FastAPI, 2026" → type: "project"
            """
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
    except Exception as e:
              raise HTTPException(status_code=502,detail=f"Extraction service returned malformed data: {e}")
    


      



              
              


              

       
       