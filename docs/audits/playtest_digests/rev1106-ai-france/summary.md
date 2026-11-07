# AI-run France sweep (rev1106) - summary

Harness: tools/ai_france_sweep.py (untracked). Master ad73ba09. 40 turns, ambient K=10000, PYTHONHASHSEED=0, LLM_MODE=mock. Control: historical run twice -> byte-identical JSON (cmp). Arms: `main` (client petitions declined, rebellion popups accepted = the driver's defaults), `steward` (client petitions granted, rebellion -> invest), `ambient` (passive France, tools/ai_v_sweep.py).


## MAIN arm (driver-default answers)

| seed | prov T0/10/20/30/40 | men T10/20/30/40 | gold T40 | laws | sats T10/20/30/40 | France battles | Austria falls (turn) | other elims | at war T40 | ending |
|---|---|---|---|---|---|---|---|---|---|---|
| historical | 28/36/41/42/45 | 111k/80k/89k/98k | 17895 | 0 | 3/2/0/0 | 40 | no | Holland@33, KingdomOfItaly@33, Switzerland@35 | Austria, Russia | none |
| ulm | 28/37/43/45/50 | 123k/97k/112k/103k | 13279 | 0 | 3/3/0/0 | 40 | 10 | Hanover@34 | Britain, Holland, Russia, Sardinia, Sweden | none |
| austerlitz | 28/37/41/43/44 | 123k/103k/102k/112k | 19542 | 0 | 3/1/1/0 | 30 | 10 | Switzerland@32 | Britain, Russia | none |
| jena | 28/36/41/43/42 | 114k/88k/87k/104k | 18753 | 0 | 3/2/1/0 | 36 | 9 | Switzerland@32 | Hanover, Russia, Sardinia, Sweden | none |
| marengo | 28/35/39/43/42 | 124k/100k/90k/122k | 13951 | 0 | 3/1/0/0 | 37 | 12 | Switzerland@26 | KingdomOfItaly, Russia, Sardinia, Sweden | none |
| eylau | 28/35/40/45/45 | 109k/93k/99k/83k | 17543 | 0 | 3/3/0/0 | 47 | 17 | Switzerland@25 | Britain, Russia | none |
| friedland | 28/30/35/33/35 | 108k/93k/81k/102k | 11199 | 0 | 3/2/2/1 | 39 | no | KingdomOfItaly@36 | Austria, Britain | none |
| wagram | 28/35/41/45/45 | 93k/94k/100k/102k | 18745 | 0 | 3/3/1/0 | 45 | 9 | Switzerland@30 | Russia | none |
| lodi | 28/37/44/45/47 | 123k/126k/119k/105k | 20221 | 0 | 3/3/0/0 | 40 | 10 | Holland@33, Switzerland@35 | Britain, Russia | none |
| rivoli | 28/33/42/43/41 | 114k/80k/79k/88k | 12742 | 0 | 3/3/0/0 | 48 | 15 | Switzerland@26 | Hanover, Prussia, Russia, Sardinia, Sweden | none |

## STEWARD arm

| seed | prov T0/10/20/30/40 | men T10/20/30/40 | gold T40 | laws | sats T10/20/30/40 | France battles | Austria falls (turn) | other elims | at war T40 | ending |
|---|---|---|---|---|---|---|---|---|---|---|
| historical | 28/35/39/36/40 | 111k/79k/92k/122k | 17259 | 0 | 3/3/3/3 | 32 | 28 | - | Britain, Hanover, Russia, Sardinia, Sweden | none |
| ulm | 28/36/42/42/40 | 123k/97k/83k/100k | 16088 | 0 | 3/3/3/3 | 34 | 10 | - | Britain, Hanover, Russia, Sardinia, Sweden | none |
| austerlitz | 28/36/41/42/43 | 123k/107k/124k/136k | 17526 | 0 | 3/3/3/3 | 31 | 10 | - | Britain, Russia | none |
| jena | 28/35/39/39/36 | 111k/90k/79k/125k | 18605 | 0 | 3/3/3/3 | 41 | 9 | - | Britain, Hanover, Russia, Sardinia, Sweden | none |
| marengo | 28/34/38/40/44 | 129k/117k/96k/123k | 19365 | 0 | 3/3/3/3 | 44 | 12 | - | Britain, Russia, Sardinia, Sweden | none |
| eylau | 28/34/38/41/41 | 109k/92k/72k/96k | 20436 | 0 | 3/3/3/3 | 46 | 18 | - | Britain, Russia | none |
| friedland | 28/29/32/33/32 | 105k/81k/29k/119k | 15879 | 0 | 3/3/3/3 | 49 | 31 | Hanover@41 | Naples, Sardinia, Sweden | none |
| wagram | 28/34/39/42/42 | 93k/94k/99k/103k | 20154 | 0 | 3/3/3/3 | 44 | 9 | - | Russia | none |
| lodi | 28/36/43/43/43 | 123k/132k/120k/111k | 21665 | 0 | 3/3/3/3 | 29 | 10 | - | Russia | none |
| rivoli | 28/32/40/41/30 | 114k/82k/103k/87k | 11739 | 0 | 3/3/2/2 | 39 | 15 | Holland@31 | Hanover, Prussia, Russia, Sardinia, Sweden | none |

## AMBIENT (passive France) control

| seed | France strength T10/20/30/40 | authority T40 | campaign_ending (turn) | eliminations |
|---|---|---|---|---|
| historical | 115k/65k/0k/0k | 90 | (27, 'eagle_falls') | [[6, 'Bavaria'], [9, 'KingdomOfItaly']] |
| ulm | 169k/123k/65k/24k | 70 | (40, 'chains') | [[4, 'Bavaria'], [31, 'Switzerland'], [33, 'KingdomOfItaly']] |
| austerlitz | 169k/128k/70k/43k | 65 | (41, 'eagle_falls') | [[4, 'Bavaria'], [31, 'Switzerland']] |
| jena | 127k/101k/56k/0k | 55 | (41, 'soil_or_sword') | [[6, 'Bavaria'], [7, 'KingdomOfItaly'], [40, 'Holland']] |
| marengo | 173k/103k/65k/26k | 30 | none | [[4, 'Bavaria'], [21, 'KingdomOfItaly']] |
| eylau | 127k/83k/35k/26k | 90 | (36, 'soil_or_sword') | [[6, 'Bavaria'], [7, 'KingdomOfItaly']] |
| friedland | 97k/56k/33k/0k | 40 | (40, 'soil_or_sword') | [[13, 'KingdomOfItaly'], [38, 'Hanover']] |
| wagram | 115k/60k/16k/16k | 90 | (32, 'eagle_falls') | [[6, 'Bavaria'], [9, 'KingdomOfItaly']] |
| lodi | 169k/126k/77k/48k | 50 | none | [[4, 'Bavaria']] |
| rivoli | 127k/84k/8k/0k | 30 | (37, 'soil_or_sword') | [[6, 'Bavaria'], [7, 'KingdomOfItaly']] |

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
