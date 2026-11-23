
/* ===== Widget C: a window (interval) versus the labelled timestamp (point) ===== */
(function(){
  const $=id=>document.getElementById(id), cv=$('cC');
  const N=60, DT=10, BASE=300;                      // 60 rows, one per 10 s, starting 10:05:00 (seconds after 10:00:00)
  const fm=x=>Math.floor(x/60)*60, tRow=i=>BASE+DT*i;
  const fmt=x=>{const m=Math.floor(x/60), s=x%60; return '10:'+String(m).padStart(2,'0')+':'+String(s).padStart(2,'0');};
  // verify.py: start -> (minute - 1):00 (unless minute 0), end -> (minute + 1):59 (unless minute 59)
  function span(s,e,mode){const a=mode==='end'?e:s; let lo=fm(tRow(a)); if(Math.floor(lo/60)%60>0) lo-=60; const hm=Math.floor(fm(tRow(e))/60)%60; return [lo, fm(tRow(e))+59+(hm<59?60:0)];}
  function draw(){
    const L=+$('cL').value, T=BASE+(+$('cT').value), mode=document.querySelector('input[name=cm]:checked').value;
    let E=Math.max(+$('cE').value, L-1); $('cLv').textContent=L; $('cTv').textContent=fmt(T); $('cEv').textContent=E;
    const dpr=window.devicePixelRatio||1, W=cv.clientWidth, H=cv.clientHeight; cv.width=W*dpr; cv.height=H*dpr;
    const x=cv.getContext('2d'); x.scale(dpr,dpr); x.clearRect(0,0,W,H);
    const css=getComputedStyle(document.documentElement), ink=css.getPropertyValue('--ink'), mute=css.getPropertyValue('--mute');
    const pad=24, w=W-2*pad, X=t=>pad+(t-BASE)/600*w;
    // selected window and its tolerance zone
    const s=E-L+1, [lo,hi]=span(s,E,mode);
    x.fillStyle='rgba(27,153,139,.18)'; x.fillRect(X(Math.max(lo,BASE)),30,X(Math.min(hi,BASE+600))-X(Math.max(lo,BASE)),70);
    x.fillStyle='#1b998b'; const a=mode==='end'?E:s; x.fillRect(X(tRow(a)),50,Math.max(3,X(tRow(E))-X(tRow(a))+3),30);
    // row ticks and minute labels
    x.strokeStyle=mute; x.fillStyle=mute; x.font='12px Calibri,sans-serif';
    for(let i=0;i<N;i++){x.beginPath(); x.moveTo(X(tRow(i)),96); x.lineTo(X(tRow(i)),104); x.stroke();}
    for(let m=0;m<=10;m++){const t=BASE+60*m; x.fillText(fmt(t).slice(0,5),X(t)-14,122);}
    // anomaly
    x.strokeStyle='#e4572e'; x.lineWidth=2.5; x.beginPath(); x.moveTo(X(T),20); x.lineTo(X(T),104); x.stroke(); x.lineWidth=1;
    x.fillStyle='#e4572e'; x.fillText('anomalija '+fmt(T),Math.min(X(T)+6,W-130),30);
    // which window ends hit this anomaly
    let k=0, tot=0; x.fillStyle=mute; x.fillText('kurie langai pataiko (pagal lango pabaigą):',pad,152);
    for(let e=L-1;e<N;e++){const [l,h]=span(e-L+1,e,mode), hit=l<=T&&T<=h; tot++; if(hit)k++; x.fillStyle=hit?'#e4572e':'#9ca3af'; x.fillRect(X(tRow(e))-2.5,165,5,26);}
    const sel=lo<=T&&T<=hi;
    $('cS').innerHTML=`<div><b>${fmt(lo)} – ${fmt(hi)}</b>tikrinamas intervalas</div><div><b style="color:${sel?'#e4572e':'inherit'}">${sel?'PATAIKO':'NEPATAIKO'}</b>pasirinktas langas</div><div><b>${k} / ${tot}</b>langų pataiko į šią anomaliją</div>`;
  }
  ['cL','cT','cE'].forEach(id=>$(id).addEventListener('input',draw));
  document.querySelectorAll('input[name=cm]').forEach(r=>r.onchange=draw);
  window.addEventListener('resize',draw); draw();
})();
