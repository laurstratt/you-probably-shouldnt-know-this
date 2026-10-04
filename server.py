import asyncio,json,os,random,string
from pathlib import Path
import websockets
from game_data import TRIVIA,DIRTY_TRIVIA,WHO,FUNNY,SABOTAGE,CHAOS,FINAL,TRANSITIONS,OUTCOMES

PORT=int(os.environ.get('PORT','8765')); PUBLIC=Path(__file__).parent/'public'; rooms={}
ROUND_TYPES=['trivia','who','funny','sabotage','dirty','who','chaos','final']
ROUND_NAMES=['KNOW YOUR SHIT','WHO WOULD?','QUESTIONABLE CHOICES','SABOTAGE','DIRTY TRIVIA','WHO WOULD?','UNHINGED','FINAL CHAOS']

class Room:
 def __init__(self,code):
  self.code=code;self.players={};self.host=None;self.round=0;self.state='lobby';self.phase='lobby';self.question=None;self.answers={};self.votes={};self.used={k:set() for k in ['trivia','dirty','who','funny','sabotage','chaos','final']};self.transition='Gather your degenerates.';self.result='';self.result_detail='';self.timer=0
 def payload(self):
  return {'type':'state','code':self.code,'state':self.state,'phase':self.phase,'round':self.round,'total':len(ROUND_TYPES),'roundName':ROUND_NAMES[self.round] if self.round<len(ROUND_NAMES) else 'FINAL CHAOS','players':[{'id':p['id'],'name':p['name'],'score':p['score'],'host':p['id']==self.host} for p in self.players.values()],'question':self.question,'transition':self.transition,'result':self.result,'resultDetail':self.result_detail,'timer':self.timer}

def make_code(): return ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(6))
def pid(): return 'p'+''.join(random.choices(string.ascii_lowercase+string.digits,k=8))
def choose(pool,used):
 a=[i for i in range(len(pool)) if i not in used]
 if not a: used.clear();a=list(range(len(pool)))
 i=random.choice(a);used.add(i);return pool[i]

def transition(room,key):
 room.transition=random.choice(TRANSITIONS.get(key,TRANSITIONS['trivia']))

def question_for(room):
 typ=ROUND_TYPES[room.round]
 if typ=='trivia' or typ=='dirty':
  pool=TRIVIA if typ=='trivia' else DIRTY_TRIVIA
  q,a,c=choose(pool,room.used[typ]);return {'type':typ,'promptType':'trivia','cat':'KNOW YOUR SHIT' if typ=='trivia' else 'DIRTY TRIVIA','q':q,'a':a,'correct':c,'instructions':'Correct answer = +200 points. Wrong answer = 0.'}
 if typ=='who':
  q=choose(WHO,room.used['who']);return {'type':'who','promptType':'who','cat':'WHO WOULD?','q':q,'instructions':'Vote for ONE other player. Most votes = +250. Unanimous = +350. You cannot vote for yourself.'}
 if typ=='funny':
  q=choose(FUNNY,room.used['funny']);return {'type':'funny','promptType':'text','cat':'QUESTIONABLE CHOICES','q':q,'instructions':'Type your funniest answer. Then the room votes. Winner = +300. Runner-up = +150.'}
 if typ=='sabotage':
  q=choose(SABOTAGE,room.used['sabotage']);return {'type':'sabotage','promptType':'sabotage','cat':'SABOTAGE','q':q,'instructions':'Pick a target. The most-targeted player loses the listed points. The rest of the room will judge your choices.'}
 if typ=='chaos':
  q=choose(CHAOS,room.used['chaos']);return {'type':'chaos','promptType':'text','cat':'UNHINGED','q':q,'instructions':'Type your answer. Then vote for the funniest. Winner = +300. Runner-up = +150.'}
 q=choose(FINAL,room.used['final']);return {'type':'final','promptType':'text','cat':'FINAL CHAOS','q':q,'instructions':'FINAL ROUND: type your answer. Everyone votes. Winner = +500. Runner-up = +250. Last place gets a +100 desperation bonus.'}

async def broadcast(r):
 msg=json.dumps(r.payload());dead=[]
 for p in list(r.players.values()):
  ws=p.get('ws')
  if ws:
   try: await ws.send(msg)
   except: dead.append(p['id'])
 for x in dead:r.players.pop(x,None)

def award_text(r):
 return random.choice(OUTCOMES)

async def start_round(r):
 r.state='playing';r.phase='answering';r.answers={};r.votes={};r.result='';r.result_detail='';r.question=question_for(r);transition(r,ROUND_TYPES[r.round] if ROUND_TYPES[r.round] in TRANSITIONS else 'trivia');r.timer=12 if r.question['type'] in ('trivia','dirty') else 14
 await broadcast(r)
 await asyncio.sleep(r.timer)
 if r.state=='playing': await resolve(r)

