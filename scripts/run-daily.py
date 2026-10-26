#!/usr/bin/env python3
import datetime,fcntl,json,os,pathlib,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parent.parent
RUNTIME=pathlib.Path.home()/'.local/state/xxvii-reports';RUNTIME.mkdir(parents=True,exist_ok=True)
CODEX='/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex'
os.environ['PATH']='/Users/27/.local/node/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
os.chdir(ROOT)
lock=(RUNTIME/'run.lock').open('w')
try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:sys.exit(0)
now=lambda:datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
def run(args,**kwargs):return subprocess.run(args,check=True,text=True,**kwargs)
def publish():
 run(['/usr/bin/python3','scripts/build.py'])
 run(['git','add','data','docs','contacts.csv'])
 if subprocess.run(['git','diff','--cached','--quiet']).returncode:
  run(['git','-c','user.name=XXVII Reports','-c','user.email=reports@users.noreply.github.com','commit','-m','Daily XXVII report '+now().date().isoformat()])
  run(['git','push','origin','main'])
# Verification uses the same auth and workspace as a scheduled invocation without changing sales data.
if '--verify' in sys.argv:
 run(['gh','api','repos/jonessssenator-art/xxvii-client-plan','--jq','.permissions.push'])
 run([CODEX,'-a','never','exec','--sandbox','workspace-write','-c','sandbox_workspace_write.network_access=true','--ephemeral','-C',str(ROOT),'--color','never','Ответь только OK. Не вызывай инструменты, не меняй файлы, не запускай субагентов.'],stdout=(RUNTIME/'verify.log').open('w'),stderr=subprocess.STDOUT,timeout=180)
 print('GitHub access and Codex invocation verified');sys.exit(0)
if run(['git','status','--porcelain'],capture_output=True).stdout.strip():raise RuntimeError('Checkout has uncommitted changes; refusing to overwrite')
run(['git','pull','--ff-only','origin','main'])
before=json.loads((ROOT/'data/dashboard.json').read_text())
status={'scheduledTime':'19:00 Europe/Moscow','runner':'Mac владельца; требуется интернет и вход в учетную запись','startedAt':now().isoformat(),'status':'running'}
try:
 if '--publish-check' not in sys.argv:
  prompt='Выполни сегодняшнюю ежедневную работу по DAILY_REPORT.md. Прочитай data/dashboard.json и обнови только этот файл. Не публикуй сам: проверку и git push сделает скрипт. Не запускай субагентов. Не меняй показатели отправок, ответов, сделок или денег: новой информации от владельца нет. Найди и проверь до 5 реальных свежих запросов или контактов, подготовь до 3 текстов. Сохрани полный формат JSON. Обязательно обнови progress.checks и progress.notes: проставь галочки фактически выполненных задач и итоги по дням. Не выдумывай новые результаты. Дата отчета '+now().date().isoformat()+'.'
  with (RUNTIME/(now().date().isoformat()+'.log')).open('a') as log:
   run([CODEX,'-a','never','exec','--sandbox','workspace-write','-c','sandbox_workspace_write.network_access=true','-c','web_search="live"','--ephemeral','-C',str(ROOT),'--color','never',prompt],stdout=log,stderr=subprocess.STDOUT,timeout=1800)
  after=json.loads((ROOT/'data/dashboard.json').read_text())
  if not isinstance(after.get('progress',{}).get('checks'),dict) or not isinstance(after.get('progress',{}).get('notes'),dict):raise ValueError('Missing checklist progress')
  if after['report']['date']!=now().date().isoformat():raise ValueError('Agent did not write today report')
  for k in ['sent','replies','deals','received']:
   if after['report'][k]!=before['report'][k]:raise ValueError('Commercial totals changed without evidence')
  if not {c['id'] for c in before['contacts']}.issubset({c['id'] for c in after['contacts']}):raise ValueError('Existing contacts removed')
  changed=run(['git','diff','--name-only'],capture_output=True).stdout.splitlines()
  if any(p!='data/dashboard.json' for p in changed):raise ValueError('Agent changed unexpected files; manual review required')
  status['status']='report-prepared'
 else:status['status']='publication-verified';status['note']='Тест публикации и проверки ссылок; новый поиск клиентов не выполнялся.'
 run(['/usr/bin/python3','scripts/daily.py'],timeout=360)
 status['finishedAt']=now().isoformat()
 (ROOT/'data/automation.json').write_text(json.dumps(status,ensure_ascii=False,indent=2))
 publish()
 # Never claim a generated report is published merely because push succeeded.
 import urllib.request
 expected=json.loads((ROOT/'data/dashboard.json').read_text())
 for attempt in range(20):
  try:
   url='https://jonessssenator-art.github.io/xxvii-client-plan/data/automation.json?t='+str(int(time.time()))
   live=json.load(urllib.request.urlopen(url,timeout=20))
   if live.get('finishedAt')==status['finishedAt']:break
  except Exception:pass
  time.sleep(15)
 else:raise RuntimeError('Push succeeded but Pages publication not confirmed')
 print('Pages report publication verified')
except Exception as exc:
 (RUNTIME/'last-error.txt').write_text(now().isoformat()+' '+str(exc))
 print('Daily run failed: '+str(exc),file=sys.stderr)
 # Do not auto-publish possibly invalid agent output.
 sys.exit(1)
