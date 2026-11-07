import json
D='tools/playtest_runs/rev1106-ai-france'
seeds="historical ulm austerlitz jena marengo eylau friedland wagram lodi rivoli".split()
out=[]
out.append("# AI-run France sweep (rev1106) - summary\n")
out.append("Harness: tools/ai_france_sweep.py (untracked). Master ad73ba09. 40 turns, ambient K=10000, PYTHONHASHSEED=0, LLM_MODE=mock. Control: historical run twice -> byte-identical JSON (cmp). Arms: `main` (client petitions declined, rebellion popups accepted = the driver's defaults), `steward` (client petitions granted, rebellion -> invest), `ambient` (passive France, tools/ai_v_sweep.py).\n")
for tag,title in (('','MAIN arm (driver-default answers)'),('/steward','STEWARD arm')):
    out.append(f"\n## {title}\n")
    out.append("| seed | prov T0/10/20/30/40 | men T10/20/30/40 | gold T40 | laws | sats T10/20/30/40 | France battles | Austria falls (turn) | other elims | at war T40 | ending |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for s in seeds:
        d=json.load(open(f'{D}{tag}/{s}.json')); ser=d['france_series']
        g=lambda k,t: ser[t][k]
        el=d['derived']['eliminations']
        aus=[t for t,n in el if n=='Austria']; oth=[f"{n}@{t}" for t,n in el if n!='Austria']
        out.append(f"| {s} | {'/'.join(str(g('provinces',t)) for t in (0,10,20,30,40))} | {'/'.join(str(g('men',t)//1000)+'k' for t in (10,20,30,40))} | {g('gold',40)} | {g('laws',40)} | {'/'.join(str(len(g('satellites',t))) for t in (10,20,30,40))} | {d['france_battles']} | {aus[0] if aus else 'no'} | {', '.join(oth) or '-'} | {', '.join(g('at_war_with',40))} | {d['ending'] or 'none'} |")
out.append("\n## AMBIENT (passive France) control\n")
out.append("| seed | France strength T10/20/30/40 | authority T40 | campaign_ending (turn) | eliminations |")
out.append("|---|---|---|---|---|")
for s in seeds:
    a=json.load(open(f'{D}/ambient/{s}.json')); t=a['turns']
    ev=[(r['turn'],e.get('cause') or e.get('kind')) for r in t for e in r['events'] if e.get('type')=='campaign_ending']
    out.append(f"| {s} | {'/'.join(str((t[i-1]['strength'].get('France') or 0)//1000)+'k' for i in (10,20,30,40))} | {t[39]['authority']} | {ev[0] if ev else 'none'} | {a['derived']['eliminations']} |")
out.append("""
## Stories (main arm unless noted)

- historical: Vienna stormed T5 (as on 10/10 seeds); Austria survives as a rump to T40 (at war with France and Russia at T40); Napoleon walks Vienna -> Moravia -> Podolia -> Lithuania -> Vilna (T13-T24) and back; Holland and Italy (T33) and Switzerland (T35) are bribed away then eliminated; France ends 45 provinces, 98k men, 17.9k gold unspent, 0 laws; Britain armistice accepted T11 and T18.
- ulm: Austria eliminated T10, Napoleon reaches Finland by T40; Teulie captured T4; 50 provinces at T40 (the max), five wars open at T40; Hanover eliminated T34.
- austerlitz: Austria out T10; Switzerland eliminated T32; France 44 provinces, 19.5k gold, 0 laws; at war with Britain and Russia at T40.
- jena: Austria out T9; Lannes captured T8 and Murat T14; Switzerland out T32; 42 provinces at T40; at war with Hanover/Russia/Sardinia/Sweden.
- marengo: the only seed with 3 crisis_brewing beats and 2 crisis_passed; Murat and Lannes captured T19/T20; Napoleon ends at Piedmont; Austria out T12, Switzerland T26.
- eylau: Austria out T17; Bernadotte captured T41; 47 battles; Switzerland out T25; 45 provinces.
- friedland: the weakest France: 35 provinces, Austria never eliminated (alive and at war T40), 3 marshals captured (Lannes T9, Massena T24, Teulie T28); STEWARD arm: Napoleon TAKEN by Russia at Moravia T27 (last stand answered fight_to_the_last), France 29.8k men at T31, Russia peace and his release T32.
- wagram: Austria out T9; 13 'not enough actions' refusals (AP overspend); 45 provinces; at war with Russia alone at T40.
- lodi: Austria out T10; the strongest army (119-126k men T10-T30); Holland T33 and Switzerland T35 eliminated; 47 provinces.
- rivoli: 48 battles, Napoleon walks to Berlin/Brandenburg (T33-36) and Amsterdam in the v1 run; Austria out T15; 41 provinces at T40 (30 in the steward arm); at war with Hanover/Prussia/Russia/Sardinia/Sweden at T40.
""")
open(f'{D}/summary.md','w',encoding='utf-8').write("\n".join(out))
