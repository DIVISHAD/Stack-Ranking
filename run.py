import json
import os
#import objectpath

jd_path="C:/Users/User/Desktop/Darwinbox/stack ranking/SovrenProductDemo-56_Resumes/SourceDocument/"
r_path="C:/Users/User/Desktop/Darwinbox/stack ranking/SovrenProductDemo-56_Resumes/TargetDocuments/"

candidates_skills=[]
candidates_qualifications=[]
jd_taxonamies={}
#highest len of SubTaxonomy
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

# def skill_score_():
#     score={}
#     for i in candidates_skills:
#         score[i["name"]]=round(evaluate_skills(i,jd_taxonamies),3)
#     list1=sorted( score.items(),key = lambda kv:kv[1] )  
#     list1.reverse()
#     sorted_list={} 
#     for k in list1:
#         sorted_list[k[0]]=k[1]
#     for k,v in sorted_list.items():
#         #st=k.split(".")[-2].split("[")[0].split("_")[-1]
#         print(k,v)

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
#print("\n---------------------------------------Skill Score------------------------------\n")
#skill_score_()


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
for i in candidates_qualifications:
    #print(i,"\n")
    if(i["name"]=="5d5fb8aac9c0a_1566554280_NitinAgrawal[12_0].docx"):
        pp=i     
#print(len(candidates_qualifications)) 

# print(pp)

# def education_score_(highest_degree):
#     education_score={}
#     for i in candidates_qualifications:
#         education_score[i["name"]]=round(evaluate_education_(i,highest_degree),3)
#     list1=sorted( education_score.items(),key = lambda kv:kv[1] )  
#     list1.reverse()
#     sorted_list={} 
#     for k in list1:
#         sorted_list[k[0]]=k[1]
#     for k,v in sorted_list.items():
#         #st=k.split(".")[-2].split("[")[0].split("_")[-1]
#         print(k,v)


# def evaluate_education_(j,min_d):
#     indx=0
#     for i in education_degree_type:
#         if min_d in i:
#             indx=education_degree_type.index(i)
#             break
#     lst=education_degree_type[0:indx+2]        
#     l=[0 for i in range(indx+2)]
#     d=j.get("candidate_degrees")
#     least_score=100
#     for i in d:
#         if i["DegreeScore"] != -1 and i["DegreeScore"]<least_score :least_score=i["DegreeScore"]
#     if least_score==100:least_score=60    
#     for i in d:
#         for dg in lst:
#             if i["DegreeType"] in dg:
#                 tst=lambda val: least_score if(val==-1) else val
#                 l[lst.index(dg)] = lst.index(dg)/sum([i for i in range(1,len(lst))])*100*(tst(i["DegreeScore"])/100)
#                 break
#     flag = 0
#     for i in range(len(lst)-1,0,-1):
#         if l[i] != 0 and flag == 0:flag=1
#         if(l[i] == 0 and flag == 1):
#             l[i] = (i/sum([i for i in range(1,len(lst))]))*100*(least_score/100)       
#     print(l)
#     return sum(l)
#print("\n---------------------------------------Education Score------------------------------\n")

#education_score_("masters")
# ttt=[{'DegreeType': 'bachelors', 'DegreeName': 'b.tech/b.e', 'DegreeMajor': 'cse', 'DegreeScore': 59, 'college_tier': ''},
#  {'DegreeType': 'masters', 'DegreeName': '', 'DegreeMajor': '', 'DegreeScore': 61, 'college_tier': ''}]

def evaluate_education(res,edu_list):
    indx=0
    for i in edu_list:
        if i["DegreeType"] in education_index.keys() and education_index[ i["DegreeType"]]>indx:
            indx = education_index[ i["DegreeType"]]
    lst=education_degree_type[0:indx+2]
    l=[0 for i in range(indx+2)]            
    d=res.get("candidate_degrees")
    least_score=100
    cnt=0
    sr=0
    for i in d:
        if i["DegreeScore"] != -1 :
            cnt+=1
            sr+=i["DegreeScore"]
    if cnt != 0:least_score=sr/cnt         
    if least_score==100:least_score=60 
    print("lst",least_score)
    tst=lambda val: least_score if(val==-1) else val
    for i in edu_list:
        if i["DegreeType"] !='':
            for j in d:
                if i["DegreeType"]==j["DegreeType"]:
                    if i["DegreeScore"]=='' or j["DegreeScore"]>=i["DegreeScore"] or (j["DegreeScore"]==-1 and least_score >= i["DegreeScore"]):
                        l[education_index[i["DegreeType"]]]=education_index[i["DegreeType"]]/sum([i for i in range(1,len(lst))])*100*(tst(j["DegreeScore"])/100)
                        print(education_index[i["DegreeType"]],1)
                    elif j["DegreeScore"]<i["DegreeScore"] or least_score < i["DegreeScore"]:
                        l[education_index[i["DegreeType"]]]=education_index[i["DegreeType"]]/sum([i for i in range(1,len(lst))])*100*(tst(j["DegreeScore"])/100)*0.75
                        print(education_index[i["DegreeType"]],2)
                    break        
    for i in d:
        for dg in lst:
            if i["DegreeType"] in dg:
                if l[lst.index(dg)] == 0:
                    l[lst.index(dg)] = lst.index(dg)/sum([i for i in range(1,len(lst))])*100*(tst(i["DegreeScore"])/100)
                break
    flag = 0
    for i in range(len(lst)-1,0,-1):
        if l[i] != 0 and flag == 0:flag=1
        if(l[i] == 0 and flag == 1):
            l[i] = (i/sum([i for i in range(1,len(lst))]))*100*(least_score/100) 
    print(l)              
    return sum(l)

def education_score(edu_list):
    education_score={}
    for i in candidates_qualifications:
        education_score[i["name"]]=round(evaluate_education(i,edu_list),3)
    return education_score    

def skill_score():
    skill_score={}
    for i in candidates_skills:
        skill_score[i["name"]]=round(evaluate_skills(i,jd_taxonamies),3)
    return skill_score   
    
def scores(edu_list,data):
    ttl={}
    es=education_score(edu_list)
    ss=skill_score()
    for k,v in es.items():
        ttl[k]=(v*data["education"])+(ss[k]*data["skill"])
        ttl[k]=round(ttl[k]/100,3)
    list1=sorted( ttl.items(),key = lambda kv:kv[1] )  
    list1.reverse()
    sorted_list={} 
    for k in list1:
        sorted_list[k[0]]={}
        sorted_list[k[0]]["Total Score"]=k[1]
        sorted_list[k[0]]["Education Score"]=round(es[k[0]]*data["education"]/100,3)
        sorted_list[k[0]]["Skill Score"]=round(ss[k[0]]*data["skill"]/100,3)
    return sorted_list    

