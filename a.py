import os
import json
from flask import Flask,render_template,request
import run

app=Flask(__name__)
jd={}
@app.route("/")
def a():
    return render_template("form.html")
@app.route("/get_json",methods=["GET","POST"])
def get_data():
    data={}
    filename = os.path.join(app.static_folder, 'education.json')
    with open(filename) as file:
        d = json.load(file)
        data["education"]=d
    filename = os.path.join(app.static_folder, 'workXP.json')    
    # with open(filename) as file:
    #     d = json.load(file)
    #     data["work"]=d
    #print(data)    
    return data

@app.route("/jd",methods=["POST"])
def jd_data():
    data=request.json
    global jd
    jd=data
    run.set_jd_path(data["jdlocation"])
    run.set_r_path(data["reslocation"])
    run.getResSkills()
    run.getJDData()
    run.getResEdu()
    print(jd)
    return ""

@app.route("/evaluate")
def eval():
    return render_template("evaluate.html")

@app.route("/get_scores", methods=["POST"])
def score():
    data=request.json
    d={}
    if "education" in jd:
        d=run.scores(jd["education"],jd["WorkExperience"],jd["WorkSkills"],data)
    # for k,v in d.items():print(k,v)
    return d

# print("jd",jd)

if __name__ == "__main__" :
    app.run(debug=True)