import sys
p='/Users/gaicibi/WorkBuddy/工业 AI 平台/智能数据预测/智能数据预测设计稿-20261117-v1.html'
s=open(p,encoding='utf-8').read()
anchor="document.addEventListener('click',function(e){var el=e.target;while(el"
print('anchor',s.count(anchor))
if s.count(anchor)!=1: sys.exit(1)
runtime=r'''/* ===== BOE 5-7-date-picker / 5-16-input-number minimal runtime (standalone) ===== */
function datePad(n){return n<10?'0'+n:''+n;}
function dateISO(y,m,d){return y+'-'+datePad(m+1)+'-'+datePad(d);}
function closeDatePickers(except){var nodes=document.querySelectorAll('.boe-date-picker.is-open');for(var i=0;i<nodes.length;i++){if(nodes[i]!==except){nodes[i].classList.remove('is-open');var tr=nodes[i].querySelector('.boe-date-trigger');if(tr){tr.setAttribute('aria-expanded','false');}}}}
function renderDatePanel(root){
 var y=Number(root.getAttribute('data-year')),mo=Number(root.getAttribute('data-month')),panel=root.querySelector('.boe-date-panel');
 if(!panel||!isFinite(y)){return;}
 var arrow='<svg class="boe-control-icon" aria-hidden="true"><use href="#boe-icon-caret-down-small"></use></svg>';
 var lead=new Date(y,mo,1).getDay(),total=new Date(y,mo+1,0).getDate(),sel=root.getAttribute('data-selected'),cells='';
 for(var k=0;k<lead;k++){cells+='<span aria-hidden="true"></span>';}
 for(var d=1;d<=total;d++){var iso=dateISO(y,mo,d),on=iso===sel;cells+='<button type="button" class="boe-date-cell'+(on?' is-selected':'')+'" data-date-cell="'+iso+'" aria-label="'+iso+'"'+(on?' aria-pressed="true"':'')+'>'+d+'</button>';}
 panel.innerHTML='<div class="boe-date-panel-header"><button type="button" class="boe-date-nav boe-date-prev" data-date-nav="-1" aria-label="上个月">'+arrow+'</button><span class="boe-date-title">'+y+' 年 '+(mo+1)+' 月</span><button type="button" class="boe-date-nav boe-date-next" data-date-nav="1" aria-label="下个月">'+arrow+'</button></div><div class="boe-date-week" aria-hidden="true"><span>日</span><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span></div><div class="boe-date-grid">'+cells+'</div><div class="boe-date-panel-footer"><button type="button" class="boe-date-link" data-date-today>今天</button><button type="button" class="boe-date-link" data-date-clear>清空</button></div>';
}
function setPickerDate(root,value){
 var id=root.getAttribute('data-date-input'),hidden=$(id),val=String(value||''),m=val.match(/^(\d{4})-(\d{2})-(\d{2})$/);
 root.setAttribute('data-selected',val);
 if(m){root.setAttribute('data-year',m[1]);root.setAttribute('data-month',Number(m[2])-1);}
 root.classList.toggle('has-value',!!val);
 var label=root.querySelector('.boe-date-value');if(label){label.textContent=val||'请选择日期';label.classList.toggle('has-value',!!val);}
 if(hidden){hidden.value=val;hidden.dispatchEvent(new Event('change',{bubbles:true}));}
 root.classList.remove('is-open');var tr=root.querySelector('.boe-date-trigger');if(tr){tr.setAttribute('aria-expanded','false');}
}
function stepNumber(root,dir){
 var input=root.querySelector('[data-input-number-input]');if(!input){return;}
 var step=Number(root.getAttribute('data-step'))||1,min=root.getAttribute('data-min'),max=root.getAttribute('data-max');
 var cur=Number(input.value),base=isFinite(cur)?cur:(min!==''&&min!==null?Number(min):0),next=base+dir*step;
 if(min!==''&&min!==null&&next<Number(min)){next=Number(min);}
 if(max!==''&&max!==null&&next>Number(max)){next=Number(max);}
 input.value=next;input.dispatchEvent(new Event('change',{bubbles:true}));
}
document.addEventListener('click',function(e){
 var trigger=e.target.closest('.boe-date-trigger');
 if(trigger){var root=trigger.closest('.boe-date-picker'),open=!root.classList.contains('is-open');closeDatePickers(root);if(open){renderDatePanel(root);}root.classList.toggle('is-open',open);trigger.setAttribute('aria-expanded',String(open));return;}
 var nav=e.target.closest('[data-date-nav]');
 if(nav){var r=nav.closest('.boe-date-picker'),mo=Number(r.getAttribute('data-month'))+Number(nav.getAttribute('data-date-nav')),y=Number(r.getAttribute('data-year'));if(mo<0){mo=11;y--;}if(mo>11){mo=0;y++;}r.setAttribute('data-month',mo);r.setAttribute('data-year',y);renderDatePanel(r);return;}
 var cell=e.target.closest('[data-date-cell]');
 if(cell){setPickerDate(cell.closest('.boe-date-picker'),cell.getAttribute('data-date-cell'));return;}
 if(e.target.closest('[data-date-today]')){var t=new Date();setPickerDate(e.target.closest('.boe-date-picker'),dateISO(t.getFullYear(),t.getMonth(),t.getDate()));return;}
 if(e.target.closest('[data-date-clear]')){setPickerDate(e.target.closest('.boe-date-picker'),'');return;}
 if(!e.target.closest('.boe-date-picker')){closeDatePickers();}
 var up=e.target.closest('[data-input-number-action="increase"]'),down=e.target.closest('[data-input-number-action="decrease"]');
 if(up||down){stepNumber((up||down).closest('.boe-input-number'),up?1:-1);}
});
'''
s=s.replace(anchor,runtime+anchor,1)
open(p,'w',encoding='utf-8').write(s)
print('runtime inserted',len(runtime))
