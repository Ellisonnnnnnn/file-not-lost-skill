import io, sys
p='/Users/gaicibi/WorkBuddy/工业 AI 平台/智能数据预测/智能数据预测设计稿-20261117-v1.html'
s=open(p,encoding='utf-8').read()
def rep(old,new,n=1,label=''):
    global s
    c=s.count(old)
    if c!=n:
        print('FAIL count',c,'expected',n,label,old[:120]);sys.exit(1)
    s=s.replace(old,new,n)
    print('OK',label or old[:50])

# ---------- 1. helper functions: correct module-details wrappers ----------
old_num_start=s.index('function boeNumber(')
old_num_end=s.index('function boeDate(',old_num_start)
new_num=r'''function boeNumber(id,value,min,max,step,more){return '<div class="input-number-module-details" style="width:100%"><div class="boe-input-number input-number-component-token-scope" data-boe-input-number data-min="'+min+'" data-max="'+max+'" data-step="'+step+'" style="width:100%"><input class="boe-input-number-input" data-input-number-input id="'+id+'" type="number" value="'+esc(value)+'" min="'+min+'" max="'+max+'" step="'+step+'" '+(more||'')+'><div class="boe-input-number-actions"><button class="boe-input-number-button boe-input-number-up" data-input-number-action="increase" type="button" aria-label="增加"><svg class="boe-input-number-icon boe-control-icon" aria-hidden="true"><use href="#boe-icon-caret-down-small"></use></svg></button><button class="boe-input-number-button boe-input-number-down" data-input-number-action="decrease" type="button" aria-label="减少"><svg class="boe-input-number-icon boe-control-icon" aria-hidden="true"><use href="#boe-icon-caret-down-small"></use></svg></button></div></div></div>';}
'''
s=s[:old_num_start]+new_num+s[old_num_end:]
print('OK rewrite boeNumber')

old_date_start=s.index('function boeDate(')
old_date_end=s.index('function boeSelect(',old_date_start)
new_date=r'''function boeDate(id,value){var v=String(value||''),m=v.match(/^(\d{4})-(\d{2})-(\d{2})$/),y=m?Number(m[1]):2026,mo=m?Number(m[2])-1:10;return '<input type="hidden" id="'+id+'" value="'+esc(v)+'"><div class="picker-module-details" data-picker-module="date-picker" style="width:100%"><div class="boe-date-picker'+(v?' has-value':'')+'" data-date-picker data-date-input="'+id+'" data-selected="'+esc(v)+'" data-year="'+y+'" data-month="'+mo+'" style="width:100%"><button class="boe-date-trigger" type="button" aria-haspopup="dialog" aria-expanded="false"><span class="boe-date-value'+(v?' has-value':'')+'">'+esc(v||'请选择日期')+'</span><svg class="boe-control-icon boe-control-suffix boe-control-suffix--passive boe-control-calendar boe-date-calendar" aria-hidden="true"><use href="#boe-icon-calendar"></use></svg></button><div class="boe-date-panel" role="dialog" aria-label="选择日期"></div></div></div>';}
'''
s=s[:old_date_start]+new_date+s[old_date_end:]
print('OK rewrite boeDate')

# ---------- 2. listSelect: carry input id, full width ----------
rep(r'''<div class="boe-select select-component-token-scope" data-select data-select-key="'+key+'">''',
    r'''<div class="boe-select select-component-token-scope" data-select data-select-key="'+key+'" data-select-input-id="'+id+'" style="width:100%">''',1,'listSelect root')

rep(r'''key=el.getAttribute('data-select-key'),input=$(key==='metric'?'filterMetric':'filterStatus'),options=''',
    r'''key=el.getAttribute('data-select-key'),input=$(select.getAttribute('data-select-input-id')),options=''',1,'listSelectOption input')

rep(r''' closeListSelects();select.querySelector('.boe-select-trigger').focus();
}
/* 分页器''',
    r''' closeListSelects();select.querySelector('.boe-select-trigger').focus();input.dispatchEvent(new Event('change',{bubbles:true}));
}
/* 分页器''',1,'listSelectOption dispatch')

rep(r'''.list-page [data-select]''',r'''[data-select]''',1,'click global select')
rep(r'''e.target.closest('.list-page .boe-select')''',r'''e.target.closest('.boe-select')''',1,'keydown global select')

