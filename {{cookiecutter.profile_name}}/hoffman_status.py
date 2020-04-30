#!/usr/bin/env python3

import sys
import subprocess
import xml.etree.cElementTree as ET

jobid = sys.argv[1]

try:
    res = subprocess.run("qstat -f -j {}".format(jobid), check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for line in res.stdout.decode().split("\n"):
        print(line)
    print("running")
except KeyboardInterrupt:
    print("failed")
except (subprocess.CalledProcessError) as e:
    # if not running, use qacct to check for exit status
    try:
        p = subprocess.Popen(['qacct', '-j', jobid], stdout=subprocess.PIPE)
        output, err = p.communicate()
        for x in output.decode().split('\n'):
            y = x.split()
            if y[0] == 'exit_status':
                if y[1] == '0':
                    print("success")
                else:
                    print("failed")
                break
    except (subprocess.CalledProcessError, IndexError, KeyboardInterrupt) as e:
        print("failed")
