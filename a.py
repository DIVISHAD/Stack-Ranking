import os
import json
from flask import Flask,render_template,request

app=Flask(__name__)
@app.route("/")
def a():
    return render_template("form.html")
@app.route("/get_json",methods=["GET","POST"])
def renderblog():
    data={}
    filename = os.path.join(app.static_folder, 'education.json')
    with open(filename) as file:
        d = json.load(file)
        data["education"]=d
    filename = os.path.join(app.static_folder, 'workXP.json')    
    with open(filename) as file:
        d = json.load(file)
        data["work"]=d
    #print(data)    
    return data        
if __name__ == "__main__" :
    app.run(debug=True)