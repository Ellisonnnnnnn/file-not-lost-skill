import sys
p='/Users/gaicibi/WorkBuddy/工业 AI 平台/智能数据预测/智能数据预测设计稿-20261117-v1.html'
s=open(p,encoding='utf-8').read()
anchor='<style id="design-list-boe">'
print('anchor',s.count(anchor))
if s.count(anchor)!=1: sys.exit(1)
tokens='''<style id="design-list-boe">\n/* BOE semantic tokens scoped to chat page (for inlined 5-4/5-7/5-16 controls) */\n.chat-page{\n  --color-primary-default:#0081FF;\n  --color-primary-hover:#2E98FF;\n  --color-primary-active:#0070DE;\n  --color-primary-bg:#E6F2FF;\n  --color-blue-2:#E6F2FF;\n  --color-text-primary:#303133;\n  --color-text-secondary:#606266;\n  --color-text-tertiary:#909399;\n  --color-text-placeholder:#C0C4CC;\n  --color-text-disabled:#C0C4CC;\n  --color-neutral-white:#FFFFFF;\n  --color-bg-page:#FFFFFF;\n  --color-bg-container:#F5F7FA;\n  --color-border-base:#E1E4EB;\n  --color-border-light:#D7DAE0;\n  --color-border-strong:#C0C4CC;\n  --color-error-default:#F56C6C;\n  --color-error-bg:#FEF0F0;\n  --color-success-default:#67C23A;\n  --color-success-bg:#F0F9EB;\n  --radius-control:4px;\n  --radius-full:999px;\n  --font-family-base:"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Helvetica Neue",Arial,sans-serif;\n  --font-weight-regular:400;\n  --font-weight-medium:500;\n  --font-size-t08:14px;\n  --font-size-t09:12px;\n  --line-height-t09:20px;\n  --shadow-popup:0 -2px 8px rgba(0,0,0,.02),0 8px 14px 2px rgba(0,0,0,.06),0 5px 5px -3px rgba(0,0,0,.05);\n  --shadow-elevation-0:0 1px 2px rgba(0,0,0,.04);\n  --boe-component-input-number-accent:#0081FF;\n}\n'''
s=s.replace(anchor,tokens,1)
open(p,'w',encoding='utf-8').write(s)
print('tokens inserted')
