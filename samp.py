"""
Created on Wed Jan 22 18:08:24 2020
@author: khyati
"""
import json
import os
import pymongo
from datetime import datetime
import operator
import math
def work_exp(inputlist):

    resd={}
    client = pymongo.MongoClient("mongodb+srv://divishad:abcde@cluster0-gdmit.gcp.mongodb.net/test?retryWrites=true&w=majority")
    db = client.StackRanking.education
    mypathh='C:/Users/User/Desktop/Darwinbox/stack ranking/SovrenProductDemo-14_Resumes/TargetDocuments/' 
    gd={}
    comp_str={}
    for f in os.listdir(mypathh):
        with open(mypathh+f+"/"+f+".json",'r',encoding='cp850') as file:
            data=json.load(file)
            if 'EmploymentHistory' in data["Resume"]["StructuredXMLResume"]:
                a=data["Resume"]["StructuredXMLResume"]["EmploymentHistory"]["EmployerOrg"]
                ud={}
                comp={}
                for i in range(len(a)):
                    pos_hist_roles=[]
                    for j in range(len(a[i]["PositionHistory"])):
                        
                        pos_hist_role={}
                        title=""
                        pht={}
                        if "StartDate" and "EndDate" in a[i]["PositionHistory"][j]:
                                
                            sdd=a[i]["PositionHistory"][j]["StartDate"]
                            for _ in sdd:
                                if _ == "YearMonth":
                                    sd=sdd["YearMonth"]
                                    
                                if _=="AnyDate":
                                    if sdd["AnyDate"]=="notKnown":
                                        break
                                    else:
                                        sd=sdd["AnyDate"]
                                if _=="Year":
                                    sd=sdd["Year"]+"-00"
                            ldd=a[i]["PositionHistory"][0]["EndDate"]
                            for _ in ldd:
                                if _ == "YearMonth":
                                    ld=ldd["YearMonth"]
                                if _=="AnyDate":
                                    ld=ldd["AnyDate"]
                                if _=="Year":
                                    ld=ldd["Year"]+"-00"
                                if _=="StringDate":
                                    currentMonth = datetime.now().month
                                    currentYear = datetime.now().year
                                    ld=str(currentYear)+"-"+str(currentMonth)
                            pht[sd]=ld                               
                            sd=sd.split("-")
                            ld=ld.split("-")
                            sd=sd[:2]
                            ld=ld[:2]
                            nl=[]
                            for _ in range(len(sd)):
                                nl.append(int(ld[_])-int(sd[_]))
                            nl[0]=nl[0]*12
                            exp=nl[0]+nl[1]
                            pht["experience"]=exp
        
                        else:
                            exp=0
                            pht["experience"]=exp
                        if "UserArea" in a[i]["PositionHistory"][j]:
                            area=a[i]["PositionHistory"][j]["UserArea"]["sov:PositionHistoryUserArea"]
                            if "sov:NormalizedTitle" in area:
                                title=area["sov:NormalizedTitle"]
                            if "sov:Subtitles" in area:
                                for _ in range(len(area["sov:Subtitles"]["sov:Subtitle"])):
                                    title=title+"/"+area["sov:Subtitles"]["sov:Subtitle"][_]
                        if "JobCategory" in a[i]["PositionHistory"][j]:
                            if len(a[i]["PositionHistory"][j]["JobCategory"])==1:
                                pht["CategoryCode"]=a[i]["PositionHistory"][j]["JobCategory"][0]["CategoryCode"]
                            elif len(a[i]["PositionHistory"][j]["JobCategory"])==2:
                                pht["CategoryCode"]=a[i]["PositionHistory"][j]["JobCategory"][1]["CategoryCode"]
                        pos_hist_role[title]=pht
                        pos_hist_roles.append(pos_hist_role)
                    if "UserArea" in a[i]:
                        comp[a[i]["UserArea"]["sov:EmployerOrgUserArea"]["sov:NormalizedEmployerOrgName"]]=pos_hist_roles
                    else:
                        comp[""]=pos_hist_roles
                comp_str[f]=comp    
                gd[f]=ud
            else:
                resd[f]=0
    
    for i in comp_str:
        score=0
        nlscore=0
        njdscore=0
        recent=1000
        orgcount=0
        for j in comp_str[i]:
            orgcount=orgcount+1
            company_tier=db.find_one({"key":"CompanyTier"})["CompanyTier"].get(j)
            if company_tier==None:
                company_tier=3
            for k in range(len(comp_str[i][j])): 
                totalexp=0
                cc=0
                for title in comp_str[i][j][k]:
                    
                    for key in comp_str[i][j][k][title]:
                        if key=="experience":
                            totalexp=totalexp+comp_str[i][j][k][title][key]
                    count=0
                    nlcount=0
                    njdcount=0
                    if title !="":
                        resume_list=title.split("/")
                        cc=cc+len(resume_list)   
                        for z in inputlist:
                            
                            if 'Experience' in z:
                                if z["Experience"]!='':
                                    jdexp=z['Experience']
                                elif z["Experience"]=="":
                                    jdexp=0
                        
                            if z['JobPosition']!="":
                                if z['JobPosition'] in resume_list:
                                    if z["CompanyTier"]=='':
                                        jdtier=3
                                        score=10+math.tanh((company_tier-jdtier)/1.5)
                                    elif z["CompanyTier"]!='':
                                        jdtier=int(z["CompanyTier"])
                                        score=10+math.tanh((company_tier-jdtier)/1.5)
                                    count=count+1
                                    for key in comp_str[i][j][k][title]:
                                        
                                            
                                        if key!="experience" and key!="CategoryCode":
                                             #print(key,len(key),type(comp_str[i][j][k][title][key]),"dsv ")
                                             currentMonth = datetime.now().month
                                             currentYear = datetime.now().year
                                             ld=str(currentYear)+"-"+str(currentMonth)
                                             #sd=value.split("-")
                                             if len(key)==4:
                                                 sd=comp_str[i][j][k][title][key]+"-00"
                                                 #print(sd,"fdkb")
                                             sd=comp_str[i][j][k][title][key].split("-")
                                             ld=ld.split("-")
                                             #print(sd,ld)
                                             sd=sd[:2]
                                             ld=ld[:2]
                                             nl=[]
                                            
                                             #print(sd,ld)
                                             for _ in range(len(sd)):
                                                 nl.append(int(ld[_])-int(sd[_]))
                                             nl[0]=nl[0]*12
                                             new_recent=nl[0]+nl[1]
                                             if new_recent<recent:
                                                 recent=new_recent/12
                                             if recent!=1000:
                                                score=score+10/(1+0.2*recent)
                                     
                                        if key=="experience":
                                            bws=comp_str[i][j][k][title][key]/12
                                            extra=(bws-(int(jdexp)))/5
                                            score=score+45+(5*math.tanh(extra))  
                                else:
                                   nlcount=nlcount+1
                                   nlscore=nlscore+10
                           
                            elif z['JobPosition']=="":
                                njdcount=njdcount+1
                                njdscore=njdscore+20

                        if count!=0:
                            score=score/count
                            #print(score)
                        if nlcount!=0:
                            nlscore=nlscore/nlcount
                   
            if njdcount!=0:
                njdscore=njdscore/njdcount
        score=score+nlscore+njdscore
        #score=score/orgcount
        resd[i]=score/len(inputlist)
    #print(resd)                            
    resd=dict( sorted(resd.items(), key=operator.itemgetter(1),reverse=True))
    return resd

k=work_exp([
{"JobPosition":"Software Development Engineer",
"CompanyTier":"3",
"Experience":"2"
 
},


{"JobPosition":"Software Engineer",
"CompanyTier":"",
"Experience":"4"

},
{"JobPosition":"",
"CompanyTier":"",
"Experience":""
 
}

]) 
