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
    #print(jd)
    return ""

@app.route("/evaluate")
def eval():
    return render_template("evaluate.html")

@app.route("/get_score", methods=["POST"])
def score():
    data=request.json
    d=run.scores(jd["education"],data)
    return d

if __name__ == "__main__" :
    app.run(debug=True)