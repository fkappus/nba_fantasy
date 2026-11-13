import json, statistics as st
CATS=[('0','PTS'),('6','REB'),('3','AST'),('2','STL'),('1','BLK'),('17','3PM'),('19','FG%'),('20','FT%'),('11','TO')]
LOWER={'TO'}
def cmp(a,b,c):
    if a==b: return 0
    w = a<b if c in LOWER else a>b
    return 1 if w else -1
def h2h(x,y):
    w=sum(cmp(x[c],y[c],c)==1 for _,c in CATS); l=sum(cmp(x[c],y[c],c)==-1 for _,c in CATS)
    return w,l,9-w-l
def res(w,l): return 1 if w>l else (0 if w<l else .5)
def season(yr,label):
    d=json.load(open(f'raw_{yr}.json'))
    teams={t['id']:{'id':t['id'],'name':t['name'].strip(),'abbr':t['abbrev']} for t in d['teams']}
    reg=d['settings']['scheduleSettings']['matchupPeriodCount']
    weeks={}  # wk -> {tid: {cats, opp}}
    for m in d['schedule']:
        wk=m['matchupPeriodId']
        if wk>reg or m.get('winner') in (None,'UNDECIDED') or 'away' not in m: continue
        for a,b in (('home','away'),('away','home')):
            s=m[a]['cumulativeScore']['scoreByStat']
            weeks.setdefault(wk,{})[m[a]['teamId']]={'cats':{c:s[k]['score'] for k,c in CATS},'opp':m[b]['teamId']}
    wks=sorted(weeks); ids=sorted(teams)
    T={i:{**teams[i],'w':0,'l':0,'t':0,'xw':0,'apw':0,'apl':0,'apt':0,'weeks':[],'cat':{c:[0,0] for _,c in CATS},'catActual':{c:[0,0] for _,c in CATS},'oppStr':0} for i in ids}
    appct={}
    for wk in wks:
        W=weeks[wk]
        for i in ids:
            aw=al=at=0
            for j in ids:
                if j==i: continue
                w,l,_=h2h(W[i]['cats'],W[j]['cats']); r=res(w,l)
                aw+=r==1; al+=r==0; at+=r==.5
                for _,c in CATS:
                    x=cmp(W[i]['cats'][c],W[j]['cats'][c],c); T[i]['cat'][c][0]+= 1 if x==1 else (.5 if x==0 else 0); T[i]['cat'][c][1]+=1
            appct[(wk,i)]=(aw+.5*at)/11
            o=W[i]['opp']; w,l,t=h2h(W[i]['cats'],W[o]['cats']); r=res(w,l)
            for _,c in CATS:
                x=cmp(W[i]['cats'][c],W[o]['cats'][c],c); T[i]['catActual'][c][0]+= 1 if x==1 else (.5 if x==0 else 0); T[i]['catActual'][c][1]+=1
            T[i]['w']+=r==1; T[i]['l']+=r==0; T[i]['t']+=r==.5
            T[i]['apw']+=aw; T[i]['apl']+=al; T[i]['apt']+=at; T[i]['xw']+=appct[(wk,i)]
            T[i]['weeks'].append({'wk':wk,'opp':o,'cw':w,'cl':l,'ct':t,'r':r,'aw':aw,'al':al,'at':at})
    for i in ids:
        T[i]['oppStr']=round(st.mean(appct[(x['wk'],x['opp'])] for x in T[i]['weeks']),3)
    # schedule swap: row i plays col j's schedule
    swap=[]
    for i in ids:
        row=[]
        for j in ids:
            tot=0
            for wk in wks:
                o=weeks[wk][j]['opp']
                if o==i: o=j
                w,l,_=h2h(weeks[wk][i]['cats'],weeks[wk][o]['cats']); tot+=res(w,l)
            row.append(tot)
        swap.append(row)
    # close calls: decided by one category; find tightest category the winner took
    close=[]
    for wk in wks:
        W=weeks[wk]; sd={c:(st.pstdev([W[i]['cats'][c] for i in ids]) or 1) for _,c in CATS}
        for i in ids:
            o=W[i]['opp']; w,l,t=h2h(W[i]['cats'],W[o]['cats'])
            if w>l and w-l<=2:
                best=min(((abs(W[i]['cats'][c]-W[o]['cats'][c])/sd[c],c) for _,c in CATS if cmp(W[i]['cats'][c],W[o]['cats'][c],c)==1))
                c=best[1]
                close.append({'wk':wk,'win':i,'lose':o,'score':f'{w}-{l}'+(f'-{t}' if t else ''),'cat':c,'a':W[i]['cats'][c],'b':W[o]['cats'][c],'z':round(best[0],3),'flip':'loss' if w-l==1 else 'tie',
                  'winAP':round(appct[(wk,i)],3),'loseAP':round(appct[(wk,o)],3)})
    close.sort(key=lambda x:(x['z']))
    out=[]
    for i in ids:
        t=T[i]; t['xw']=round(t['xw'],2); t['wins']=t['w']+.5*t['t']; t['luck']=round(t['wins']-t['xw'],2)
        t['appct']=round((t['apw']+.5*t['apt'])/(t['apw']+t['apl']+t['apt']),3)
        t['cat']={c:round(v[0]/v[1],3) for c,v in t['cat'].items()}; t['catActual']={c:round(v[0]/v[1],3) for c,v in t['catActual'].items()}
        out.append(t)
    return {'label':label,'weeks':wks,'regWeeks':reg,'teams':out,'swap':swap,'close':close[:8],'cats':[c for _,c in CATS]}
data={'league':'NBA Europe','updated':__import__('datetime').date.today().isoformat(),'seasons':{'2027':season(2027,'2026-27'),'2026':season(2026,'2025-26')}}
json.dump(data,open('data.json','w'),separators=(',',':'))
for k,s in data['seasons'].items():
    print(k,s['label'],'weeks',s['weeks'][0],'-',s['weeks'][-1])
    for t in sorted(s['teams'],key=lambda t:-t['luck']): print(f"  {t['name'][:28]:28} {t['w']}-{t['l']}-{t['t']}  xW {t['xw']:5}  luck {t['luck']:+5}  AP {t['appct']}")
    print('  close:',[(c['wk'],c['score'],c['cat'],c['a'],c['b']) for c in s['close'][:4]])
