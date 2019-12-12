from collections import Counter
import sys
import boto3
import json

#count = 0
all_sg_list=[]
list_group=[]
vul_instance_set = set()
ec2 = boto3.client('ec2')
instances=ec2.describe_instances()
response=ec2.describe_security_groups()
def get_instances(z):
    total_vul_sg_instances_count=0
    instances = ec2.describe_instances(Filters=[{'Name':'instance.group-id', 'Values':[z]}])
    for i in instances['Reservations']:
        for j in i['Instances']:
            print("Insatnce Id = ", j['InstanceId'])
            vul_instance_set.add(j['InstanceId'])
            total_vul_sg_instances_count += 1
    #print ("Total Vulnerable Insntaces Count"  ,z ,total_vul_sg_instances_count)

def unused_sg():
    all_instances = ec2.describe_instances() 
    all_sg = ec2.describe_security_groups()

    instance_sg_set = set()
    sg_set = set()

    for reservation in all_instances["Reservations"] :
        for instance in reservation["Instances"]: 
                for sg in instance["SecurityGroups"]:
                    instance_sg_set.add(sg["GroupId"]) 
                #print("Hi")
    
    for security_group in all_sg["SecurityGroups"] :
        sg_set.add(security_group ["GroupId"])

    idle_sg = sg_set - instance_sg_set
    return len(idle_sg),idle_sg
    #print("Unused Security Group :", len(idle_sg))
    #print("Unused Security Group IDS:", idle_sg)

def vul_rules():
    count=0
    for i in response['SecurityGroups']:
        #print("SG : ", i)
        all_sg_list.append(i['GroupId'])
        for j in i['IpPermissions']:
            try:
                port=j['FromPort']  
                for k in j['IpRanges']:
                    if ( port == 22 and k['CidrIp'] == "0.0.0.0/0" ):
                        print ("ID : ",i['GroupId'],"\t Port:", port ,"\t Open_IP: ", k['CidrIp'])
                    if (port in(22) and k['CidrIp'] == "0.0.0.0/0"):
                        count += 1
                        list_group.append(i['GroupId'])
            except Exception:
                continue
    newlist=list(set(list_group))
    #print ("List SG : ", list_group)
    print ("Vul SG List" ,newlist)
    print ("Vul SG Count" ,len(newlist))
    print ("Vul Rules" ,count)
    print ("Total SG", len(all_sg_list))
    for i in newlist:
        get_instances(i)
    return len(newlist),newlist,count,len(all_sg_list),all_sg_list
    #print (i)
    #print ("Vul Instance Count" ,len(vul_instance_set))
#unused_sg()
vul_rules()

