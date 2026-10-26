import json, pathlib, shutil, csv
root=pathlib.Path(__file__).resolve().parent.parent
latest=json.loads((root/'data/dashboard.json').read_text())
assert len({c['id'] for c in latest['contacts']})==len(latest['contacts'])
r=latest['report']; assert all(isinstance(r[k],(int,float)) and r[k]>=0 for k in ['sent','replies','deals','received'])
path=root/'data/reports'/f"{r['date']}.json"
path.write_text(json.dumps(latest,ensure_ascii=False,indent=2))
dates=sorted([p.stem for p in path.parent.glob('????-??-??.json')],reverse=True)
(path.parent/'index.json').write_text(json.dumps({'dates':dates},ensure_ascii=False))
with (root/'contacts.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(latest['contacts'][0]),delimiter=';',extrasaction='ignore');w.writeheader();w.writerows(latest['contacts'])
out=root/'docs';shutil.rmtree(out,ignore_errors=True);out.mkdir()
for name in ['index.html','style.css','app.js','execution.js','plan.js','channels.js','studio.js','contacts.csv']:
 shutil.copy(root/name,out/name)
shutil.copytree(root/'assets',out/'assets');shutil.copytree(root/'data',out/'data');(out/'.nojekyll').touch()
print('Built static dashboard; reports:',len(dates),'contacts:',len(latest['contacts']))

# Version assets so browsers receive the same code as the published page.
import hashlib
html=(out/'index.html').read_text()
for asset in ['style.css','app.js','execution.js','plan.js','channels.js','studio.js']:
 version=hashlib.sha256((out/asset).read_bytes()).hexdigest()[:10]
 html=html.replace('"'+asset+'"','"'+asset+'?v='+version+'"')
(out/'index.html').write_text(html)
