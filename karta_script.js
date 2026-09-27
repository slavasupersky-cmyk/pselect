/* ---------- объекты: дома реальные (база NOTA), квартиры, цены и комментарии — демо ---------- */
const OBJ = {{OBJ_JSON}};
const TOTAL = 197;   // объектов в базе сейчас
const PAGE = 8;      // карточек за раз
const SN = {w:"Был ранее",n:"Новый за неделю",g:"Ушёл за неделю"};
const ORDER = {n:0,w:1,g:2};
const fmt = n => n.toLocaleString("ru-RU");
const cnt = s => OBJ.filter(o=>o.s===s).length;
document.querySelectorAll('[data-stat=all]').forEach(e=>e.textContent = TOTAL);
document.querySelectorAll('[data-stat=new]').forEach(e=>e.textContent = "+"+cnt('n'));
document.querySelectorAll('[data-stat=gone]').forEach(e=>e.textContent = "−"+cnt('g'));

const pts = document.getElementById('pts');
const ptsHome = document.getElementById('pts-home');
const list = document.getElementById('objlist');
const panel = document.getElementById('panel');
let sel = null, filter = 'all', cfilter = 'all', shownMax = PAGE;
const COL = {w:'var(--was)',n:'var(--new)',g:'var(--gone)'};

/* точки на карте (и на мини-карте главной) */
function dot(o, big){
  const g = document.createElementNS('http://www.w3.org/2000/svg','g');
  g.setAttribute('class','pt'); g.dataset.id=o.id;
  const r = (o.p>=200?7.5:o.p>=120?6:5) * (big?1:1.15);
  g.innerHTML = `<circle class="h" cx="${o.x}" cy="${o.y}" r="16"/><circle class="d" cx="${o.x}" cy="${o.y}" r="${r}" fill="${COL[o.s]}" stroke="var(--bg2)" stroke-width="1.5" ${o.s==='g'?'opacity=".8"':''}/>`;
  return g;
}
OBJ.forEach(o=>{
  const g = dot(o, true); g.addEventListener('click',()=>select(o.id,true)); pts.appendChild(g);
  if(ptsHome) ptsHome.appendChild(dot(o, false));
});

/* карточки: группы по статусу, внутри — по цене */
const sorted = [...OBJ].sort((a,b)=>ORDER[a.s]-ORDER[b.s] || a.p-b.p);
sorted.forEach(o=>{
  const gone = o.s==='g';
  const c = document.createElement('article');
  c.className = 'card'; c.dataset.id=o.id; c.dataset.s=o.s;
  c.innerHTML = `<div class="ph" data-open><img src="${o.img}" alt="${o.n}"><span class="tag"><i class="st-${o.s}"></i>${SN[o.s]}</span></div>
    <div class="cb">
      <h3 data-open>${o.n}</h3>
      <p class="sub">${o.d} · ${o.a}<br>${o.c} · ${o.m} м² · ${o.r} сп. · ${o.f}/${o.ff} эт.</p>
      <div class="pr">${fmt(o.p)} млн ₽<small>${fmt(Math.round(o.p*1e6/o.m/1000))} тыс. ₽/м²</small></div>
      <div class="why"><small>Почему в Select</small>${o.why}</div>
      <div class="cdet"></div>
      <button class="lnk more" data-open>Подробнее ↓</button>
      <div class="acts">${gone?`<button class="btn ghost" data-params>Подобрать похожие</button>`:`
        <button class="btn" data-lead="Получить презентацию">Получить презентацию</button>
        <button class="btn ghost" data-lead="Обсудить вариант">Обсудить вариант</button>`}</div>
    </div>`;
  c.querySelectorAll('[data-open]').forEach(b=>b.addEventListener('click',()=>select(o.id,false)));
  c.querySelectorAll('[data-lead]').forEach(b=>b.addEventListener('click',()=>openLead(b.dataset.lead,o)));
  list.appendChild(c);
});

function detailHTML(o){
  const gal = [];
  if(o.pic1) gal.push(`<figure><img src="${o.pic1}" alt="Интерьер"><figcaption>Интерьер · демо-визуализация</figcaption></figure>`);
  if(o.pic2) gal.push(`<figure><img src="${o.pic2}" alt=""><figcaption>${o.cap2||"Фасад"} · демо-визуализация</figcaption></figure>`);
  if(o.plan) gal.push(`<figure>${o.plan}<figcaption>Планировка · вымышленная, для прототипа</figcaption></figure>`);
  return `<div class="params"><div><small>Площадь</small>${o.m} м²</div><div><small>Спален</small>${o.r}</div><div><small>Этаж</small>${o.f} из ${o.ff}</div><div><small>Класс</small>${o.c}</div><div><small>Потолки</small>${o.h||'—'}</div><div><small>Состояние</small>${o.st}</div></div>
    ${gal.join('')}
    <p>${o.t||(o.s==='g'?'Объект ушёл с рынка на этой неделе. Похожие, которые ещё готовятся к выходу, покажем по запросу.':'Проверен: документы, история прав, перепланировки, дом. Презентация с адресом и условиями приходит лично от Елены.')}</p>`;
}

