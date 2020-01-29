import json
import os
#import objectpath

jd_path="C:/Users/User/Desktop/Darwinbox/stack ranking/SovrenProductDemo-56_Resumes/SourceDocument/"
r_path="C:/Users/User/Desktop/Darwinbox/stack ranking/SovrenProductDemo-56_Resumes/TargetDocuments/"

candidates_skills=[]
candidates_qualifications=[]
jd_taxonamies={}
constant=0

for nm in os.listdir(r_path):
    candidate_taxonamies={}
    candidate_taxonamies["name"]=nm
    with open(r_path+nm+"/"+nm+".json",'r',encoding='cp850') as file:
        #print(nm)
        data=json.load(file)
        a=data.get("Resume").get("UserArea").get("sov:ResumeUserArea").get("sov:ExperienceSummary").get("sov:SkillsTaxonomyOutput").get("sov:TaxonomyRoot")[0].get("sov:Taxonomy")
        #json_tree = objectpath.Tree(data)
        #result_tuple = tuple(json_tree.execute('$..@name'))
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
                        candidate_taxonamies[i["@name"]][j["@name"]][k["@name"]]=child_skills  
        candidates_skills.append(candidate_taxonamies)

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
                if len(jd_taxonamies[i["@name"]][j["@name"]]) >= constant:
                    #print(jd_taxonamies[i["@name"]][j["@name"]])
                    constant = len(jd_taxonamies[i["@name"]][j["@name"]])   
                
#for i in candidates_skills:print(i,"\n\n")
#print(type(jd_taxonamies))
#for i in jd_taxonamies:print(i)    
#print(jd_taxonamies)    
#print(constant)

def skill_score():
    score={}
    for i in candidates_skills:
        score[i["name"]]=round(evaluate_skills(i,jd_taxonamies),3)
    list1=sorted( score.items(),key = lambda kv:kv[1] )  
    list1.reverse()
    sorted_list={} 
    for k in list1:
        sorted_list[k[0]]=k[1]
    for k,v in sorted_list.items():
        #st=k.split(".")[-2].split("[")[0].split("_")[-1]
        print(k,v)

def evaluate_skills(candidate,json):
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
                                    score += (val / (len(subTaxonomy_value)-1)) / len(skill_value)
                            if len(skill_value) == 0 :
                                score += (val / (len(subTaxonomy_value)-1))
                            elif len(candidate_childSkill_list) == 0 :
                                score += (val / (len(subTaxonomy_value)-1)) / (len(skill_value)+1)
                            elif len(candidate_childSkill_list) != 0 :
                                len_nonMatch = len(candidate_childSkill_list)-childSkill_match
                                if childSkill_match != len(skill_value):
                                    score += (len_nonMatch)*(val/(len(subTaxonomy_value)-1))/(len(skill_value) + 2*len_nonMatch) 
                    if len(subTaxonomy_value) == 1 :
                        score +=val
                    elif len(candidate_skills) == 0 :
                        score += val / len(subTaxonomy_value)
                    elif len(candidate_skills) != 0 :
                        nonMatch_skills=len(candidate_skills)-skill_match
                        #print(skill_match ,nonMatch_skills,val,(len(subTaxonomy_value)-1))
                        if skill_match != (len(subTaxonomy_value)-1):
                            score += nonMatch_skills*val/(len(subTaxonomy_value)-1+ constant*nonMatch_skills)            
    return  score  
print("\n---------------------------------------Skill Score------------------------------\n")
skill_score()


education_degree_type = [['specialeducation'],['some high school or equivalent','ged','secondary'],
                        ['high school or equivalent','certification','vocational','some college'],
                        ['HND/HNC or equivalent','associates','international'],['bachelors'],
                        ['some post-graduate','masters','intermediategraduate'],['professional'],
                        ['postprofessional'],['doctorate'],['postdoctorate']]
index=0                        
score_degree_type=index*(index+1)/110                        


for i in os.listdir(r_path):
    candidate_education={}
    candidate_education["name"]=i
    candidate_education["candidate_degrees"]=[]
    with open(r_path+i+"/"+i+".json",'r',encoding='cp850') as file:
        #print(i)
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
                        degree["DegreeName"]=deg.get("Degree")[0].get("DegreeName")
                    else:degree["DegreeName"]=""    
                    if "DegreeMajor" in deg.get("Degree")[0]:
                        degree["DegreeMajor"]=deg.get("Degree")[0].get("DegreeMajor")[0].get("Name")[0]
                    else:degree["DegreeMajor"]=""    
                    if "sov:NormalizedGPA" in deg.get("Degree")[0].get("UserArea").get("sov:DegreeUserArea"):
                        degree["DegreeScore"]=float(deg.get("Degree")[0].get("UserArea").get("sov:DegreeUserArea").get("sov:NormalizedGPA"))*100
                    else:degree["DegreeScore"]=-1
                candidate_education["candidate_degrees"].append(degree)    
        candidates_qualifications.append(candidate_education) 
pp={}
# for i in candidates_qualifications:
#     #print(i,"\n")
#     if(i["name"]=="5d5fb8aac9c0a_1566554280_NitinAgrawal[12_0].docx"):
#         pp=i     
# print(len(candidates_qualifications)) 

# print(pp)

def education_score(highest_degree):
    education_score={}
    for i in candidates_qualifications:
        education_score[i["name"]]=round(evaluate_education(i,highest_degree),3)
    list1=sorted( education_score.items(),key = lambda kv:kv[1] )  
    list1.reverse()
    sorted_list={} 
    for k in list1:
        sorted_list[k[0]]=k[1]
    for k,v in sorted_list.items():
        #st=k.split(".")[-2].split("[")[0].split("_")[-1]
        print(k,v)


def evaluate_education(j,min_d):
    indx=0
    for i in education_degree_type:
        if min_d in i:
            indx=education_degree_type.index(i)
            break
    lst=education_degree_type[0:indx+2]        
    l=[0 for i in range(indx+2)]
    d=j.get("candidate_degrees")
    least_score=100
    for i in d:
        if i["DegreeScore"] != -1 and i["DegreeScore"]<least_score:least_score=i["DegreeScore"]
    if least_score==100:least_score=60    
    for i in d:
        for dg in lst:
            if i["DegreeType"] in dg:
                tst=lambda val: least_score if(val==-1) else val
                l[lst.index(dg)] = lst.index(dg)/sum([i for i in range(1,len(lst))])*100*(tst(i["DegreeScore"])/100)
                break
    flag = 0
    for i in range(len(lst)-1,0,-1):
        if l[i] != 0 and flag == 0:flag=1
        if(l[i] == 0 and flag == 1):
            l[i] = (i/sum([i for i in range(1,len(lst))]))*100*(least_score/100)       
    return sum(l)
print("\n---------------------------------------Education Score------------------------------\n")

education_score("masters")