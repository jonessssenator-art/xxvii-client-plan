"""Check public portfolio/source availability; never invent commercial activity."""
import json,pathlib,datetime,urllib.request,urllib.error
root=pathlib.Path(__file__).resolve().parent.parent
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
data=json.loads((root/'data/dashboard.json').read_text())
checks=[]
for item in data['report']['cases']+data['report']['sources']:
 url=item['url']
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'XXVII-Dashboard-LinkCheck/1.0'})
  with urllib.request.urlopen(req,timeout=20) as response:
   status=response.status;response.read(1024)
  result=f'HTTP {status}. Доступность проверена; актуальность предложения не установлена.'
 except urllib.error.HTTPError as e: result=f'HTTP {e.code}. Возможны ограничения доступа; не считать компанию закрытой.'
 except Exception: result='Не удалось получить ответ. Требуется повторная проверка.'
 checks.append({'name':item['name'],'url':url,'result':result})
report={'date':now.date().isoformat(),'checkedAt':now.isoformat(),'kind':'availability-check','summary':f'Проверена доступность {len(checks)} ссылок портфолио и источников. Переписка и оплаты не подключены; показатели продаж не изменены.','checks':checks}
folder=root/'data/daily';folder.mkdir(exist_ok=True)
text=json.dumps(report,ensure_ascii=False,indent=2)
(folder/f"{report['date']}.json").write_text(text);(folder/'latest.json').write_text(text)
print(report['summary'])