function renderPanel(){
  if(sel===null){
    const n=cnt('n'),g=cnt('g');
    panel.innerHTML = `<p class="eyebrow">За неделю</p>
      <div class="stats"><div><b>${TOTAL}</b><small>объектов в базе</small></div><div class="n"><b>+${n}</b><small>новых</small></div><div class="g"><b>−${g}</b><small>ушли</small></div></div>
      <p class="mute">На карте — часть базы. Нажмите на точку или карточку ниже; точка крупнее — дороже.</p>
      <p class="mute" style="font-size:14px">Ушедшие объекты остаются на карте неделю: так видно, как двигается рынок в вашем районе.</p>
      <div class="acts"><button class="btn ghost" data-params>Ищете другое? Оставьте параметры</button></div>`;
    return;
  }
  const o = OBJ[sel];
  panel.innerHTML = `${o.img?`<img class="pimg" src="${o.img}" alt="">`:''}
    <span class="tag"><i class="st-${o.s}"></i>${SN[o.s]}</span>
    <div><p class="eyebrow">${o.d}</p><h3 style="margin-top:6px">${o.n}</h3><p class="mute" style="font-size:13px">${o.a}</p></div>
    <div class="price">${fmt(o.p)} млн ₽</div>
    <p class="mute" style="font-size:14px"><b style="font-weight:500;color:var(--ink)">Почему в Select.</b> ${o.why}</p>
    <div class="acts"><button class="btn ghost sm" id="tocard">К карточке ↓</button></div>`;
  panel.querySelector('#tocard').addEventListener('click',()=>{const r=list.querySelector(`.card[data-id="${o.id}"]`);r.scrollIntoView({behavior:'smooth',block:'start'})});
}

function select(id, fromMap){
  const same = sel===id;
  sel = same && !fromMap ? null : id;
  document.querySelectorAll('#pts .pt').forEach(p=>p.classList.toggle('sel',+p.dataset.id===sel));
  if(sel!==null){ /* выбранная карточка должна быть видна: раскрываем страницу до неё */
    const vis = visibleCards(); const i = vis.findIndex(c=>+c.dataset.id===sel);
    if(i>=shownMax) shownMax = i+1;
  }
  list.querySelectorAll('.card').forEach(c=>{
    const open = +c.dataset.id===sel;
    const det = c.querySelector('.cdet');
    if(open && !det.innerHTML) det.innerHTML = detailHTML(OBJ[sel]);
    c.classList.toggle('open', open); c.classList.toggle('sel', open);
    c.querySelector('.more').textContent = open ? 'Свернуть ↑' : 'Подробнее ↓';
  });
  renderPanel(); paginate();
  if(fromMap && sel!==null){
    const r = list.querySelector(`.card[data-id="${sel}"]`);
    const rect = r.getBoundingClientRect();
    if(rect.top<0 || rect.top>window.innerHeight*0.7) r.scrollIntoView({behavior:'smooth',block:'start'});
  }
}
const hidden = o => (filter!=='all'&&o.s!==filter) || (cfilter!=='all'&&o.c!==cfilter);
const visibleCards = () => [...list.querySelectorAll('.card')].filter(c=>!hidden(OBJ[+c.dataset.id]));
function paginate(){
  const vis = visibleCards();
  vis.forEach((c,i)=>c.classList.toggle('paged', i>=shownMax));
  const more = document.getElementById('showmore'); const rest = vis.length - shownMax;
  more.parentElement.style.display = rest>0 ? '' : 'none';
  if(rest>0) more.textContent = `Показать ещё ${Math.min(PAGE,rest)} из ${rest}`;
}
function applyFilter(){
  let shown=0;
  document.querySelectorAll('#pts .pt').forEach(p=>{const h=hidden(OBJ[+p.dataset.id]);p.classList.toggle('hidden',h);if(!h)shown++});
  list.querySelectorAll('.card').forEach(c=>c.classList.toggle('hidden',hidden(OBJ[+c.dataset.id])));
  document.getElementById('map-count').textContent = shown+' на карте';
  shownMax = PAGE;
  if(sel!==null && hidden(OBJ[sel])){ select(sel,false); } else paginate();
}
document.getElementById('showmore').addEventListener('click',()=>{shownMax+=PAGE;paginate()});
document.querySelectorAll('.chip[data-f]').forEach(c=>c.addEventListener('click',()=>{
  filter=c.dataset.f;document.querySelectorAll('.chip[data-f]').forEach(x=>x.setAttribute('aria-pressed',x===c));applyFilter();
}));
document.querySelectorAll('.chip[data-c]').forEach(c=>c.addEventListener('click',()=>{
  cfilter=c.dataset.c;document.querySelectorAll('.chip[data-c]').forEach(x=>x.setAttribute('aria-pressed',x===c));applyFilter();
}));
renderPanel(); applyFilter();