async def resolve(r):
 if r.state!='playing':return
 q=r.question;typ=q['type']
 if typ in ('trivia','dirty'):
  correct=[r.players[pid] for pid,a in r.answers.items() if a==q['correct'] and pid in r.players]
  for p in correct:p['score']+=200
  r.result=f'{len(correct)} player(s) got it right.';r.result_detail='Correct = +200. Wrong = 0.'
 elif typ=='who': await start_voting(r);return
 elif typ in ('funny','chaos','final'): await start_voting(r);return
 elif typ=='sabotage':
  counts={x:0 for x in r.players}
  for target in r.answers.values():
   if target in counts:counts[target]+=1
  if counts:
   mx=max(counts.values());targets=[x for x,n in counts.items() if n==mx]
   if len(targets)==1:
    loss=200 if '200' in q['q'] else 150; r.players[targets[0]]['score']-=loss;r.result=f"{r.players[targets[0]]['name']} got absolutely sabotaged.";r.result_detail=f'-{loss} points. Choose your enemies carefully.'
   else:r.result='A beautiful tie in terrible decision-making.';r.result_detail='No sabotage points changed.'
  else:r.result='Nobody chose violence.';r.result_detail='Cowards. No points changed.'
 await finish_round(r)

async def start_voting(r):
 r.phase='voting';r.timer=10
 if r.question['type'] in ('funny','chaos','final'):
  r.result='SUBMISSIONS ARE IN.';r.result_detail='Vote for the answer that made you laugh hardest. You cannot vote for yourself.'
 else:
  r.result='TIME TO JUDGE EACH OTHER.';r.result_detail=r.question['instructions']
 await broadcast(r);await asyncio.sleep(10)
 if r.state=='playing':await resolve_votes(r)

async def resolve_votes(r):
 q=r.question;counts={}
 for target in r.votes.values():counts[target]=counts.get(target,0)+1
 if not counts:
  r.result='Nobody voted. Bold choice.';r.result_detail='No points awarded.'
  await finish_round(r);return
 ranked=sorted(counts.items(),key=lambda x:x[1],reverse=True)
 typ=q['type']
 if typ=='who':
  top=ranked[0][1];winners=[x for x,n in ranked if n==top]
  if len(winners)==1:r.players[winners[0]]['score']+=350 if top==len(r.players) else 250;r.result=f"{r.players[winners[0]]['name']} got {top} vote(s).";r.result_detail=f"+{350 if top==len(r.players) else 250} points." 
  else:r.result='A tie. Nobody is safe.';r.result_detail='No Who Would points awarded on a tie.'
 else:
  first=ranked[0][0];r.players[first]['score']+=500 if typ=='final' else 300
  if len(ranked)>1:r.players[ranked[1][0]]['score']+=250 if typ=='final' else 150
  if typ=='final':
   last=min(r.players,key=lambda x:r.players[x]['score']);r.players[last]['score']+=100;r.result=f"{r.players[first]['name']} won FINAL CHAOS.";r.result_detail='+500 winner, +250 runner-up, +100 desperation bonus.'
  else:r.result=f"{r.players[first]['name']} won the room's vote.";r.result_detail=f"+{500 if typ=='final' else 300} winner; runner-up gets +{250 if typ=='final' else 150}."
 await finish_round(r)

async def finish_round(r):
 r.phase='results';r.transition=award_text(r);await broadcast(r);await asyncio.sleep(3)
 if r.round+1>=len(ROUND_TYPES):r.state='finished';r.phase='finished';r.question=None;r.transition='And the winner is…';await broadcast(r)
 else:r.round+=1;await start_round(r)

async def handler(ws):
 room=None;me=None
 try:
  async for raw in ws:
   d=json.loads(raw);t=d.get('type')
   if t=='create':
    c=make_code()
    while c in rooms:c=make_code()
    room=rooms[c]=Room(c);me=pid();room.host=me;room.players[me]={'id':me,'name':(d.get('name') or 'Player').strip()[:18],'score':0,'ws':ws};await broadcast(room)
   elif t=='join':
    room=rooms.get(str(d.get('code','')).upper().strip())
    if not room:await ws.send(json.dumps({'type':'error','message':'Room not found.'}));continue
    if len(room.players)>=8:await ws.send(json.dumps({'type':'error','message':'Room is full.'}));continue
    me=pid();name=(d.get('name') or 'Player').strip()[:18]
    if any(p['name'].lower()==name.lower() for p in room.players.values()):name=f'{name} {len(room.players)+1}'
    room.players[me]={'id':me,'name':name,'score':0,'ws':ws};await broadcast(room)
   elif t=='start' and room and me==room.host and room.state=='lobby' and len(room.players)>=2:room.round=0;await start_round(room)
   elif t=='answer' and room and room.state=='playing' and room.phase=='answering':
    if me not in room.answers:room.answers[me]=d.get('answer');await ws.send(json.dumps({'type':'locked'}))
   elif t=='text' and room and room.state=='playing' and room.phase=='answering':
    if me not in room.answers:room.answers[me]=str(d.get('text',''))[:240];await ws.send(json.dumps({'type':'locked'}))
   elif t=='vote' and room and room.state=='playing' and room.phase=='voting':
    target=d.get('target')
    if target in room.players and target!=me and me not in room.votes:room.votes[me]=target;await ws.send(json.dumps({'type':'locked'}))
   elif t=='sabotage' and room and room.state=='playing' and room.question and room.question['type']=='sabotage' and room.phase=='answering':
    target=d.get('target')
    if target in room.players and target!=me and me not in room.answers:room.answers[me]=target;await ws.send(json.dumps({'type':'locked'}))
   elif t=='again' and room and room.state=='finished' and me==room.host:
    for p in room.players.values():p['score']=0
    room.round=0;room.used={k:set() for k in room.used};await start_round(room)
 except Exception:pass
 finally:
  if room and me in room.players:
   room.players[me]['ws']=None
   if not any(p.get('ws') for p in room.players.values()):rooms.pop(room.code,None)
