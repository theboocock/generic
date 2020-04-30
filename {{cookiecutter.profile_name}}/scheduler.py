#!/usr/bin/env python3


import sys, os
from subprocess import Popen, PIPE
import yaml

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# let snakemake read job_properties
from snakemake.utils import read_job_properties


jobscript = sys.argv[1]
job_properties = read_job_properties(jobscript)

#default paramters defined in cluster_spec (accessed via snakemake read_job_properties)
cluster_param= job_properties["cluster"]

if job_properties["type"]=='single':
    cluster_param['name'] = job_properties['rule']
elif job_properties["type"]=='group':
    cluster_param['name'] = job_properties['groupid']
else:
    raise NotImplementedError(f"Don't know what to do with job_properties['type']=={job_properties['type']}")


# don't overwrite default parameters if defined in rule (or config file)
cluster_param["threads"] = job_properties["threads"]
for res in ['time','mem']:
    if (res in job_properties["resources"]) and (res not in cluster_param):
        cluster_param[res] = job_properties["resources"][res]

# time in hours
if "time" in cluster_param:
    cluster_param["time"]=int(cluster_param["time"]*60)

# check which system you are on and load command command_options
key_mapping_file=os.path.join(os.path.dirname(__file__),"key_mapping.yaml")
command_options=yaml.load(open(key_mapping_file),
                          Loader=yaml.BaseLoader)
command= command_options[command_options['system']]['command']

key_mapping= command_options[command_options['system']]['key_mapping']

# construct command:


for  key in key_mapping:
    if key in cluster_param:
        if key == "highp":
            if "highp" == cluster_param[key]:
                command+=" "
                command+=key_mapping[key].format(cluster_param[key])
        else: 
            command+=" "
            command+=key_mapping[key].format(cluster_param[key])

command+=' {}'.format(jobscript)
eprint("submit command: "+command)
p = Popen(command.split(' '), stdout=PIPE, stderr=PIPE)
output, error = p.communicate()
if p.returncode != 0:
    raise Exception("Job can't be submitted\n"+output.decode("utf-8")+error.decode("utf-8"))
else:
    res= output.decode("utf-8")
    jobid= int(res.strip().split()[2])
    print(jobid)
