
from __future__ import print_function
import os
import re
import sys


class CPVM:
    vmName=""
    clientID=""
    masterMoid=""
    snapID=""
    vcUuid=""


templateList = []
replicaList = []
parentList = []
vmList = []

hasIOErrored = 0
# Walk the datastores and build a list of all templates, replicas, and parents

count = 0
walkResult = os.walk("/vmfs/volumes")
for root, dirs, files in walkResult:
    
    vmxFiles = [x for x in files if x.endswith(".vmx")]
    for file in vmxFiles:
            try:
                # Found a VMX file, pull information
                count = count + 1
                vmx = open(os.path.join(root, file)).read()
                temp = CPVM()
                temp.vmName = file.strip('.vmx')
                cid = re.search('cloneprep\.client\.uuid = "([0-9a-fA-F-]+)"', vmx)
                if cid is not None:
                    temp.clientID = cid.group(1)
                mid = re.search('master\.uuid%3D([0-9a-fA-F-]+)', vmx)
                if mid is not None:
                    temp.masterMoid = mid.group(1)
                ssid = re.search('ss.id%3D([0-9]+)', vmx)
                if ssid is not None:
                    temp.snapID = ssid.group(1)
                uuid = re.search('vc\.uuid = "([0-9a-fA-F -]+)"', vmx)
                if uuid is not None:
                    temp.vcUuid = uuid.group(1)
                
                if file.startswith("cp-template"):
                    # Found a template!               
                    templateList.append(temp)
                elif file.startswith("cp-replica"):
                    # Found a replica!
                    replicaList.append(temp)
                elif file.startswith("cp-parent"):
                    # Found a parent!
                    parentList.append(temp)
                else:
                    vmList.append(temp)
            except IOError as err:
                if hasIOErrored == 0:
                    print('')
                    print("Warning: Some VMX files are inaccessable either due to file locks or insufficient permissions. Output may not be complete")
                    hasIOErrored = 1
            print('.',end='')
            sys.stdout.flush()


# Output list of templates with related replicas and parents

for temp in templateList:
    print('Template: ' + temp.vmName)
    master = next((x for x in vmList if temp.masterMoid.replace('-','') == x.vcUuid.replace(' ','').replace('-','')),None)
    print('Master VM: ' + master.vmName)
    print('Snapshot ID: ' + temp.snapID)
    print('     Replicas:')
    for rep in [x for x in replicaList if (x.masterMoid == temp.masterMoid) & (x.snapID == temp.snapID)]:
        print('       ' + rep.vmName)
    print('     Parents:')
    for pnt in [x for x in parentList if (x.masterMoid == temp.masterMoid) & (x.snapID == temp.snapID)]:
        print('       ' + pnt.vmName)
