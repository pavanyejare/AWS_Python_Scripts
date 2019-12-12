#!/usr/bin/python3
import boto3
import sys
import csv
from botocore.exceptions import ClientError
import os
from datetime import datetime, timedelta
import datetime 
from prettytable import from_csv
from openpyxl import Workbook

def tags(instance_id,region,current_status):
    try : 
        client=boto3.client('ec2', region_name=region)
        result=client.describe_instances(InstanceIds=[instance_id])
        for reservation in result['Reservations']:
            for info in reservation['Instances']:
                inst_type = info['InstanceType']
                inst_life = 'On-Demand'
                if 'InstanceLifecycle' in info:
                    inst_life = info['InstanceLifecycle']
                inst_state = info['State']['Name']
                inst_time = info['LaunchTime']
                inst_time = inst_time.strftime("%Y-%m-%d")
                creator = 'NULL'
                name= 'NULL'
                if 'Tags' in info:
                    for tags in info['Tags']:
                        if (tags['Key']=='Name' or tags['Key']=='name'):
                            name = tags['Value']
                        if  (tags['Key']=='Creator'):
                            creator = tags['Value']
            inst_dict={'ID':instance_id, 'Name': name , 'Creator' : creator, 'Inst_type' : inst_type ,'Inst_life' : inst_life, 'current_status':current_status, 'Inst_state':inst_state, 'Time':inst_time}
    except ClientError as e:
        print(e)
    return inst_dict
def region():
    region_list=[]
    client=boto3.client('ec2')
    response = client.describe_regions()
    for region in response['Regions']:
        region_list.append(region['RegionName'])

    return region_list
    #return ['ap-southeast-1']

def ec2_id():
    current_status='stopped'
    data_list=[]
    regions=region()
    for r in regions:
        ec2=boto3.resource('ec2', region_name=r)
        instance=ec2.instances.filter(Filters=[{'Name': 'instance-state-name','Values': [current_status]}])
        count=0
        inst_tags=[]
        for i in instance:
            tags_dict = tags(i.id,r,current_status)
            inst_tags.append(tags_dict)
            count += 1
        region_tags = {'Region' : r , 'Tags' : inst_tags}
        data_list.append(region_tags)
    current_status='running'
    for r in regions:
        ec2=boto3.resource('ec2', region_name=r)
        instance=ec2.instances.filter(Filters=[{'Name': 'instance-state-name','Values': [current_status]}])
        count=0
        inst_tags=[]
        for i in instance:
            tags_dict = tags(i.id,r,current_status)
            inst_tags.append(tags_dict)
            count += 1
        region_tags = {'Region' : r , 'Tags' : inst_tags}
        data_list.append(region_tags)
    return data_list




def write_faild(region,i_id,creator,name,i_type,i_life,current_status,inst_time):
    with open('running_ins.csv', 'a') as csvfile:
        fieldnames = ['Region', 'ID' ,'Type', 'Life','Creator', 'Status', 'Time', 'Name' ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",")
        writer.writerow({'Region': region, 'ID': i_id,'Type':i_type,'Life':i_life,'Creator':creator,'Status':current_status,'Time':inst_time,'Name':name})

def write_null_id(region,i_id,i_type,i_life,creator,current_status,name,inst_time):
    with open('null_value.csv', 'a') as csvfile:
        fieldnames = ['Region', 'ID' , 'Type','Life','Creator','Status', 'Time', 'Name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",")
        writer.writerow({'Region': region, 'ID': i_id,'Type':i_type,'Life':i_life,'Creator':creator,'Status':current_status,'Time': inst_time,'Name':name})

def csv_header():
    with open('running_ins.csv', 'a') as csvfile:
        fieldnames = ['Region', 'ID' ,'Type', 'Life' ,'Creator', 'Status', 'Time' ,'Name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",")
        writer.writeheader()
    with open('null_value.csv', 'a') as csvfile:
        fieldnames = ['Region', 'ID','Type', 'Life' , 'Creator','Status','Time', 'Name',]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",")
        writer.writeheader()

def mail():
    with open("running_ins.csv", "r") as fp: 
        x = from_csv(fp)
    f= open("val_table.txt","w+")
    f.write(str(x))
    f.close()
    wb = Workbook()
    ws = wb.active
    with open('running_ins.csv', 'r') as f:
        for row in csv.reader(f):
            ws.append(row)
    wb.save('all_instance_.xlsx')
    with open('running_ins.csv', 'r') as book1:
        r = csv.reader(book1, delimiter=',')
        for row in r:
            if (row[4] == 'NULL'):
                write_null_id(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])
                

    date=datetime.datetime.now()
    date=date.strftime("%Y-%m-%d %H:%M:%S")
    cmd = "cat running_ins.csv | column -t > /tmp/running.txt"
    os.system(cmd)
    cmd =  "mutt -s 'Running Instnace and Tags "+ date +" '  -c MAIL_ID -a /tmp/running_ins.csv < /tmp/running.txt"
    #os.system(cmd)
    cmd = "rm -rf running*"
    #os.system(cmd)
    
def main():
    csv_header()
    #dash = '-' * 40
    instance=ec2_id()
    #print (dash)
    #print('{:<10s}{:>4s}{:>12s}{:>12s}'.format('Region','ID','Creator','Name'))
    #print (dash)
    for i in instance:
        if i['Tags']:
            for tags in i['Tags']:
                write_faild(i['Region'],tags['ID'],tags['Creator'],tags['Name'],tags['Inst_type'],tags['Inst_life'],tags['current_status'],tags['Time'])
    mail()

main()


