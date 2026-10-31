(function(){
'use strict';
var D=window.__DATA__;
var $=function(s,r){return (r||document).querySelector(s)};
var $$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
function h(tag,attrs){
  var e=document.createElement(tag);
  if(attrs){Object.keys(attrs).forEach(function(k){
    var v=attrs[k];
    if(v==null||v===false)return;
    if(k==='class')e.className=v;
    else if(k==='html')e.innerHTML=v;
    else if(k.slice(0,2)==='on')e.addEventListener(k.slice(2),v);
    else e.setAttribute(k,v);
  });}
  for(var i=2;i<arguments.length;i++){add(e,arguments[i]);}
  return e;
}
function add(e,c){
  if(c==null||c===false)return;
  if(Array.isArray(c)){c.forEach(function(x){add(e,x)});return;}
  e.appendChild(c.nodeType?c:document.createTextNode(String(c)));
}
var NS='http://www.w3.org/2000/svg';
function sv(tag,attrs){
  var e=document.createElementNS(NS,tag);
  if(attrs){Object.keys(attrs).forEach(function(k){if(attrs[k]!=null)e.setAttribute(k,attrs[k]);});}
  for(var i=2;i<arguments.length;i++){add(e,arguments[i]);}
  return e;
}
function nf(n,d){d=d||0;return n.toLocaleString('ru-RU',{minimumFractionDigits:d,maximumFractionDigits:d});}
var FACT={};D.facts.forEach(function(f){FACT[f.id]=f;});
var GL={};D.glossary.forEach(function(g){GL[g.key]=g;});
function chip(id){
  var f=FACT[id];
  return h('span',{class:'fact lvl-'+(f?f.level:'secondary'),'data-f':id,tabindex:'0',role:'button','aria-label':'Источник '+id},id);
}
function chips(ids){return (ids||[]).map(function(i){return [' ',chip(i)];});}
var LV={primary:'первичный документ',secondary:'пересказ СМИ / вторичный',estimate:'расчёт редакции'};

/* ---------- popovers ---------- */
var pop=h('div',{id:'pop',role:'dialog'});var tip=h('div',{id:'tip',role:'tooltip'});
document.body.appendChild(pop);document.body.appendChild(tip);
function place(box,el){
  var r=el.getBoundingClientRect();box.style.display='block';
  var w=box.offsetWidth,x=r.left+window.scrollX,y=r.bottom+window.scrollY+8;
  var max=window.scrollX+document.documentElement.clientWidth-w-10;
  box.style.left=Math.max(8,Math.min(x,max))+'px';box.style.top=y+'px';
}
function showFact(el){
  var id=el.getAttribute('data-f'),f=FACT[id];if(!f)return;
  pop.innerHTML='';
  pop.appendChild(h('div',{class:'h'},h('span',null,id+' · '+f.year),h('span',{class:'lv '+f.level},LV[f.level]||f.level)));
  pop.appendChild(h('div',null,f.text));
  pop.appendChild(h('div',{class:'src'},'Источник: '+f.source));
  pop._for=el;place(pop,el);
}
document.addEventListener('click',function(e){
  var t=e.target.closest&&e.target.closest('.fact');
  if(t){if(pop.style.display==='block'&&pop._for===t){pop.style.display='none';}else{showFact(t);}e.stopPropagation();return;}
  var tm=e.target.closest&&e.target.closest('.term');
  if(tm){showTerm(tm);return;}
  if(!e.target.closest('#pop'))pop.style.display='none';
  tip.style.display='none';
});
document.addEventListener('keydown',function(e){
  if(e.key==='Escape'){pop.style.display='none';tip.style.display='none';}
  if((e.key==='Enter'||e.key===' ')&&e.target.classList&&e.target.classList.contains('fact')){e.preventDefault();e.target.click();}
});
function showTerm(el){
  var g=GL[el.getAttribute('data-t')];if(!g)return;
  tip.innerHTML='';tip.appendChild(h('b',null,g.term));tip.appendChild(h('div',null,g.text));place(tip,el);
}
document.addEventListener('mouseover',function(e){var t=e.target.closest&&e.target.closest('.term');if(t)showTerm(t);});
document.addEventListener('mouseout',function(e){var t=e.target.closest&&e.target.closest('.term');if(t)tip.style.display='none';});

/* ---------- widget shell ---------- */
function shell(root,title,sub){
  root.innerHTML='';root.appendChild(h('div',{class:'wt'},title));
  if(sub)root.appendChild(h('div',{class:'ws'},sub));
}
function chipRow(items,onpick,start){
  var row=h('div',{class:'row',role:'group'});var btns=[];
  items.forEach(function(it,i){
    var b=h('button',{class:'chip',type:'button','aria-pressed':String(i===start)},it.label);
    b.addEventListener('click',function(){btns.forEach(function(x){x.setAttribute('aria-pressed','false')});b.setAttribute('aria-pressed','true');onpick(it,i);});
    btns.push(b);row.appendChild(b);
  });
  return row;
}
var W={};

/* ---------- forms ---------- */
W.forms=function(root){
  shell(root,'Три формы тенге','Выберите свойство, и оно подсветится в каждой карточке.');
  var rows=D.forms.rows;
  var cards=D.forms.cards;
  var cur='obl';var grid=h('div',{class:'grid3'});
  function draw(){
    grid.innerHTML='';
    cards.forEach(function(c){
      var card=h('div',{class:'card'+(c.f?' hl':'')},h('h4',null,c.n,c.f?chips(c.f):null));
      rows.forEach(function(r){card.appendChild(h('div',{class:'kv'+(r[0]===cur?' on':'')},h('span',null,r[1]),h('span',null,c[r[0]])));});
      grid.appendChild(card);
    });
  }
  root.appendChild(chipRow(rows.map(function(r){return {label:r[1],k:r[0]};}),function(it){cur=it.k;draw();},0));
  root.appendChild(grid);draw();
};

/* ---------- timeline ---------- */
W.timeline=function(root){
  shell(root,'Хронология проекта, 2020–2026','Нажмите на событие, чтобы развернуть. Фильтры показывают отдельные линии истории.');
  var types=[{label:'Всё',t:null},{label:'Решения',t:'decision'},{label:'Пилоты',t:'pilot'},{label:'Закон и правила',t:'law'},{label:'Мир и сотрудничество',t:'world'}];
  var list=h('div',{class:'tl'});
  function draw(t){
    list.innerHTML='';var last='';
    D.timeline.filter(function(e){return !t||e.type===t;}).forEach(function(e){
      var y=e.date.slice(0,4);
      if(y!==last){list.appendChild(h('div',{class:'yr'},y));last=y;}
      var btn=h('button',{type:'button','aria-expanded':'false'},h('div',{class:'d'},e.date.slice(5)+'.'+y),h('div',{class:'t'},e.title));
      var ev=h('div',{class:'ev '+e.type},btn,h('div',{class:'x'},e.text,chips(e.facts)));
      btn.addEventListener('click',function(){var o=ev.classList.toggle('open');btn.setAttribute('aria-expanded',String(o));});
      list.appendChild(ev);
    });
  }
  root.appendChild(chipRow(types,function(it){draw(it.t);},0));
  root.appendChild(h('div',{class:'legend'},
    h('span',null,h('i',{class:'dot',style:'background:var(--tm-accent)'}),'решения'),h('span',null,h('i',{class:'dot',style:'background:#3a7bd5'}),'пилоты'),
    h('span',null,h('i',{class:'dot',style:'background:var(--tm-warm)'}),'закон'),h('span',null,h('i',{class:'dot',style:'background:#8e6bbf'}),'мир')));
  root.appendChild(list);draw(null);
};

/* ---------- lifecycle ---------- */
W.lifecycle=function(root){
  shell(root,'Путь цифрового тенге: от выпуска до погашения','Листайте шаги: токен переходит от узла к узлу.');
  var nodes=['Нацбанк','Банк','Клиент','Продавец','Банк продавца'];
  var steps=D.lifecycle;
  var i=0,wd=640,xs=nodes.map(function(_,k){return 20+k*122;});
  var svg=sv('svg',{viewBox:'0 0 640 150',width:'100%',role:'img','aria-label':'Схема пути токена'});
  var boxes=nodes.map(function(n,k){
    var g=sv('g',null,sv('rect',{x:xs[k],y:40,width:100,height:56,rx:10,fill:'var(--tm-accent-soft)',stroke:'var(--tm-accent)','stroke-width':1.5}),
      (function(){var parts=n.split(' ');var tx=sv('text',{x:xs[k]+50,y:parts.length>1?66:73,'text-anchor':'middle','font-size':13,'font-weight':700,fill:'var(--tm-fg)'});
        parts.forEach(function(w,j){tx.appendChild(sv('tspan',{x:xs[k]+50,dy:j?15:0},w));});return tx;})());
    svg.appendChild(g);return g;
  });
  nodes.forEach(function(_,k){if(k<4)svg.appendChild(sv('path',{d:'M'+(xs[k]+102)+' 68 L'+(xs[k+1]-4)+' 68',stroke:'var(--tm-muted)','stroke-width':2,'marker-end':'url(#ar)'}));});
  var defs=sv('defs',null,sv('marker',{id:'ar',markerWidth:8,markerHeight:8,refX:6,refY:3,orient:'auto'},sv('path',{d:'M0 0 L6 3 L0 6 z',fill:'var(--tm-muted)'})));
  svg.insertBefore(defs,svg.firstChild);
  var tok=sv('g',{class:'tok'},sv('circle',{r:11,fill:'var(--tm-warm)'}),sv('text',{'text-anchor':'middle',y:4,'font-size':12,'font-weight':700,fill:'#fff'},'₸'));
  svg.appendChild(tok);
  var oracle=sv('g',null,sv('rect',{x:215,y:112,width:210,height:26,rx:8,fill:'none',stroke:'var(--tm-gray)','stroke-dasharray':'4 3'}),sv('text',{x:320,y:129,'text-anchor':'middle','font-size':11,fill:'var(--tm-muted)'},'нотариальная нода · оракул'));
  svg.appendChild(oracle);
  var body=h('div',{class:'out'});var ctr=h('div',{class:'row'});
  var prev=h('button',{class:'chip',type:'button'},'← назад'),next=h('button',{class:'chip',type:'button'},'дальше →');
  ctr.appendChild(prev);ctr.appendChild(next);
  function draw(){
    var s=steps[i];boxes.forEach(function(g,k){g.firstChild.setAttribute('fill',(k===s.a||k===s.b)?'var(--tm-accent)':'var(--tm-accent-soft)');g.lastChild.setAttribute('fill',(k===s.a||k===s.b)?'#fff':'var(--tm-fg)');});
    tok.setAttribute('transform','translate('+(xs[s.b]+50)+',22)');
    body.innerHTML='';body.appendChild(h('b',null,s.t+'. '));body.appendChild(document.createTextNode(s.x));add(body,chips(s.f));
    prev.disabled=i===0;next.disabled=i===steps.length-1;
  }
  prev.addEventListener('click',function(){i=Math.max(0,i-1);draw();});next.addEventListener('click',function(){i=Math.min(steps.length-1,i+1);draw();});
  root.appendChild(svg);root.appendChild(ctr);root.appendChild(body);draw();
};

/* ---------- marking demo ---------- */
W.marking=function(root){
  shell(root,'Попробуйте заплатить маркированными деньгами','Государство перевело 10 млн условных единиц генподрядчику строительства дороги. Задайте глубину маркировки и выберите, кому он попробует заплатить.');
  var depth=2;
  var targets=[
    {n:'Своему субподрядчику',lvl:1,x:'разрешено первым звеном цепочки'},
    {n:'Поставщику субподрядчика',lvl:2,x:'зависит от глубины маркировки'},
    {n:'Поставщику поставщика',lvl:3,x:'зависит от глубины маркировки'},
    {n:'Посторонней компании',lvl:99,x:'не входит в цепочку'},
    {n:'Вывести деньги из системы',lvl:100,x:'выход за пределы параметров'}
  ];
  var out=h('div',{class:'out'});
  var sel=h('div',{class:'sel'});
  function judge(t){
    var ok=t.lvl<=depth,why;
    if(t.lvl===99)why='Получатель не указан в параметрах маркировки, поэтому платёж невозможен: деньги останутся на счёте.';
    else if(t.lvl===100)why='Выход из системы ограничен параметрами маркировки (сумма и срок), поэтому свободно вывести такие деньги нельзя.';
    else if(ok)why='Платёж пройдёт: получатель находится в пределах заданной глубины ('+depth+').';
    else why='Платёж не пройдёт: получатель находится на уровне '+t.lvl+', а маркировка настроена на глубину '+depth+'.';
    out.className='out'+(ok?'':' bad');out.innerHTML='';out.appendChild(h('b',null,(ok?'Разрешено. ':'Заблокировано. ')));out.appendChild(document.createTextNode(why));
    out.appendChild(h('div',{style:'margin-top:6px;font-size:13px;color:var(--tm-muted)'},'Практически надёжно отследить удаётся 2–3 звена цепочки.',chips(['Ф-009','Ф-023'])));
  }
  targets.forEach(function(t){sel.appendChild(h('button',{class:'chip',type:'button',onclick:function(){judge(t);}},t.n));});
  root.appendChild(h('div',{class:'row'},h('span',null,'Глубина маркировки:'),chipRow([{label:'1 звено',d:1},{label:'2 звена',d:2},{label:'3 звена',d:3}],function(it){depth=it.d;out.textContent='Глубина изменена. Выберите получателя.';out.className='out';},1)));
  root.appendChild(sel);root.appendChild(out);out.textContent='Выберите получателя.';
};

/* ---------- VAT demo ---------- */
W.vat=function(root){
  shell(root,'Цифровой НДС: куда идёт налог','Условный пример. Ставка НДС здесь произвольная: меняйте её и суммы, как хотите.');
  var cost=h('input',{type:'number',value:'1000',min:'0',step:'100','aria-label':'Закупка'}),price=h('input',{type:'number',value:'1500',min:'0',step:'100','aria-label':'Продажа'}),rate=h('input',{type:'range',min:'0',max:'20',value:'12','aria-label':'Ставка'});
  var rl=h('b',null,'12%');var out=h('div');var bar=h('div');
  function draw(){
    var c=+cost.value||0,p=+price.value||0,r=(+rate.value)/100;rl.textContent=Math.round(r*100)+'%';
    var vin=c*r,vout=p*r,net=vout-vin;
    out.innerHTML='';
    var t=h('table',null,
      h('tr',null,h('th',null,'Шаг'),h('th',null,'Обычные токены'),h('th',null,'Токены НДС')),
      h('tr',null,h('td',null,'Покупатель платит вам'),h('td',null,nf(p,0)),h('td',null,nf(vout,0))),
      h('tr',null,h('td',null,'Вы платите своему поставщику'),h('td',null,nf(c,0)),h('td',null,nf(vin,0))),
      h('tr',null,h('td',null,net>=0?'Вы отправляете в бюджет':'Налог к возврату вам'),h('td',null,'—'),h('td',null,nf(Math.abs(net),0))));
    out.appendChild(t);
    out.appendChild(h('div',{class:'out'},net>=0?'Налоговые токены нельзя потратить на другое: они либо идут следующему звену цепочки в зачёт, либо в бюджет. Потерять налог «по дороге» нельзя.':'Входного налога больше, чем исходящего: в обычной схеме это основание для возврата, а в цифровой видно, что платёжные токены уже на месте.',chips(['Ф-010'])));
  }
  [cost,price,rate].forEach(function(e){e.addEventListener('input',draw);});
  root.appendChild(h('div',{class:'row'},h('label',null,'Закупка у поставщика (без НДС) ',cost),h('label',null,'Продажа покупателю (без НДС) ',price)));
  root.appendChild(h('div',{class:'row'},h('label',{style:'flex:1'},'Условная ставка: ',rl,rate)));
  root.appendChild(out);draw();
};

/* ---------- issuance chart ---------- */
W.issuance=function(root){
  shell(root,'Сколько цифровых тенге выпущено','Четыре заявленные точки. Что между ними происходило, мы не знаем. Нажмите на точку, чтобы увидеть источник.');
  var pts=[{d:'2025-07-11',v:257.5,l:'11 июля 2025',f:'Ф-096'},{d:'2025-12-31',v:336.6,l:'конец 2025',f:'Ф-102'},{d:'2026-06-15',v:340,l:'середина июня 2026',f:'Ф-088'},{d:'2026-07-24',v:340,l:'24 июля 2026',f:'Ф-089'}];
  var t0=Date.parse('2025-05-01'),t1=Date.parse('2026-09-01'),zero=true,info=h('div',{class:'out'},'Нажмите на точку.');
  var holder=h('div');
  function draw(){
    holder.innerHTML='';var W=640,H=260,L=48,R=16,T=16,B=36;var lo=zero?0:200,hi=zero?400:380;
    var x=function(d){return L+(Date.parse(d)-t0)/(t1-t0)*(W-L-R);},y=function(v){return T+(hi-v)/(hi-lo)*(H-T-B);};
    var svg=sv('svg',{viewBox:'0 0 '+W+' '+H,width:'100%',role:'img','aria-label':'График выпуска'});
    var ticks=zero?[0,100,200,300,400]:[200,240,280,320,360];
    ticks.forEach(function(v){svg.appendChild(sv('line',{x1:L,x2:W-R,y1:y(v),y2:y(v),stroke:'var(--tm-line)'}));svg.appendChild(sv('text',{x:L-6,y:y(v)+4,'text-anchor':'end','font-size':11,fill:'var(--tm-muted)'},String(v)));});
    ['2025-07-01','2025-10-01','2026-01-01','2026-04-01','2026-07-01'].forEach(function(d){svg.appendChild(sv('text',{x:x(d),y:H-12,'text-anchor':'middle','font-size':11,fill:'var(--tm-muted)'},d.slice(5,7)+'.'+d.slice(0,4)));});
    svg.appendChild(sv('polyline',{points:pts.map(function(p){return x(p.d)+','+y(p.v);}).join(' '),fill:'none',stroke:'var(--tm-accent)','stroke-width':2.5,'stroke-dasharray':'6 4'}));
    pts.forEach(function(p){
      var c=sv('circle',{cx:x(p.d),cy:y(p.v),r:8,fill:'var(--tm-accent)',stroke:'var(--tm-card)','stroke-width':2,style:'cursor:pointer',tabindex:'0'});
      var show=function(){info.innerHTML='';info.appendChild(h('b',null,p.l+': '+nf(p.v,1)+' млрд тенге. '));info.appendChild(document.createTextNode('Заявленная точка, не измерение между ними.'));add(info,chips([p.f]));};
      c.addEventListener('click',show);c.addEventListener('keydown',function(e){if(e.key==='Enter')show();});svg.appendChild(c);
      svg.appendChild(sv('text',{x:x(p.d),y:y(p.v)-14,'text-anchor':'middle','font-size':11.5,'font-weight':700,fill:'var(--tm-fg)'},nf(p.v,1)));
    });
    svg.appendChild(sv('text',{x:8,y:12,'font-size':11,fill:'var(--tm-muted)'},'млрд тенге'));
    holder.appendChild(svg);
  }
  root.appendChild(chipRow([{label:'Ось от нуля',z:true},{label:'Приблизить',z:false}],function(it){zero=it.z;draw();},0));
  root.appendChild(holder);root.appendChild(info);draw();
};

/* ---------- scale ---------- */
W.scale=function(root){
  shell(root,'Масштаб: выпуск против безналичного оборота','Сравниваются накопленный выпуск (конец 2025) и годовой оборот безналичных платежей (2024). Это порядок величин, не точная доля.');
  var log=false,holder=h('div'),note=h('div',{class:'out'});
  var data=[{n:'Цифровые тенге (накоплено)',v:336.6,u:'336,6 млрд тенге',c:'var(--tm-accent)',f:'Ф-102'},{n:'Безналичные платежи (за 2024 год)',v:166100,u:'166,1 трлн тенге',c:'var(--tm-gray)',f:'Ф-003'}];
  function draw(){
    holder.innerHTML='';var W=640,H=130,L=210,R=20;var svg=sv('svg',{viewBox:'0 0 '+W+' '+H,width:'100%'});
    var sc=function(v){return log?(Math.log10(v)-2)/(Math.log10(600000)-2)*(W-L-R):v/170000*(W-L-R);};
    data.forEach(function(d,k){
      var y=16+k*52,w=Math.max(3,sc(d.v));
      svg.appendChild(sv('text',{x:L-8,y:y+22,'text-anchor':'end','font-size':12,fill:'var(--tm-fg)'},d.n));
      svg.appendChild(sv('rect',{x:L,y:y,width:w,height:32,rx:5,fill:d.c}));
      svg.appendChild(sv('text',{x:L+w+8,y:y+21,'font-size':12.5,'font-weight':700,fill:'var(--tm-fg)'},d.u));
    });
    holder.appendChild(svg);
    note.innerHTML='';note.appendChild(h('b',null,'Выпуск составляет около 0,2% от годового безналичного оборота'));note.appendChild(document.createTextNode(' (расчёт редакции: 336,6 / 166 100). '+(log?'Логарифмическая шкала сжимает разницу.':'На линейной шкале столбик выпуска почти не виден.')));add(note,chips(['Ф-102','Ф-003']));
  }
  root.appendChild(chipRow([{label:'Линейная шкала',l:false},{label:'Логарифмическая',l:true}],function(it){log=it.l;draw();},0));
  root.appendChild(holder);root.appendChild(note);draw();
};

/* ---------- ladder ---------- */
W.ladder=function(root){
  shell(root,'Лестница норм','Нажмите на ступень.');
  var steps=[
    {t:'Закон № 259-VIII (16.01.2026)',x:'Определил цифровой тенге как цифровую форму национальной валюты и законное платёжное средство; ввёл главу о цифровом тенге в Закон «О платежах и платёжных системах». Нормы вступили в силу 18 июля 2026 года.',f:['Ф-019','Ф-020']},
    {t:'Правила Нацбанка № 42',x:'Порядок выпуска, обращения и погашения. Действуют с 19 июля 2026 года. Не более одного цифрового счёта у пользователя, сберегательный режим не предусмотрен, офлайн-хранение допускается.',f:['Ф-054','Ф-084']},
    {t:'Приказ Минфина № 375 (08.06.2026)',x:'Пилот в бюджетном процессе: платежи свыше 100 млн тенге по перечню статей идут в цифровом тенге.',f:['Ф-085']},
    {t:'Постановление Правительства (23.10.2026)',x:'Перечень расходов бюджета в форме цифрового тенге; вступило в силу 30 октября 2026 года.',f:['Ф-087']},
    {t:'Тарифы НПК (с 06.09.2026)',x:'135 тенге за документ, минимум 20 000 тенге в месяц с участника, госорганам бесплатно.',f:['Ф-078']}
  ];
  steps.forEach(function(s,k){
    var d=h('details',{class:'q'},h('summary',null,(k+1)+'. '+s.t),h('div',{style:'margin-top:6px'},s.x,chips(s.f)));
    if(k===0)d.setAttribute('open','');root.appendChild(d);
  });
};

/* ---------- faq ---------- */
W.faq=function(root){
  root.className=root.className.replace('widget','').trim();
  D.faq.forEach(function(q){root.appendChild(h('details',{class:'q'},h('summary',null,q.q),h('div',{style:'margin-top:6px;font-family:var(--tm-sans);font-size:15px'},q.a,chips(q.facts))));});
};

/* ---------- tariff calculator ---------- */
W.tariff=function(root){
  shell(root,'Калькулятор тарифа платформы','Тариф: 135 тенге за документ, минимум 20 000 тенге в месяц с участника, без НДС. Задайте сумму платежа и число документов.');
  var exp=h('input',{type:'range',min:'3',max:'9.5',step:'0.01',value:'4','aria-label':'Сумма платежа'});var docs=h('input',{type:'number',value:'100',min:'1',step:'10','aria-label':'Документов в месяц'});
  var lab=h('b'),res=h('div',{class:'out'}),chart=h('div');
  function pct(x){var d=x>=1?1:x>=0.01?2:x>=0.0001?4:6;return nf(x,d)+'%';}
  function draw(){
    var amt=Math.pow(10,+exp.value),share=135/amt*100,n=+docs.value||1,bill=Math.max(20000,135*n);
    lab.textContent=nf(Math.round(amt),0)+' тенге';
    res.innerHTML='';res.appendChild(h('div',null,'Тариф за один документ: ',h('b',null,'135 тенге'),' = ',h('b',null,pct(share)),' от суммы платежа.'));
    res.appendChild(h('div',null,'За месяц при '+nf(n,0)+' документах: ',h('b',null,nf(bill,0)+' тенге'),n*135<20000?' (действует минимум; безубыточность около 148 документов в месяц)':'',' ',chips(['Ф-078'])));
    chart.innerHTML='';var W=640,H=250,L=56,R=16,T=14,B=36;
    var x=function(v){return L+(v-3)/(9.5-3)*(W-L-R);},y=function(p){return T+(1.5-Math.log10(p))/(1.5+5.5)*(H-T-B);};
    var svg=sv('svg',{viewBox:'0 0 '+W+' '+H,width:'100%',role:'img','aria-label':'Доля тарифа в сумме платежа'});
    [-5,-4,-3,-2,-1,0,1].forEach(function(e){svg.appendChild(sv('line',{x1:L,x2:W-R,y1:y(Math.pow(10,e)),y2:y(Math.pow(10,e)),stroke:'var(--tm-line)'}));svg.appendChild(sv('text',{x:L-6,y:y(Math.pow(10,e))+4,'text-anchor':'end','font-size':10.5,fill:'var(--tm-muted)'},e>=0?String(Math.pow(10,e)):nf(Math.pow(10,e),-e)));});
    [3,4,5,6,7,8,9].forEach(function(v){svg.appendChild(sv('text',{x:x(v),y:H-16,'text-anchor':'middle','font-size':10.5,fill:'var(--tm-muted)'},({3:'1 тыс.',4:'10 тыс.',5:'100 тыс.',6:'1 млн',7:'10 млн',8:'100 млн',9:'1 млрд'})[v]));});
    var pts=[];for(var v=3;v<=9.5;v+=0.05){pts.push(x(v)+','+y(135/Math.pow(10,v)*100));}
    svg.appendChild(sv('polyline',{points:pts.join(' '),fill:'none',stroke:'var(--tm-accent)','stroke-width':2.5}));
    [[3779,'средний чек пилота 2023'],[1e8,'порог пилота Минфина']].forEach(function(m){var v=Math.log10(m[0]);svg.appendChild(sv('circle',{cx:x(v),cy:y(135/m[0]*100),r:5,fill:'var(--tm-warm)'}));svg.appendChild(sv('text',{x:x(v)+8,y:y(135/m[0]*100)-8,'font-size':11,fill:'var(--tm-fg)'},m[1]));});
    svg.appendChild(sv('circle',{cx:x(+exp.value),cy:y(share),r:7,fill:'none',stroke:'var(--tm-fg)','stroke-width':2.5}));
    svg.appendChild(sv('text',{x:8,y:12,'font-size':11,fill:'var(--tm-muted)'},'тариф, % суммы (лог. шкала)'));
    chart.appendChild(svg);
  }
  exp.addEventListener('input',draw);docs.addEventListener('input',draw);
  root.appendChild(h('div',{class:'row'},h('label',{style:'flex:1'},'Сумма платежа: ',lab,exp)));
  root.appendChild(h('div',{class:'row'},h('label',null,'Документов в месяц ',docs)));
  root.appendChild(res);root.appendChild(chart);draw();
};

/* ---------- countries ---------- */
W.countries=function(root){
  shell(root,'Как поступают другие страны','Фильтры выбирают подход. Данные приведены с атрибуцией: нажмите на значок источника.');
  var tags=['Все','закон прежде','принуждение','процент','осторожность','масштаб'];var grid=h('div',{class:'grid3'});
  function draw(t){
    grid.innerHTML='';
    D.countries.filter(function(c){return t==='Все'||c.tags.indexOf(t)>=0;}).forEach(function(c){
      var card=h('div',{class:'card'+(c.code==='kz'?' hl':'')},h('h4',null,c.name,chips(c.facts)),h('div',{style:'font-size:13.5px;margin-bottom:6px'},c.summary));
      c.stats.forEach(function(s){card.appendChild(h('div',{class:'kv'},h('span',null,s[0]),h('span',null,s[1])));});
      c.tags.forEach(function(g){card.appendChild(h('span',{class:'badge',style:'background:var(--tm-gray);margin:6px 4px 0 0;display:inline-block'},g));});
      grid.appendChild(card);
    });
  }
  root.appendChild(chipRow(tags.map(function(t){return {label:t,t:t};}),function(it){draw(it.t);},0));
  root.appendChild(grid);draw('Все');
};

/* ---------- risks ---------- */
W.risks=function(root){
  shell(root,'Карта рисков','Оценка редакции, не оператора. Нажмите на кружок, чтобы прочитать описание.');
  var out=h('div',{class:'out'},'Выберите риск.');var W=440,H=330,L=92,T=14;var cw=(W-L-10)/3,ch=(H-T-40)/3;
  var svg=sv('svg',{viewBox:'0 0 '+W+' '+H,width:'100%',style:'max-width:520px',role:'img','aria-label':'Матрица рисков'});
  for(var i=0;i<3;i++)for(var j=0;j<3;j++){svg.appendChild(sv('rect',{x:L+i*cw,y:T+(2-j)*ch,width:cw,height:ch,fill:'var(--tm-warm)','fill-opacity':0.05+0.05*(i+j),stroke:'var(--tm-line)'}));}
  ['низкая','средняя','высокая'].forEach(function(t,i){svg.appendChild(sv('text',{x:L+i*cw+cw/2,y:H-22,'text-anchor':'middle','font-size':11,fill:'var(--tm-muted)'},t));});
  ['умеренные','заметные','тяжёлые'].forEach(function(t,j){svg.appendChild(sv('text',{x:L-6,y:T+(2-j)*ch+ch/2+4,'text-anchor':'end','font-size':11,fill:'var(--tm-muted)'},t));});
  svg.appendChild(sv('text',{x:L+cw*1.5,y:H-6,'text-anchor':'middle','font-size':11,fill:'var(--tm-muted)'},'вероятность'));
  var slots={};
  D.risks.forEach(function(r,n){
    var key=r.p+'-'+r.i,k=slots[key]||0;slots[key]=k+1;
    var cx=L+(r.p-1)*cw+cw*0.3+(k%2)*cw*0.4,cy=T+(3-r.i)*ch+ch*0.32+Math.floor(k/2)*ch*0.38;
    var g=sv('g',{style:'cursor:pointer',tabindex:'0'},sv('circle',{cx:cx,cy:cy,r:15,fill:'var(--tm-warm)'}),sv('text',{x:cx,y:cy+4,'text-anchor':'middle','font-size':12,'font-weight':700,fill:'#fff'},String(n+1)));
    var pick=function(){out.innerHTML='';out.appendChild(h('b',null,(n+1)+'. '+r.name+'. '));out.appendChild(document.createTextNode(r.text));add(out,chips(r.facts));};
    g.addEventListener('click',pick);g.addEventListener('keydown',function(e){if(e.key==='Enter')pick();});svg.appendChild(g);
  });
  var list=h('ol',{style:'margin:8px 0 0;padding-left:1.2em;font-size:13.5px'},D.risks.map(function(r){return h('li',null,r.name);}));
  root.appendChild(h('div',{style:'display:flex;flex-wrap:wrap;gap:12px;align-items:flex-start'},svg,list));root.appendChild(out);
};

/* ---------- pace ---------- */
W.pace=function(root){
  shell(root,'Какой темп нужен для цели','Предположение: цель означает накопленный выпуск. Задайте цель, срок и стартовый уровень.');
  var tgt=h('input',{type:'range',min:'500',max:'3000',step:'250',value:'2000','aria-label':'Цель'});var mon=h('input',{type:'range',min:'6',max:'36',step:'1',value:'12','aria-label':'Срок'});var st=h('input',{type:'number',value:'340',min:'0',step:'10','aria-label':'Старт'});
  var tl=h('b'),ml=h('b'),out=h('div',{class:'out'}),chart=h('div');var best=13.95;
  function draw(){
    var T=+tgt.value,M=+mon.value,S=+st.value||0,need=Math.max(0,(T-S)/M),ratio=need/best;
    tl.textContent=nf(T/1000,2)+' трлн тенге';ml.textContent=M+' мес.';
    out.innerHTML='';out.appendChild(h('div',null,'Нужный темп: ',h('b',null,'≈'+nf(need,0)+' млрд в месяц'),'. Лучший известный темп (вторая половина 2025): ',h('b',null,'≈14 млрд'),', то есть цель требует ускорения примерно в ',h('b',null,nf(ratio,1)+' раза'),'.',chips(['Ф-096','Ф-102','Ф-088'])));
    out.appendChild(h('div',{style:'font-size:13px;color:var(--tm-muted);margin-top:4px'},'Если «охват» означает объём платежей, а не накопленный выпуск, арифметика другая: уточнений от оператора нет.'));
    chart.innerHTML='';var Wd=640,Hd=96;var svg=sv('svg',{viewBox:'0 0 '+Wd+' '+Hd,width:'100%'});var mx=Math.max(need,best,1)*1.1;
    [['Лучший известный',best,'var(--tm-accent)'],['Нужно для цели',need,'var(--tm-warm)']].forEach(function(b,k){var y=8+k*44,w=b[1]/mx*(Wd-250);svg.appendChild(sv('text',{x:140,y:y+22,'text-anchor':'end','font-size':12,fill:'var(--tm-fg)'},b[0]));svg.appendChild(sv('rect',{x:150,y:y,width:Math.max(3,w),height:30,rx:5,fill:b[2]}));svg.appendChild(sv('text',{x:158+w,y:y+20,'font-size':12,'font-weight':700,fill:'var(--tm-fg)'},nf(b[1],0)+' млрд/мес'));});
    chart.appendChild(svg);
  }
  [tgt,mon,st].forEach(function(e){e.addEventListener('input',draw);});
  root.appendChild(h('div',{class:'row'},h('label',{style:'flex:1'},'Цель: ',tl,tgt)));root.appendChild(h('div',{class:'row'},h('label',{style:'flex:1'},'Срок: ',ml,mon)));
  root.appendChild(h('div',{class:'row'},h('label',null,'Стартовый уровень, млрд тенге ',st)));root.appendChild(out);root.appendChild(chart);draw();
};

/* ---------- registry ---------- */
W.registry=function(root){
  shell(root,'Реестр фактов этой редакции','Только факты, упомянутые в тексте. Поиск по содержанию и источнику.');
  var q=h('input',{class:'search',type:'search',placeholder:'Поиск: тариф, банк, 2026…','aria-label':'Поиск'});var lv='all';var body=h('tbody');var cnt=h('div',{class:'ws'});
  function draw(){
    body.innerHTML='';var s=q.value.trim().toLowerCase(),n=0;
    D.facts.forEach(function(f){
      if(lv!=='all'&&f.level!==lv)return;
      if(s&&(f.text+' '+f.source+' '+f.id+' '+f.year).toLowerCase().indexOf(s)<0)return;
      n++;body.appendChild(h('tr',{id:'r-'+f.id},h('td',null,f.id),h('td',null,f.text),h('td',null,f.source),h('td',null,f.year),h('td',null,h('span',{class:'badge '+f.level},LV[f.level]))));
    });
    cnt.textContent='Показано фактов: '+n+' из '+D.facts.length;
  }
  q.addEventListener('input',draw);
  root.appendChild(h('div',{class:'row'},q,chipRow([{label:'Все',l:'all'},{label:'Первичные',l:'primary'},{label:'Пересказ СМИ',l:'secondary'}],function(it){lv=it.l;draw();},0)));
  root.appendChild(cnt);
  root.appendChild(h('div',{class:'regwrap'},h('table',null,h('thead',null,h('tr',null,h('th',null,'Код'),h('th',null,'Содержание'),h('th',null,'Источник'),h('th',null,'Год'),h('th',null,'Уровень'))),body)));
  draw();
};

/* ---------- versions ---------- */
W.versions=function(root){
  shell(root,'История версий','Каждая редакция сохраняется. Выберите версию, чтобы увидеть, что в ней изменилось.');
  var sel=h('select',{'aria-label':'Версия'},D.versions.map(function(v){return h('option',{value:v.v},v.v+' · '+v.date+' · '+(v.kind==='public'?'публичная':'аналитическая'));}));
  var out=h('div');
  function draw(){var v=D.versions.filter(function(x){return x.v===sel.value;})[0];out.innerHTML='';out.appendChild(h('div',{class:'out'},h('b',null,'Редакция '+v.v+'. '),v.title));out.appendChild(h('ul',null,v.changes.map(function(c){return h('li',null,c);})));}
  sel.addEventListener('change',draw);root.appendChild(h('div',{class:'row'},sel));root.appendChild(out);draw();
};

/* ---------- glossary ---------- */
W.glossary=function(root){
  shell(root,'Словарь терминов','Поиск по терминам и их происхождению. Подчёркнутые в тексте слова показывают то же самое во всплывающей подсказке.');
  var q=h('input',{class:'search',type:'search',placeholder:'Найти термин…','aria-label':'Поиск по словарю'});var list=h('div');
  function draw(){list.innerHTML='';var s=q.value.trim().toLowerCase();D.glossary.filter(function(g){return !s||(g.term+' '+g.text).toLowerCase().indexOf(s)>=0;}).forEach(function(g){list.appendChild(h('details',{class:'q'},h('summary',null,g.term),h('div',{style:'margin-top:6px'},g.text)));});}
  q.addEventListener('input',draw);root.appendChild(h('div',{class:'row'},q));root.appendChild(list);draw();
};

/* ---------- boot ---------- */
function boot(){
  $$('span.fact[data-f]').forEach(function(e){var f=FACT[e.getAttribute('data-f')];e.className='fact lvl-'+(f?f.level:'secondary');e.setAttribute('tabindex','0');e.setAttribute('role','button');e.setAttribute('aria-label','Источник '+e.getAttribute('data-f'));});
  $$('.widget[data-widget]').forEach(function(w){var f=W[w.getAttribute('data-widget')];if(f){try{f(w);}catch(e){w.textContent='Интерактивный блок недоступен: '+e.message;}}});
  var secs=$$('main section.level1');var toc=$('nav.toc');
  if(toc){toc.appendChild(h('h2',null,'Содержание'));secs.forEach(function(s){var t=$('h1',s);if(!t)return;toc.appendChild(h('a',{href:'#'+s.id,'data-id':s.id},t.textContent));});}
  var links=$$('nav.toc a');
  if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){links.forEach(function(a){a.classList.toggle('on',a.getAttribute('data-id')===e.target.id);});}});},{rootMargin:'-20% 0px -70% 0px'});secs.forEach(function(s){io.observe(s);});}
  var bar=$('#progress');window.addEventListener('scroll',function(){var d=document.documentElement;var p=d.scrollTop/(d.scrollHeight-d.clientHeight);bar.style.width=(Math.max(0,Math.min(1,p))*100)+'%';},{passive:true});
  function setTheme(t){document.documentElement.setAttribute('data-theme',t);try{localStorage.setItem('tm-theme',t);}catch(e){}}
  var saved=null;try{saved=localStorage.getItem('tm-theme');}catch(e){}
  setTheme(saved||(window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'));
  $('#theme').addEventListener('click',function(){setTheme(document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark');});
  var fs=19;function setFs(n){fs=Math.max(15,Math.min(24,n));document.documentElement.style.setProperty('--tm-fs',fs+'px');}
  $('#fsm').addEventListener('click',function(){setFs(fs-1);});$('#fsp').addEventListener('click',function(){setFs(fs+1);});
  $('#vb').addEventListener('click',function(){var t=$('#versions');if(t)t.scrollIntoView();});
  $$('main h1,main h2').forEach(function(hd){var id=(hd.closest('section')||hd).id;if(hd.tagName==='H1'&&id){hd.style.cursor='pointer';hd.title='Скопировать ссылку на раздел';hd.addEventListener('click',function(){try{navigator.clipboard.writeText(location.href.split('#')[0]+'#'+id);}catch(e){}});}});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();
