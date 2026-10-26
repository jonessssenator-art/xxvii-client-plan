from pathlib import Path
p=Path('execution.js');s=p.read_text().replace("fetch('/api/dashboard'","fetch('data/dashboard.json'").replace('href="/api/dashboard"','href="data/dashboard.json"').replace('href="/contacts.csv"','href="contacts.csv"').replace('<a class="btn" href="/api/reports" target="_blank">Архив отчетов ↗</a>','<div id="report-archive"></div>');s=s.replace("if(tab!=='report')return;v.innerHTML=", "if(tab!=='report')return;v.innerHTML=")
s=s.replace("}catch(e){v.textContent=e.message}}\nasync function renderContacts", ";await renderArchive(v)}catch(e){v.textContent=e.message}}\nasync function renderContacts",1)
s=s.replace('${esc(r.summary)}</p>','${esc(r.summary)}</p><div id="daily-checks"></div>',1)
s += '''
async function renderArchive(v){
 try{const response=await fetch('data/reports/index.json',{cache:'no-store'});if(!response.ok)throw Error('Архив недоступен');const archive=await response.json();const target=v.querySelector('#report-archive');if(!target)return;
 target.innerHTML='<label for="report-date">Отчет за дату</label><select id="report-date"><option value="">Последний отчет</option>'+archive.dates.map(d=>'<option value="'+esc(d)+'">'+esc(d)+'</option>').join('')+'</select><p id="archive-status" role="status"></p>';
 target.querySelector('select').value=window.selectedReportDate||'';
 target.querySelector('select').addEventListener('change',async e=>{try{const date=e.target.value;if(date&&!/^\\d{4}-\\d{2}-\\d{2}$/.test(date))return;const r=await fetch(date?'data/reports/'+date+'.json':'data/dashboard.json',{cache:'no-store'});if(!r.ok)throw Error('Не удалось загрузить отчет');shared=await r.json();window.selectedReportDate=date;await renderReport(v);v.scrollIntoView({block:'start'})}catch(error){target.querySelector('#archive-status').textContent=error.message}});
 const daily=await fetch('data/daily/latest.json',{cache:'no-store'}).then(r=>r.ok?r.json():null);const box=v.querySelector('#daily-checks');
 if(daily&&box)box.innerHTML='<div class="guidance"><h3>Ежедневная проверка · '+esc(daily.date)+'</h3><p>'+esc(daily.summary)+'</p><p>Последний содержательный отчет: '+esc(shared.report.date)+'. Автоматическая проверка ссылок не означает новые переговоры или продажи.</p><details><summary>Что проверено</summary>'+daily.checks.map(c=>'<p><a target="_blank" rel="noopener" href="'+href(c.url)+'">'+esc(c.name)+'</a> · '+esc(c.result)+'</p>').join('')+'</details><p><a href="data/daily/'+esc(daily.date)+'.json">Скачать проверку</a> · <a href="https://github.com/jonessssenator-art/xxvii-client-plan/actions">История запусков ↗</a></p></div>';
 }catch(error){const t=v.querySelector('#report-archive');if(t)t.textContent=error.message}
}
'''
p.write_text(s)
p=Path('index.html');s=p.read_text().replace('Отчеты сохраняются на сервере.','Отчеты и архив публикуются на GitHub Pages.');p.write_text(s)
