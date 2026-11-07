'use strict';
// Leitor visual experimental sem TextDetector e sem calibração do usuário.
// Compara formas normalizadas dos símbolos com fontes locais; retorna null em caso de dúvida.
const CardVision=(()=>{
 const ranks=['A','K','Q','J','10','9','8','7','6','5','4','3','2'],suits=['♦','♥','♠','♣'];
 const fonts=['Arial','Arial Black','Georgia','Times New Roman','Verdana','sans-serif'];
 const make=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c};
 function ink(canvas,red){const {width:w,height:h}=canvas,c=canvas.getContext('2d'),p=c.getImageData(0,0,w,h).data,mask=new Uint8Array(w*h);let n=0;
 for(let i=0;i<mask.length;i++){const k=i*4,r=p[k],g=p[k+1],b=p[k+2],dark=Math.min(r,g,b)<135,chromatic=r>g*1.28&&r>b*1.28&&r>75;const v=red?chromatic:dark&&!chromatic;if(v){mask[i]=1;n++}}
 return {mask,w,h,n}}
 function normalize(src){let minx=src.w,miny=src.h,maxx=-1,maxy=-1;for(let y=0;y<src.h;y++)for(let x=0;x<src.w;x++)if(src.mask[y*src.w+x]){minx=Math.min(x,minx);miny=Math.min(y,miny);maxx=Math.max(x,maxx);maxy=Math.max(y,maxy)}
 if(maxx<0||maxy<0)return null;const out=new Uint8Array(24*32),bw=maxx-minx+1,bh=maxy-miny+1;for(let y=0;y<32;y++)for(let x=0;x<24;x++){const sx=Math.min(src.w-1,minx+Math.floor((x+.5)*bw/24)),sy=Math.min(src.h-1,miny+Math.floor((y+.5)*bh/32));out[y*24+x]=src.mask[sy*src.w+sx]}return out}
 function dist(a,b){let n=0;for(let i=0;i<a.length;i++)if(a[i]!==b[i])n++;return n/a.length}
 const templates={rank:[],suit:[]};
 for(const font of fonts)for(const bold of [true,false])for(const [type,items] of [['rank',ranks],['suit',suits]])for(const label of items){const c=make(110,110),x=c.getContext('2d');x.fillStyle='white';x.fillRect(0,0,110,110);x.font=(bold?'bold ':'')+'64px '+font;x.textBaseline='top';x.fillStyle=type==='suit'&&['♥','♦'].includes(label)?'#d92037':'#151515';x.fillText(label,8,8);const norm=normalize(ink(c,type==='suit'&&['♥','♦'].includes(label)));if(norm)templates[type].push({label,norm})}
 function match(src,type,allowed){const v=normalize(src);if(!v)return null;const scores=[];for(const t of templates[type]){if(allowed&&!allowed.includes(t.label))continue;const d=dist(v,t.norm);const prev=scores.find(s=>s.label===t.label);if(!prev)scores.push({label:t.label,d});else prev.d=Math.min(prev.d,d)}scores.sort((a,b)=>a.d-b.d);if(!scores.length)return null;return {value:scores[0].label,score:scores[0].d,gap:(scores[1]?.d??1)-scores[0].d}}
 function crop(img,x,y,w,h){const c=make(w,h);c.getContext('2d').drawImage(img,x,y,w,h,0,0,w,h);return c}
 function detect(canvas,zone){const x=Math.round(zone.x*canvas.width),y=Math.round(zone.y*canvas.height),w=Math.round(zone.w*canvas.width),h=Math.round(zone.h*canvas.height);if(x<0||y<0||x+w>canvas.width||y+h>canvas.height||w<20||h<30)return null;
 const card=crop(canvas,x,y,w,h),p=card.getContext('2d').getImageData(0,0,w,h).data;let light=0,red=0,black=0;
 for(let i=0;i<p.length;i+=4){const r=p[i],g=p[i+1],b=p[i+2];if(r>180&&g>165&&b>145)light++;if(r>g*1.28&&r>b*1.28&&r>75)red++;if(r<100&&g<100&&b<100)black++}
 if(light/(w*h)<.30)return null;const isRed=red>black*.65;
 // Região do canto superior esquerdo: valor na primeira faixa, naipe na faixa seguinte.
 const rank=crop(card,Math.round(w*.04),Math.round(h*.02),Math.max(10,Math.round(w*.42)),Math.max(14,Math.round(h*.34)));
 const suit=crop(card,Math.round(w*.04),Math.round(h*.31),Math.max(10,Math.round(w*.42)),Math.max(14,Math.round(h*.25)));
 const a=match(ink(rank,isRed),'rank'),b=match(ink(suit,isRed),'suit',isRed?['♦','♥']:['♠','♣']);
 if(!a||!b||a.score>.36||b.score>.40||a.gap<.018||b.gap<.018)return null;
 return {card:a.value+b.value,confidence:Math.round(100*(1-(a.score+b.score)/2))}}
 return {detect};
})();