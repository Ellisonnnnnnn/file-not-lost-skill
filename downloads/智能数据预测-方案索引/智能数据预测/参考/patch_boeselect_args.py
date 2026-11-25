import sys
p='/Users/gaicibi/WorkBuddy/工业 AI 平台/智能数据预测/智能数据预测设计稿-20261117-v1.html'
s=open(p,encoding='utf-8').read()
pairs=[
("boeSelect('cMetric','metric',metricOptions(c),c.metric)","boeSelect('cMetric',metricOptions(c),c.metric,'metric')"),
("boeSelect('cProduct','product',products,c.product)","boeSelect('cProduct',products,c.product,'product')"),
("boeSelect('cInterval','interval',[[90,'90% · 常规观察'],[95,'95% · 更宽范围']],c.interval)","boeSelect('cInterval',[[90,'90% · 常规观察'],[95,'95% · 更宽范围']],c.interval,'interval')"),
("boeSelect('cDimension','dimension',[['','不筛选'],['LINE_ID','LINE_ID · 产线'],['FACTORY','FACTORY · 工厂']],c.dimension)","boeSelect('cDimension',[['','不筛选'],['LINE_ID','LINE_ID · 产线'],['FACTORY','FACTORY · 工厂']],c.dimension,'dimension')"),
("boeSelect('cDimensionValue','dimensionValue',dimensionOptions(c.dimension),c.dimensionValue)","boeSelect('cDimensionValue',dimensionOptions(c.dimension),c.dimensionValue,'dimensionValue')"),
("boeSelect('cSource','source',a,currentValue)","boeSelect('cSource',a,currentValue,'source')"),
("boeSelect('fFile','fFile',opts,f.fileId)","boeSelect('fFile',opts,f.fileId,'fFile')"),
("boeSelect('fDate','fDate',cols,f.dateColumn)","boeSelect('fDate',cols,f.dateColumn,'fDate')"),
("boeSelect('fValue','fValue',cols,f.valueColumn)","boeSelect('fValue',cols,f.valueColumn,'fValue')"),
("boeSelect('fUnit','fUnit',[['%','百分比（%）'],['片','数量（片）'],['数值','数值（无单位）']],f.unit)","boeSelect('fUnit',[['%','百分比（%）'],['片','数量（片）'],['数值','数值（无单位）']],f.unit,'fUnit')"),
("boeSelect('fProductColumn','fProductColumn',[['','不区分产品']].concat(cols.slice(1)),f.productColumn)","boeSelect('fProductColumn',[['','不区分产品']].concat(cols.slice(1)),f.productColumn,'fProductColumn')"),
("boeSelect('fAggregation','fAggregation',[['mean','按日平均'],['sum','按日求和'],['last','按日取最后一条']],f.aggregation)","boeSelect('fAggregation',[['mean','按日平均'],['sum','按日求和'],['last','按日取最后一条']],f.aggregation,'fAggregation')"),
("boeSelect('fScale','fScale',[['percent','0–100，例如 95.6 / 95.6%'],['ratio','0–1，例如 0.956']],f.scale)","boeSelect('fScale',[['percent','0–100，例如 95.6 / 95.6%'],['ratio','0–1，例如 0.956']],f.scale,'fScale')"),
]
for old,new in pairs:
    c=s.count(old)
    if c!=1: print('FAIL',c,old[:80]);sys.exit(1)
    s=s.replace(old,new,1)
    print('OK',old[:45])
open(p,'w',encoding='utf-8').write(s)
print('DONE')
