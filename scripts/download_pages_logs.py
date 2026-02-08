#!/usr/bin/env python3
import json, subprocess, os

src='site/.github/actions-logs/pages_runs.json'
if not os.path.exists(src):
    src='.github/actions-logs/pages_runs.json'
if not os.path.exists(src):
    print('pages_runs.json not found at site or root')
    raise SystemExit(1)
with open(src,'r',encoding='utf-8') as f:
    runs=json.load(f)
failed=[r for r in runs if r.get('conclusion')!='success']
outdir='.github/actions-logs'
os.makedirs(outdir,exist_ok=True)
for r in failed[:10]:
    rid=str(r.get('databaseId'))
    d=os.path.join(outdir,'run-'+rid)
    os.makedirs(d,exist_ok=True)
    logfile=os.path.join(d,'run-'+rid+'-log.txt')
    print('Downloading',rid,'->',logfile)
    try:
        with open(logfile,'wb') as lf:
            subprocess.run(['gh','run','view',rid,'--log'],stdout=lf,stderr=subprocess.STDOUT,check=False)
    except Exception as e:
        print('failed',e)
print('Done')
