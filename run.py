import json
import os
import objectpath

jd_path="C:/Users/User/Desktop/Darwinbox/stack ranking/SovrenProductDemo-14_Resumes/SourceDocument/"
r_path="C:/Users/User/Desktop/Darwinbox/stack ranking/SovrenProductDemo-14_Resumes/TargetDocuments/"

candidate_skills=[]
jd_taxonamies={}
for i in os.listdir(r_path):
    candidate_taxonamies={}
    candidate_taxonamies["name"]=i
    with open(r_path+i+"/"+i+".json",'r',encoding='cp850') as file:
        #print(i)
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
        candidate_skills.append(candidate_taxonamies)

for i in os.listdir(jd_path):
    with open(jd_path+i+"/"+i+".json",'r',encoding='cp850') as file:
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
                
#for i in candidate_skills:print(i,"\n\n")
#for i in jd_taxonamies:print(i)    
#print(jd_taxonamies)    

def skill_score():
    score={}
    for i in candidate_skills:
        score[i["name"]]=round(evaluate(i,jd_taxonamies),3)
    list1=sorted(score.items(), key = lambda kv:(kv[1], kv[0]))  
    list1.reverse()
    sorted_list={} 
    for k in list1:
        sorted_list[k[0]]=k[1]
    for k,v in sorted_list.items():
        print(k,v)

def evaluate(candidate,json):
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
                                score += (len_nonMatch)*(val/(len(subTaxonomy_value)-1))/(len(skill_value) + 2*len_nonMatch) 
                    if len(subTaxonomy_value) == 1 :
                        score +=val
                    elif len(candidate_skills) == 0 :
                        score += val / len(subTaxonomy_value)
                    elif len(candidate_skills) != 0 :
                        nonMatch_skills=len(candidate_skills)-skill_match
                        #print(skill_match ,nonMatch_skills,val,(len(subTaxonomy_value)-1))
                        score += nonMatch_skills*val/(len(subTaxonomy_value)-1+ 4*nonMatch_skills)            
    return  score  

skill_score()