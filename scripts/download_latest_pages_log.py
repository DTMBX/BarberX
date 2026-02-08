import json, subprocess, os, sys
p='.github/actions-logs/latest_pages_runs.json'
if not os.path.exists(p):
    print('file not found:', p)
    sys.exit(1)
with open(p,'r',encoding='utf-8') as f:
    runs = json.load(f)
if not runs:
    print('no runs in file')
    sys.exit(2)
first = runs[0]
runid = first.get('databaseId')
if not runid:
    print('no databaseId in first run')
    sys.exit(3)
outdir = '.github/actions-logs'
os.makedirs(outdir, exist_ok=True)
outfile = os.path.join(outdir, f'run-{runid}-log.txt')
print('Downloading run', runid, 'to', outfile)
try:
    r = subprocess.run(['gh','run','view',str(runid),'--log'], stdout=open(outfile,'wb'), stderr=subprocess.STDOUT, check=False)
except Exception as e:
    print('gh run view failed:', e)
    sys.exit(4)
# print first 200 lines
with open(outfile,'r',encoding='utf-8',errors='replace') as f:
    for i, line in enumerate(f):
        if i>=200:
            break
        print(line.rstrip())
print('\nSaved full log to', outfile)
