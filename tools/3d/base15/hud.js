/* 시험판 전용: 기존 주민 ↔ 새 주민 바꿔 보기 + 주민 수·그리기 호출·삼각형·프레임 수 */
(()=>{const go=()=>{const B=window.__b15;if(!B||!document.body){setTimeout(go,300);return;}
 const el=document.createElement('div');el.style.cssText='position:fixed;left:calc(12px + env(safe-area-inset-left,0px));top:calc(64px + env(safe-area-inset-top,0px));z-index:99;display:flex;flex-wrap:wrap;gap:4px;align-items:center;max-width:304px;padding:6px;border-radius:14px;background:rgba(20,24,32,.72);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);color:#fff;font:600 12px/1 system-ui,sans-serif;white-space:nowrap';
 const bt={},o=document.createElement('span'),sync=()=>{for(const k in bt)bt[k].style.background=k===B.mode()?'rgba(255,255,255,.22)':'transparent';};
 for(const [k,t] of [['','기존 주민'],['b','새 주민']]){const b=document.createElement('button');b.type='button';b.textContent=t;b.style.cssText='border:0;border-radius:9px;padding:7px 9px;font:inherit;color:#fff;background:transparent';b.onclick=()=>{B.set(k);sync();};el.appendChild(b);bt[k]=b;}
 o.style.cssText='flex-basis:100%;padding:4px 6px 2px;font-weight:500;font-size:11px;font-variant-numeric:tabular-nums;opacity:.85';el.appendChild(o);sync();document.body.appendChild(el);
 let f0=B.stat().f,t0=performance.now(),mc=0,mt=0;setInterval(()=>{const s=B.stat();if(s.c>mc){mc=s.c;mt=s.t;}},100);
 setInterval(()=>{const s=B.stat(),t=performance.now(),fps=(s.f-f0)/(t-t0)*1000;f0=s.f;t0=t;o.textContent='주민 '+B.n()+' · 호출 '+mc+' · 삼각형 '+(mt>=1e6?(mt/1e6).toFixed(2)+'M':Math.round(mt/1e3)+'k')+' · '+fps.toFixed(0)+'fps';mc=0;mt=0;sync();},1000);};go();})();
