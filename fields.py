import json
import os
import samp

import pymongo


client = pymongo.MongoClient("mongodb+srv://divishad:abcde@cluster0-gdmit.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = client.StackRanking

jd_path="C:/Users/User/Desktop/Darwinbox/stack ranking/SovrenProductDemo-14_Resumes/SourceDocument/"
r_path="C:/Users/User/Desktop/Darwinbox/stack ranking/SovrenProductDemo-14_Resumes/TargetDocuments/"
degree_type=[]
degree_name=[]
college_name=[]
degree_major=[]
c=0
for nm in os.listdir(r_path):
    with open(r_path+nm+"/"+nm+".json",'r',encoding='cp850') as file:
        data=json.load(file)
        if data.get("Resume").get("StructuredXMLResume").get("EducationHistory") != None:
            a=data.get("Resume").get("StructuredXMLResume").get("EducationHistory").get("SchoolOrInstitution")
            c+=len(a)
            for deg in a:
                a1,a2,a3,a4="","","",""
                if "Degree" in deg:
                    if "@degreeType" in deg.get("Degree")[0]:
                        degree_type.append(deg.get("Degree")[0].get("@degreeType"))
                        a1=deg.get("Degree")[0].get("@degreeType")
                    if "DegreeName" in deg["Degree"][0]:
                        degree_name.append(deg["Degree"][0]["DegreeName"])
                        a2=deg["Degree"][0]["DegreeName"]
                    if "DegreeMajor" in deg.get("Degree")[0]:
                        degree_major.append(deg.get("Degree")[0].get("DegreeMajor")[0].get("Name")[0])
                        a3=deg.get("Degree")[0].get("DegreeMajor")[0].get("Name")[0]
                if "UserArea" in deg:
                    if "sov:SchoolOrInstitutionTypeUserArea" in deg["UserArea"]:
                        if "sov:NormalizedSchoolName" in deg["UserArea"]["sov:SchoolOrInstitutionTypeUserArea"]:
                            college_name.append(deg["UserArea"]["sov:SchoolOrInstitutionTypeUserArea"]["sov:NormalizedSchoolName"])
                            a4=deg["UserArea"]["sov:SchoolOrInstitutionTypeUserArea"]["sov:NormalizedSchoolName"]
                print(a1,a2,a3,a4,sep=", ")            


print(len(degree_type),len(degree_name),len(degree_major),len(college_name),c)

for i in range(0,24):
    if len(degree_type)>i:
        a=degree_type[i]
    else:a="" 
    if len(degree_name)>i:
        b=degree_name[i]
    else:b=""
    if len(degree_major)>i:
        c1=degree_major[i]
    else:c1=""
    if len(college_name)>i:
        d=college_name[i]
    else:d=""
    # print(a,b,c1,d,sep=", ") 
# print(degree_name)
# print(degree_major)
# print(college_name)  
print(db.education.find_one({"key":"DegreeName"}))
org_name=[]
for nm in os.listdir(r_path):
    with open(r_path+nm+"/"+nm+".json",'r',encoding='cp850') as file:
        data=json.load(file)
        if data.get("Resume").get("StructuredXMLResume").get("EmploymentHistory") != None:
            a=data.get("Resume").get("StructuredXMLResume").get("EmploymentHistory")
            if "EmployerOrg" in a:
                for i in a["EmployerOrg"]:
                    org_name.append(i["EmployerOrgName"])
for i in org_name:print(i)
