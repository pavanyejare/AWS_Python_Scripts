#!/usr/bin/python3
import boto3
import sys




def region():
    region_list=[]
    client=boto3.client('ec2')
    response = client.describe_regions()
    for region in response['Regions']:
        region_list.append(region['RegionName'])

    return region_list


def ec2_id():
    regions=region()
    for r in regions:
        #ec2=boto3.client('ec2', region_name='ap-southeast-1')
        ec2=boto3.client('ec2', region_name=r)
        #data  = ec2.describe_instances(Filters=[{'Name':'instance-id', 'Values':['i-0c2ea811310162c7a']}])
        data  = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped', 'running']}])
        for i in data['Reservations']:
            for j in  i['Instances']:
                name = 'NONE'
                if 'Tags' in j:
                    for tags in j['Tags']:
                        if (tags['Key']=='Name' or tags['Key']=='name'):
                            name = tags['Value']
                print ("Instance Name: ", name, "   Instance ID: ", j['InstanceId'], "   Region:", r)
                root_device=j['RootDeviceName']
                volumes=[]
                for i in  j['BlockDeviceMappings']:
                    if ( root_device == i['DeviceName'] ):
                        root_id=i['Ebs']['VolumeId']
                    volumes.append(i['Ebs']['VolumeId'])
                vol_session = ec2.describe_volumes(Filters=[{'Name':'volume-id','Values':volumes}])
                for data in vol_session['Volumes']:
                    print ("\t Volume ID : ", data['VolumeId'] , "\tSize : ", data['Size'], "")
                print ("\t Root Device : ", root_device , "\tID : ",root_id)
                print ("-------------------------------- *************** ---------------------------------------------")
                #print ("Volumes : ", volumes)


ec2_id()
