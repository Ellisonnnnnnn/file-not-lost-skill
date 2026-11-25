import re,sys
p='/Users/gaicibi/WorkBuddy/工业 AI 平台/智能数据预测/智能数据预测设计稿-20261117-v1.html'
s=open(p,encoding='utf-8').read()
start=s.find('/* ===== BOE 5-7-date-picker / 5-16-input-number canonical styles')
end=s.find('</style>',start)
if start<0 or end<0: sys.exit('marker not found')
seg=s[start:end]
drop=['.boe-control-clear','.boe-control-inline-clear','.boe-control-location','.boe-control-icon--sm',
      '.size-lg','.size-md','.size-mini','.is-disabled','.demo-static','.boe-date-placeholder',
      '.boe-date-hint','.is-today','.is-in-range','.is-range-','.is-outside',':disabled',
      '.boe-range-','.range-separator','.is-range','.picker-tiles','.picker-tile',
      '.is-hover','.is-active','.is-error','.is-success','--compact']
kept=[];removed=0
def repl(m):
    global removed
    sel=m.group(1)
    clean=re.sub(r'/\*[\s\S]*?\*/','',sel).strip()
    if clean.startswith('@'):
        return m.group(0)
    if any(tok in clean for tok in drop):
        removed+=1
        # keep comments that contain BOE_COMPONENT_STYLE markers
        comments=re.findall(r'/\*[\s\S]*?\*/',sel)
        keepc=' '.join(c for c in comments if 'BOE_COMPONENT_STYLE' in c or 'canonical styles' in c or '自动生成' in c)
        return ('\n'+keepc+'\n') if keepc else '\n'
    return m.group(0)
newseg=re.sub(r'([^{}]+)\{([^{}]*)\}',repl,seg)
s=s[:start]+newseg+s[end:]
open(p,'w',encoding='utf-8').write(s)
print('removed rules',removed,'segment bytes',len(seg),'->',len(newseg))