rep(r'''$('cDimensionValue').innerHTML=options(dimensionOptions(e.target.value),'');''',
    r'''refreshBoeSelect('cDimensionValue',dimensionOptions(e.target.value),'');''',2,'cDimension refresh')

# ---------- 3. confirm card controls ----------
repls=[
(r'''select('cMetric',metricOptions(c),c.metric)''',r'''boeSelect('cMetric','metric',metricOptions(c),c.metric)''',1),
(r'''select('cProduct',products,c.product)''',r'''boeSelect('cProduct','product',products,c.product)''',1),
(r'''input('cStart',c.start,'date')''',r'''boeDate('cStart',c.start)''',1),
(r'''input('cEnd',c.end,'date')''',r'''boeDate('cEnd',c.end)''',1),
(r'''input('cHorizon',c.horizon,'number','min="1" max="60" step="1"')''',r'''boeNumber('cHorizon',c.horizon,1,60,1)''',1),
(r'''select('cInterval',[[90,'90% · 常规观察'],[95,'95% · 更宽范围']],c.interval)''',r'''boeSelect('cInterval','interval',[[90,'90% · 常规观察'],[95,'95% · 更宽范围']],c.interval)''',1),
(r'''input('cThreshold',typeof c.threshold==='undefined'?'':c.threshold,'number','min="0" step="any" placeholder="例如：95"')''',r'''boeNumber('cThreshold',typeof c.threshold==='undefined'?'':c.threshold,0,'','any','placeholder="例如：95"')''',1),
(r'''input('cVolume',c.minVolume,'number','min="0" step="1"')''',r'''boeNumber('cVolume',c.minVolume,0,'',1)''',1),
(r'''select('cDimension',[['','不筛选'],['LINE_ID','LINE_ID · 产线'],['FACTORY','FACTORY · 工厂']],c.dimension)''',r'''boeSelect('cDimension','dimension',[['','不筛选'],['LINE_ID','LINE_ID · 产线'],['FACTORY','FACTORY · 工厂']],c.dimension)''',1),
(r'''select('cDimensionValue',dimensionOptions(c.dimension),c.dimensionValue)''',r'''boeSelect('cDimensionValue','dimensionValue',dimensionOptions(c.dimension),c.dimensionValue)''',1),
(r'''select('cSource',a,currentValue)''',r'''boeSelect('cSource','source',a,currentValue)''',1),
(r'''select('fFile',opts,f.fileId)''',r'''boeSelect('fFile','fFile',opts,f.fileId)''',1),
(r'''select('fDate',cols,f.dateColumn)''',r'''boeSelect('fDate','fDate',cols,f.dateColumn)''',1),
(r'''select('fValue',cols,f.valueColumn)''',r'''boeSelect('fValue','fValue',cols,f.valueColumn)''',1),
(r'''input('fLabel',f.label||'','text','maxlength="60"')''',r'''boeInput('fLabel',f.label||'','text','maxlength="60"')''',1),
(r'''select('fUnit',[['%','百分比（%）'],['片','数量（片）'],['数值','数值（无单位）']],f.unit)''',r'''boeSelect('fUnit','fUnit',[['%','百分比（%）'],['片','数量（片）'],['数值','数值（无单位）']],f.unit)''',1),
(r'''select('fProductColumn',[['','不区分产品']].concat(cols.slice(1)),f.productColumn)''',r'''boeSelect('fProductColumn','fProductColumn',[['','不区分产品']].concat(cols.slice(1)),f.productColumn)''',1),
(r'''select('fAggregation',[['mean','按日平均'],['sum','按日求和'],['last','按日取最后一条']],f.aggregation)''',r'''boeSelect('fAggregation','fAggregation',[['mean','按日平均'],['sum','按日求和'],['last','按日取最后一条']],f.aggregation)''',1),
(r'''select('fScale',[['percent','0–100，例如 95.6 / 95.6%'],['ratio','0–1，例如 0.956']],f.scale)''',r'''boeSelect('fScale','fScale',[['percent','0–100，例如 95.6 / 95.6%'],['ratio','0–1，例如 0.956']],f.scale)''',1),
]
for old,new,n in repls: rep(old,new,n,'control')

open(p,'w',encoding='utf-8').write(s)
print('DONE stage1-3')
