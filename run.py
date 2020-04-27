import json
import os
import samp
import pymongo
import numpy as np

client = pymongo.MongoClient("mongodb+srv://divishad:abcde@cluster0-gdmit.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = client.StackRanking.education

jd_path="C:/Users/User/Desktop/Darwinbox/stack ranking/SovrenProductDemo-14_Resumes/SourceDocument/"
r_path="C:/Users/User/Desktop/Darwinbox/stack ranking/SovrenProductDemo-12_Resumes/"

def set_jd_path(path):
    global jd_path
    jd_path=path

def set_r_path(path):
    global r_path
    r_path=path    

candidates_skills=[]
candidates_qualifications=[]
jd_taxonamies={}
candidate_work_skills={}

def getResSkills():
    for nm in os.listdir(r_path):
        candidate_taxonamies={}
        candidate_work_skills[nm]={}
        candidate_work_skills[nm]["Skills"]={}
        candidate_taxonamies["name"]=nm     #r_path+nm+"/"+nm+".json"
        with open(r_path+nm,'r',encoding='cp850') as file:
            data=json.load(file)
            a=data.get("Resume").get("UserArea").get("sov:ResumeUserArea").get("sov:ExperienceSummary").get("sov:SkillsTaxonomyOutput").get("sov:TaxonomyRoot")[0].get("sov:Taxonomy")
            for i in a:
                candidate_taxonamies[i["@name"]]={}
                for j in i.get("sov:Subtaxonomy"):
                    candidate_taxonamies[i["@name"]][j["@name"]]={}
                    if j.get("sov:Skill") != None:
                        for k in j.get("sov:Skill"):
                            child_skills=[]
                            if k.get("sov:ChildSkill") != None:
                                for sub in k.get("sov:ChildSkill"):
                                    child_skills.append(sub["@name"])
                                    if "@whereFound" in sub:
                                        if " WORK HISTORY" in sub["@whereFound"][8:].split(";"):
                                            if "@totalMonths" in sub:
                                                candidate_work_skills[nm]["Skills"][sub["@name"]]=int(sub["@totalMonths"])
                                            else:
                                                candidate_work_skills[nm]["Skills"][sub["@name"]]=-1   
                            candidate_taxonamies[i["@name"]][j["@name"]][k["@name"]]=child_skills
                            if "@whereFound" in k:
                                if " WORK HISTORY" in k["@whereFound"][8:].split(";"):
                                    if "@totalMonths" in k:
                                        candidate_work_skills[nm]["Skills"][k["@name"]]=int(k["@totalMonths"])
                                    else:
                                            candidate_work_skills[nm]["Skills"][k["@name"]]=-1   
            candidates_skills.append(candidate_taxonamies)

def getJDData():
    for nm in os.listdir(jd_path):
        with open(jd_path+nm+"/"+nm+".json",'r',encoding='cp850') as file:
            data=json.load(file)
            a=data.get("SovrenData").get("SkillsTaxonomyOutput")[0].get("Taxonomy")
            for i in a:
                jd_taxonamies[i["@name"]]={}
                for j in i.get("Subtaxonomy"):
                    jd_taxonamies[i["@name"]][j["@name"]]={}
                    if j.get("Skill") != None:
                        for k in j.get("Skill"):
                            child_skills=[]
                            if k.get("ChildSkill") != None:
                                for sub in k.get("ChildSkill"):
                                    child_skills.append(sub["@name"])        
                            jd_taxonamies[i["@name"]][j["@name"]][k["@name"]]=child_skills 
                    jd_taxonamies[i["@name"]][j["@name"]]["percent"]=j["@percentOfOverall"]  

def tanh(z):
    return 1-(2/(1+np.exp(2*z)))

def evaluate_skills(candidate,json,param):
    score = 0
    for taxonomy_name,taxonomy_value in json.items():
        if taxonomy_name in candidate != False:
            for subTaxonomy_name,subTaxonomy_value in taxonomy_value.items():
                val=subTaxonomy_value["percent"]
                if subTaxonomy_name in candidate[taxonomy_name]!= False:
                    skill_match = 0
                    candidate_skills=candidate[taxonomy_name][subTaxonomy_name]
                    for skill_name,skill_value in subTaxonomy_value.items():
                        if skill_name in candidate[taxonomy_name][subTaxonomy_name] != False:
                            skill_match += 1
                            childSkill_match = 0
                            candidate_childSkill_list = candidate[taxonomy_name][subTaxonomy_name][skill_name]
                            for childSkill in skill_value:
                                if childSkill in candidate_childSkill_list != False:
                                    childSkill_match +=1
                                    score += param["matchSkillScr"]/100 * (val / (len(subTaxonomy_value)-1)) / len(skill_value)
                            if len(skill_value) == 0 :
                                score += param["matchSkillScr"]/100 * (val / (len(subTaxonomy_value)-1))
                            elif len(candidate_childSkill_list) == 0 :
                                score += param["matchSkillScr"]/100 * (val / (len(subTaxonomy_value)-1)) / 2
                            elif len(candidate_childSkill_list) != 0 :
                                len_nonMatch = len(candidate_childSkill_list)-childSkill_match
                                score += param["extraSkillScr"]/100*(val / (len(subTaxonomy_value)-1))*tanh(len_nonMatch/5)    # (len_nonMatch)*(val/(len(subTaxonomy_value)-1))/(len(skill_value) + 2*len_nonMatch) 
                    if len(subTaxonomy_value) == 1 :
                        score +=param["matchSkillScr"]/100 * val
                    elif len(candidate_skills) == 0 :
                        score +=param["matchSkillScr"]/100 *  val / 2
                    elif len(candidate_skills) != 0 :
                        nonMatch_skills=len(candidate_skills)-skill_match
                        score += param["extraSkillScr"]/100 * val*tanh(nonMatch_skills/10)    # (len(subTaxonomy_value)-1+ constant*nonMatch_skills)            
    return  score  
education_degree_type = [['specialeducation'],['some high school or equivalent','ged','secondary'],
                        ['high school or equivalent','certification','vocational','some college'],
                        ['HND/HNC or equivalent','associates','international'],['bachelors'],
                        ['some post-graduate','masters','intermediategraduate'],['professional'],
                        ['postprofessional'],['doctorate'],['postdoctorate']]
education_index = {'specialeducation':0,'some high school or equivalent':1,'ged':1,'secondary':1,
                        'high school or equivalent':2,'certification':2,'vocational':2,'some college':2,
                        'HND/HNC or equivalent':3,'associates':3,'international':3,'bachelors':4,
                        'some post-graduate':5,'masters':5,'intermediategraduate':5,'professional':6,
                        'postprofessional':7,'doctorate':8,'postdoctorate':9}
d_name=db.find_one({"key":"DegreeName"})["DegreeName"]  
d_major=db.find_one({"key":"DegreeMajor"})["DegreeMajor"]
colleges_tier=db.find_one({"key":"CollegeTier"})["CollegeTier"]

def getResEdu():
    for i in os.listdir(r_path):
        candidate_education={}
        candidate_education["name"]=i
        candidate_education["candidate_degrees"]=[]
        with open(r_path+i,'r',encoding='cp850') as file:
            data=json.load(file)
            if data.get("Resume").get("StructuredXMLResume").get("EducationHistory") != None:
                a=data.get("Resume").get("StructuredXMLResume").get("EducationHistory").get("SchoolOrInstitution")
                for deg in a:
                    degree={}
                    if "Degree" in deg:
                        if "@degreeType" in deg.get("Degree")[0]:
                            degree["DegreeType"]=deg.get("Degree")[0].get("@degreeType")
                        else:degree["DegreeType"]=""    
                        if "DegreeName" in deg.get("Degree")[0]:
                            if deg.get("Degree")[0].get("DegreeName") in d_name:
                                degree["DegreeName"]=d_name[deg.get("Degree")[0].get("DegreeName")]
                            else:    
                                degree["DegreeName"]=deg.get("Degree")[0].get("DegreeName")
                        else:degree["DegreeName"]=""    
                        if "DegreeMajor" in deg.get("Degree")[0]:
                            if deg.get("Degree")[0].get("DegreeMajor")[0].get("Name")[0] in d_major:
                                degree["DegreeMajor"]=d_major[deg.get("Degree")[0].get("DegreeMajor")[0].get("Name")[0]]
                            else:    
                                degree["DegreeMajor"]=deg.get("Degree")[0].get("DegreeMajor")[0].get("Name")[0]
                        else:degree["DegreeMajor"]=""    
                        if "sov:NormalizedGPA" in deg.get("Degree")[0].get("UserArea").get("sov:DegreeUserArea"):
                            degree["DegreeScore"]=float(deg.get("Degree")[0].get("UserArea").get("sov:DegreeUserArea").get("sov:NormalizedGPA"))*100
                        else:degree["DegreeScore"]=-1
                    if "UserArea" in deg:
                        if "sov:SchoolOrInstitutionTypeUserArea" in deg["UserArea"]:
                            if "sov:NormalizedSchoolName" in deg["UserArea"]["sov:SchoolOrInstitutionTypeUserArea"]:
                                if deg["UserArea"]["sov:SchoolOrInstitutionTypeUserArea"]["sov:NormalizedSchoolName"] in colleges_tier:
                                    degree["CollegeTier"]=colleges_tier[deg["UserArea"]["sov:SchoolOrInstitutionTypeUserArea"]["sov:NormalizedSchoolName"]]
                                else:
                                    degree["CollegeTier"]=2 #deg["UserArea"]["sov:SchoolOrInstitutionTypeUserArea"]["sov:NormalizedSchoolName"]
                        else:
                            degree["CollegeTier"]=3
                    else:
                        degree["CollegeTier"]=3                           
                    candidate_education["candidate_degrees"].append(degree)    
            candidates_qualifications.append(candidate_education) 
pp={}
for i in candidates_qualifications:
    # print(i,"\n")
    if(i["name"]=="5d5fb8aac9c0a_1566554280_NitinAgrawal[12_0].docx"):
        pp=i     
# print(pp)

def evaluate_education(res,edu_list,param):
    indx=0
    for i in edu_list:
        if i["DegreeType"] in education_index.keys() and education_index[ i["DegreeType"]]>indx:
            indx = education_index[ i["DegreeType"]]
    if indx==0:indx=len(education_degree_type)-1
    lst=education_degree_type[0:indx+1]
    l=[0 for i in range(indx+1)]            
    d=res.get("candidate_degrees")
    least_score=100
    cnt=0
    sr=0
    for i in d:
        if i["DegreeScore"] != -1 :
            cnt+=1
            sr+=i["DegreeScore"]
    if cnt != 0:least_score=sr/cnt         
    if least_score==100:least_score=param["noScrRes"] 
    tst=lambda val: least_score if(val==-1) else val
    for i in edu_list:
        if i["DegreeType"] !='':
            for j in d:
                if i["DegreeType"]==j["DegreeType"]:
                    scr=education_index[i["DegreeType"]]/sum([i for i in range(1,len(lst))])*param["mentionedDegScr"]    # (tst(j["DegreeScore"])/100)
                    if i["DegreeName"]=='' or i["DegreeName"].lower()==j["DegreeName"].lower():
                        if i["DegreeMajor"]=='' or i["DegreeMajor"].lower()==j["DegreeMajor"].lower():
                            jd_clg_tier=3
                            if i["CollegeTier"]!='':
                                jd_clg_tier=i["CollegeTier"]
                            jd_deg_score=50
                            if i["DegreeScore"]!='':
                                jd_deg_score=i["DegreeScore"]
                            tier_penalize=1.5
                            deg_score_penalize=25
                            if j["CollegeTier"]>= jd_clg_tier:
                                tier_penalize = 1
                            if tst(j["DegreeScore"]) < jd_deg_score:
                                deg_score_penalize=20
                            add_val = scr*param["degMatchScr"]/100  + scr*(param["percentagescr"]/100)*tanh((tst(j["DegreeScore"])-jd_deg_score)/deg_score_penalize) + scr*(param["clgTierscr"]/100)*tanh(jd_clg_tier-j["CollegeTier"]/tier_penalize)
                            if l[education_index[i["DegreeType"]]] < add_val:    
                                l[education_index[i["DegreeType"]]] = add_val        
                        else:
                            if l[education_index[i["DegreeType"]]]<(scr*0.45):
                                l[education_index[i["DegreeType"]]]=scr*0.45
                    else:
                        if l[education_index[i["DegreeType"]]]<(scr*0.35):
                            l[education_index[i["DegreeType"]]]=scr*0.35                
                    break        
    additional_score=0
    for i in d:
        flag_=0
        for dg in lst:
            if i["DegreeType"] in dg:
                if l[lst.index(dg)] == 0:
                    l[lst.index(dg)] = lst.index(dg)/sum([i for i in range(1,len(lst))])*100*(tst(i["DegreeScore"])/100)
                break
            elif i["DegreeType"] in education_index and education_index[i["DegreeType"]] >= len(l) and flag_==0:
                flag_=1
                additional_score=param["otherDegScr"] 
    flag = 0
    for i in range(len(lst)-1,0,-1):
        if l[i] != 0 and flag == 0:flag=1
        if(l[i] == 0 and flag == 1):
            l[i] = (i/sum([i for i in range(1,len(lst))]))*100*(least_score/100) 
    return sum(l)+additional_score  

def work_skill_score(skill_lst,param):
    work_skill_score={}
    max_score_val=param
    ttl_skills=len(skill_lst["Skills"])
    for k,v in candidate_work_skills.items():
        score=0
        for nm,val in skill_lst["Skills"].items():
            if nm in v["Skills"]:
                if v["Skills"][nm] == -1:
                    score += max_score_val/ttl_skills*0.70
                else:
                    time_penalize=12
                    if v["Skills"][nm] < val:
                        time_penalize=8
                    score += max_score_val/ttl_skills*0.70 + max_score_val/ttl_skills*0.30*tanh((v["Skills"][nm]-val)/time_penalize)
        work_skill_score[k]=score                           
    return work_skill_score

def education_score(edu_list,param):
    education_score={}
    for i in candidates_qualifications:
        education_score[i["name"]]=round(evaluate_education(i,edu_list,param),3)
    return education_score    

def skill_score(param):
    skill_score={}
    for i in candidates_skills:
        skill_score[i["name"]]=round(evaluate_skills(i,jd_taxonamies,param),3)
    return skill_score   
    
def scores(edu_list,work_list,work_skill_list,data):
    ttl={}
    es=education_score(edu_list,data["parameters"]["eduparameters"])
    ss=skill_score(data["parameters"]["skillparameters"])
    ws=samp.work_exp(work_list,data["parameters"]["weparameters"],r_path)
    wss=work_skill_score(work_skill_list,data["parameters"]["weparameters"]["skillExpScr"])
    for k,v in es.items():
        ws_score=0
        if k in ws:
            ws_score=ws[k]
        ttl[k]=(v*data["allValues"]["education"])+(ss[k]*data["allValues"]["skill"])+((ws_score+wss[k])*data["allValues"]["work experience"])
        ttl[k]=round(ttl[k]/100,3)
    list1=sorted( ttl.items(),key = lambda kv:kv[1] )  
    list1.reverse()
    sorted_list={} 
    sorted_list["order"]=[]
    for k in list1:
        t={}
        t[k[0]]={}
        sorted_list[k[0]]={}
        sorted_list["order"].append(k[0])
        sorted_list[k[0]]["Total Score"]=k[1]
        sorted_list[k[0]]["Education Score"]=round(es[k[0]]*data["allValues"]["education"]/100,3)
        sorted_list[k[0]]["Skill Score"]=round(ss[k[0]]*data["allValues"]["skill"]/100,3)
        sk=0
        if k[0] in ws:
            sk=ws[k[0]]
        sorted_list[k[0]]["Experience Score"]=round((sk+wss[k[0]])*data["allValues"]["work experience"]/100,3)
    return sorted_list    
