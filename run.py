import json
import os
import samp
import pymongo


client = pymongo.MongoClient("mongodb+srv://divishad:abcde@cluster0-gdmit.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = client.StackRanking.education


jd_path="C:/Users/User/Desktop/Darwinbox/stack ranking/SovrenProductDemo-14_Resumes/SourceDocument/"
r_path="C:/Users/User/Desktop/Darwinbox/stack ranking/SovrenProductDemo-14_Resumes/TargetDocuments/"

# list of json of skills for each candidate
candidates_skills=[]
# list of json of education qualifactions for each candidate
candidates_qualifications=[]
# parsed skills in jd 
jd_taxonamies={}
candidate_work_skills={}
# highest len of a SubTaxonomy
constant=0

# extracting candidate skills from candidate's parsed resume
#candidate_skills=[ {
#     Name:candidate Name1
#     Taxonamy Name1:{
#         SubTaxonamy Name1:{
#             Skill1:[ChildSkills if there are any else empty list]
#         }
#         Percent:Percent of overall of SubTaxonamy1
#     }
# } ]
# candidate_work_skills={
#     Name1:{
#         Skills:{
#             Skill Name1:Totalmonths used
#         }
#     }
# }
# candidates_qualifications=[
#     name:candidate name1,
#     EducationDegrees:[
#         {
#             DegreeType: type of degree1,
#             DegreeName: name of degree1,
#             DegreeMajor: field od degree1,
#             DegreeScore:score in degree1,
#             CollegeTier:tier of college
#         }
#     ]
# ]

for nm in os.listdir(r_path):
    candidate_taxonamies={}
    candidate_work_skills[nm]={}
    candidate_work_skills[nm]["Skills"]={}
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
                                if "@whereFound" in sub:
                                    # print(sub["@whereFound"][8:].split(";"))
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

#same as skill taxonamy of candidates
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
                
# for i in candidates_skills:
#     print(i,"\n\n")
#     break
# for i in candidate_work_skills:
#     print(i,candidate_work_skills[i],"\n\n")
#     break
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

# ->if Child skill in jd matches with child skill in candidate_child skill : score of child skill gets added
# if all the child_skills in jd didnt match and candidate has child skills that are not in jd:
#     extra partial score is given such that total score doesnt exceed limit
# ->if jd has child skills and candidate doesnt have child skills but name of skill matches partial score for that skill is given   
# ->if skill name matches and no child skills for that in jd score of skill is given
# ->for skill scoring is given same as child skills


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

# levels of education
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
# ttt=[{'DegreeType': 'bachelors', 'DegreeName': 'b.tech/b.e', 'DegreeMajor': 'cse', 'DegreeScore': 61, 'college_tier': ''},
#  {'DegreeType': 'masters', 'DegreeName': '', 'DegreeMajor': '', 'DegreeScore': 59, 'college_tier': ''}]

def evaluate_education(res,edu_list):
    indx=0
    for i in edu_list:
        if i["DegreeType"] in education_index.keys() and education_index[ i["DegreeType"]]>indx:
            indx = education_index[ i["DegreeType"]]
    if indx==0:indx=len(education_degree_type)-2
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
    #print("lst",least_score)
    tst=lambda val: least_score if(val==-1) else val
    for i in edu_list:
        if i["DegreeType"] !='':
            for j in d:
                if i["DegreeType"]==j["DegreeType"]:
                    scr=education_index[i["DegreeType"]]/sum([i for i in range(1,len(lst))])*100*(tst(j["DegreeScore"])/100)
                    if i["DegreeName"]=='' or i["DegreeName"].lower()==j["DegreeName"].lower():
                        if i["DegreeMajor"]=='' or i["DegreeMajor"].lower()==j["DegreeMajor"].lower():
                            if i["CollegeTier"]=='' or j["CollegeTier"]<=i["CollegeTier"]:
                                if i["DegreeScore"]=='' or j["DegreeScore"]>=i["DegreeScore"] or (j["DegreeScore"]==-1 and least_score >= i["DegreeScore"]):
                                    if l[education_index[i["DegreeType"]]]<scr:
                                        l[education_index[i["DegreeType"]]]=scr
                                    #print(education_index[i["DegreeType"]],1)
                                elif j["DegreeScore"]<i["DegreeScore"] or least_score < i["DegreeScore"]:
                                    if l[education_index[i["DegreeType"]]]<(scr*0.75):
                                        l[education_index[i["DegreeType"]]]=scr*0.75
                                    #print(education_index[i["DegreeType"]],2)
                            else:
                                if l[education_index[i["DegreeType"]]]<(scr*0.65):
                                    l[education_index[i["DegreeType"]]]=scr*0.65       
                        else:
                            if l[education_index[i["DegreeType"]]]<(scr*0.50):
                                l[education_index[i["DegreeType"]]]=scr*0.50
                    else:
                        if l[education_index[i["DegreeType"]]]<(scr*0.25):
                            l[education_index[i["DegreeType"]]]=scr*0.25                
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
    #print(l)              
    return sum(l)
def work_skill_score(skill_lst):
    work_skill_score={}
    max_score_val=30
    ttl_skills=len(skill_lst["Skills"])
    for k,v in candidate_work_skills.items():
        score=0
        for nm,val in skill_lst["Skills"].items():
            if nm in v["Skills"]:
                if val==None or v["Skills"][nm] >= val:
                    score+=max_score_val/ttl_skills
                else:
                    score+=max_score_val/ttl_skills*0.75
        work_skill_score[k]=score                           
    return work_skill_score

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
    
def scores(edu_list,work_list,work_skill_list,data):
    ttl={}
    es=education_score(edu_list)
    ss=skill_score()
    ws=samp.work_exp(work_list)
    wss=work_skill_score(work_skill_list)
    for k,v in es.items():
        # print(ss[k])
        # print(ws[k])
        # print(wss[k])
        ws_score=0
        if k in ws:
            ws_score=ws[k]
        ttl[k]=(v*data["education"])+(ss[k]*data["skill"])+((ws_score+wss[k])*data["work experience"])
        ttl[k]=round(ttl[k]/100,3)
    list1=sorted( ttl.items(),key = lambda kv:kv[1] )  
    list1.reverse()
    # for i in list1:
    #     print(i)
    sorted_list={} 
    sorted_list["order"]=[]
    for k in list1:
        t={}
        t[k[0]]={}
        sorted_list[k[0]]={}
        sorted_list["order"].append(k[0])
        sorted_list[k[0]]["Total Score"]=k[1]
        sorted_list[k[0]]["Education Score"]=round(es[k[0]]*data["education"]/100,3)
        sorted_list[k[0]]["Skill Score"]=round(ss[k[0]]*data["skill"]/100,3)
        sk=0
        if k[0] in ws:
            sk=ws[k[0]]
        sorted_list[k[0]]["Experience Score"]=round((sk+wss[k[0]])*data["work experience"]/100,3)

    # for i,p in sorted_list.items():print(i,p)
    # print("mohit                         ",sorted_list["5d44912169e2e_Mohit Full Stack Developer and Techno Manager.docx"]["Experience Score"])    
    return sorted_list    

# scores(ttt,{"education":33,"skill":34})
# sample={'Skills': {'DISTRIBUTED SYSTEMS': None,'MONGODB': None}}
# aaaa=work_skill_score(sample)
# for k,v in aaaa.items():print(k,v)
# print(aaaa["5d44912169e2e_Mohit Full Stack Developer and Techno Manager.docx"])

