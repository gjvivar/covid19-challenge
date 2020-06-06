import sys
import boto3
import os
import tempfile
import json
import subprocess

from time import sleep


s3 = boto3.client('s3')

config = sys.argv[1]
config_epoch = sys.argv[2]
data = sys.argv[3]
results = sys.argv[4]

config_path = os.path.join(results, 'config.json')

os.makedirs(results)

config = json.loads(config)

dirpath = tempfile.mkdtemp()

config_path = os.path.join(dirpath, 'config.json')

with open(config_path, 'w') as f:
    json.dump(config, f)

eisen_cmd = ['python3',
             '/opt/conda/bin/eisen',
             'train',
             config_path,
             str(config_epoch),
             '--data_dir={}'.format(data),
             '--artifact_dir={}'.format(results)
             ]

print('I am about to run Eisen via: {}'.format(eisen_cmd))


training = subprocess.call(eisen_cmd)

exit(training)