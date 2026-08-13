import os
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
model=SentenceTransformer('all-MiniLM-L6-v2')
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "job_description.txt")
with open (file_path,"r",encoding="utf-8") as f:
    job_description=f.read()
job_embedding=model.encode(job_description)
resume_folder=os.path.join(script_dir,"resumes")
results=[]
for filename in os.listdir(resume_folder):
    filepath=os.path.join(resume_folder,filename)
    with open(filepath,"r",encoding="utf-8")as f:
        resume_text=f.read()
    resume_embedding=model.encode(resume_text)

    score=cos_sim(resume_embedding,job_embedding)
    results.append((score.item(),filename))
results.sort(reverse=True)
for score, filename in results:
    print(f"{score:.4f}-{filename}")

