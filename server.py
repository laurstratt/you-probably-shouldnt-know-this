import asyncio, json, os, random, string
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import websockets

PORT = int(os.environ.get("PORT", "8765"))
PUBLIC = Path(__file__).parent / "public"
rooms = {}

GENERAL = [
    {"q":"Which planet has the shortest day?","a":["Jupiter","Mars","Mercury","Venus"],"correct":0,"cat":"SCIENCE"},
    {"q":"What is the only mammal capable of true flight?","a":["Flying squirrel","Bat","Sugar glider","Lemur"],"correct":1,"cat":"NATURE"},
    {"q":"Which cocktail traditionally contains vodka, coffee liqueur, and cream?","a":["White Russian","Moscow Mule","Espresso Martini","Mudslide"],"correct":0,"cat":"FOOD & DRINK"},
    {"q":"Which U.S. state was the first to legalize recreational cannabis?","a":["Colorado","California","Washington","Oregon"],"correct":0,"cat":"U.S."},
    {"q":"Who painted The Starry Night?","a":["Claude Monet","Pablo Picasso","Vincent van Gogh","Salvador Dalí"],"correct":2,"cat":"ART"},
    {"q":"What is the largest ocean on Earth?","a":["Atlantic","Indian","Pacific","Arctic"],"correct":2,"cat":"WORLD"},
    {"q":"What year did the Titanic sink?","a":["1905","1912","1918","1923"],"correct":1,"cat":"HISTORY"},
    {"q":"Which band released Bohemian Rhapsody?","a":["The Beatles","Queen","ABBA","Fleetwood Mac"],"correct":1,"cat":"MUSIC"},
    {"q":"What is the capital of Australia?","a":["Sydney","Melbourne","Canberra","Perth"],"correct":2,"cat":"WORLD"},
    {"q":"Which element has the chemical symbol Au?","a":["Silver","Gold","Copper","Argon"],"correct":1,"cat":"SCIENCE"},
    {"q":"How many hearts does an octopus have?","a":["1","2","3","8"],"correct":2,"cat":"NATURE"},
    {"q":"Which movie features the quote, \"I'll be back\"?","a":["Rocky","The Terminator","Die Hard","Predator"],"correct":1,"cat":"MOVIES"},
    {"q":"What is the smallest prime number?","a":["0","1","2","3"],"correct":2,"cat":"KNOW YOUR SHIT"},
    {"q":"Which country gifted the Statue of Liberty to the United States?","a":["France","Spain","Italy","England"],"correct":0,"cat":"HISTORY"},
    {"q":"What does HTTP stand for?","a":["HyperText Transfer Protocol","High Transfer Text Process","Hyperlink Text Transfer Program","Host Transfer Type Protocol"],"correct":0,"cat":"TECH"},
]

ADULT = [
    {"q":"Which body part is most commonly associated with a \"Brazilian\" wax?","a":["Eyebrows","Legs","Bikini area","Back"],"correct":2,"cat":"SPICY"},
    {"q":"Which of these is a real cocktail?","a":["Naked and Famous","Tipsy Unicorn","Drunk History","Bad Decision"],"correct":0,"cat":"SPICY"},
    {"q":"Which phrase is most likely to precede a regrettable 2 a.m. text?","a":["Just checking in","You up?","Hope you're well","Quick question"],"correct":1,"cat":"SPICY"},
    {"q":"Which party game is most famous for fill-in-the-blank adult humor?","a":["Scrabble","Cards Against Humanity","Clue","Risk"],"correct":1,"cat":"TRIVIA"},
    {"q":"What is the unofficial rule about texting an ex after midnight?","a":["It's encouraged","Only on weekends","Absolutely not","Only with emojis"],"correct":2,"cat":"QUESTIONABLE"},
]

FUNNY = [
    {"q":"You have to fake a skill for a job interview. What are you claiming you can do?","a":["Speak fluent dolphin","Juggle","Fix a transmission","Read minds"],"correct":None,"cat":"QUESTIONABLE CHOICES"},
    {"q":"Your FBI agent is watching your browser history. What are they most concerned about?","a":["The 2,000 searches","The weird hours","The shopping cart","All of it"],"correct":None,"cat":"QUESTIONABLE CHOICES"},
    {"q":"What is the worst thing to hear immediately after saying \"trust me\"?","a":["Absolutely","I don't","We already called them","Too late"],"correct":None,"cat":"QUESTIONABLE CHOICES"},
    {"q":"Which is the most suspicious thing to have 47 tabs open for?","a":["Recipes","Flights","Wikipedia","A breakup"],"correct":None,"cat":"QUESTIONABLE CHOICES"},
]

WHO = [
    {"q":"Who in this room would survive the longest in a zombie apocalypse?","cat":"WHO WOULD?"},
    {"q":"Who is most likely to accidentally start a cult?","cat":"WHO WOULD?"},
    {"q":"Who would be most likely to text their ex tonight?","cat":"WHO WOULD?"},
    {"q":"Who would absolutely thrive on a reality TV show?","cat":"WHO WOULD?"},
    {"q":"Who is most likely to say \"I know a guy\" and actually know a guy?","cat":"WHO WOULD?"},
]

CHAOS = [
    {"kind":"boost","title":"GIFT FROM THE GARBAGE GODS","text":"Gain 150 points. Don't question it.","amount":150},
    {"kind":"boost","title":"MAIN CHARACTER ENERGY","text":"Gain 200 points. Enjoy your moment.","amount":200},
    {"kind":"curse","title":"THE UNIVERSE HATES YOU","text":"Lose 100 points. We don't make the rules.","amount":-100},
    {"kind":"curse","title":"QUESTIONABLE CHOICES","text":"Lose 150 points. It felt right.","amount":-150},
]

ROUND_TYPES = ["trivia","funny","speed","who","chaos","wager","funny","final"]

class Room:
    def __init__(self, code):
        self.code=code; self.players={}; self.host=None; self.round=0; self.question=None; self.answers={}; self.votes={}; self.wager={}; self.state="lobby"; self.used=set(); self.timer_task=None
    def payload(self):
        return {"type":"state","code":self.code,"state":self.state,"round":self.round,"total":len(ROUND_TYPES),"players":[{"id":p["id"],"name":p["name"],"score":p["score"],"host":p["id"]==self.host} for p in self.players.values()],"question":self.question}

def code():
    return ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(6))

def pick(items):
    available=[x for i,x in enumerate(items) if i not in []]
    return random.choice(available)

async def broadcast(room):
    msg=json.dumps(room.payload())
    dead=[]
    for p in room.players.values():
        ws=p.get("ws")
        if ws:
            try: await ws.send(msg)
            except: dead.append(p["id"])
    for pid in dead: room.players.pop(pid,None)

def round_question(room):
    typ=ROUND_TYPES[room.round]
    if typ in ("trivia","speed","wager","final"):
        pool=GENERAL + (ADULT if random.random()<0.65 else [])
        q=random.choice(pool).copy(); q["type"]=typ; q["promptType"]="trivia"
        return q
    if typ=="funny":
        q=random.choice(FUNNY).copy(); q["type"]=typ; q["promptType"]="funny"; return q
    if typ=="who":
        q=random.choice(WHO).copy(); q["type"]=typ; q["promptType"]="who"; return q
    if typ=="chaos":
        q=random.choice(CHAOS).copy(); q["type"]=typ; q["promptType"]="chaos"; return q

async def start_round(room):
    room.state="playing"; room.answers={}; room.votes={}; room.wager={}; room.question=round_question(room); await broadcast(room)
    duration=12 if room.question["type"]=="speed" else 25
    if room.question["type"]=="chaos":
        await asyncio.sleep(4); await resolve(room)
    else:
        await asyncio.sleep(duration); await resolve(room)

async def resolve(room):
    if room.state not in ("playing","wagering"): return
    q=room.question; typ=q["type"]
    if typ=="trivia" or typ=="speed":
        for pid,ans in room.answers.items():
            p=room.players.get(pid)
            if p and ans==q.get("correct"):
                p["score"] += 200 if typ=="trivia" else max(50, 300 - int(ans.get("elapsed",0)*10) if isinstance(ans,dict) else 150)
    elif typ=="wager" or typ=="final":
        for pid,ans in room.answers.items():
            p=room.players.get(pid)
            if p:
                w=max(0,min(p["score"],room.wager.get(pid,0)))
                if ans==q.get("correct"): p["score"] += w
                else: p["score"] -= w
    elif typ=="who":
        counts={}
        for target in room.votes.values(): counts[target]=counts.get(target,0)+1
        if counts:
            winner=max(counts,key=counts.get); p=room.players.get(winner)
            if p: p["score"] += 100
    elif typ=="chaos":
        for p in room.players.values():
            if q["kind"] in ("boost","curse"): p["score"] += q["amount"]
    room.state="results"; await broadcast(room)
    await asyncio.sleep(5)
    if room.round+1 >= len(ROUND_TYPES):
        room.state="finished"; room.question=None; await broadcast(room)
    else:
        room.round += 1; await start_round(room)

async def handler(ws):
    room=None; pid=None
    try:
        async for raw in ws:
            data=json.loads(raw); typ=data.get("type")
            if typ=="create":
                c=code()
                while c in rooms: c=code()
                room=rooms[c]=Room(c); pid='p'+''.join(random.choices(string.ascii_lowercase+string.digits,k=8)); name=(data.get("name") or "Player").strip()[:18]
                room.players[pid]={"id":pid,"name":name,"score":0,"ws":ws}; room.host=pid; await broadcast(room)
            elif typ=="join":
                c=data.get("code","").upper().strip(); room=rooms.get(c)
                if not room: await ws.send(json.dumps({"type":"error","message":"Room not found."})); continue
                if len(room.players)>=8: await ws.send(json.dumps({"type":"error","message":"Room is full."})); continue
                pid='p'+''.join(random.choices(string.ascii_lowercase+string.digits,k=8)); name=(data.get("name") or "Player").strip()[:18]
                if any(p["name"].lower()==name.lower() for p in room.players.values()): name += " " + str(len(room.players)+1)
                room.players[pid]={"id":pid,"name":name,"score":0,"ws":ws}; await broadcast(room)
            elif typ=="start" and room and pid==room.host and room.state=="lobby" and len(room.players)>=2:
                room.round=0; await start_round(room)
            elif typ=="answer" and room and room.state=="playing":
                if pid not in room.answers: room.answers[pid]=data.get("answer"); await ws.send(json.dumps({"type":"locked"}))
            elif typ=="wager" and room and room.state=="playing" and room.question and room.question["type"] in ("wager","final"):
                room.wager[pid]=max(0,min(int(data.get("amount",0)),room.players[pid]["score"])); room.state="playing"; await ws.send(json.dumps({"type":"wagerLocked","amount":room.wager[pid]}))
            elif typ=="vote" and room and room.state=="playing" and room.question and room.question["type"]=="who":
                target=data.get("target");
                if target in room.players: room.votes[pid]=target; await ws.send(json.dumps({"type":"locked"}))
            elif typ=="again" and room and room.state=="finished" and pid==room.host:
                for p in room.players.values(): p["score"]=0
                room.round=0; await start_round(room)
    except Exception:
        pass
    finally:
        if room and pid and pid in room.players:
            room.players[pid]["ws"]=None
            if not any(p.get("ws") for p in room.players.values()): rooms.pop(room.code,None)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/health": self.send_response(200); self.end_headers(); self.wfile.write(b"ok"); return
        if path=="/": path="/index.html"
        file=PUBLIC / path.lstrip("/")
        if file.exists() and file.is_file():
            self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.end_headers(); self.wfile.write(file.read_bytes())
        else: self.send_response(404); self.end_headers()

def http_server():
    ThreadingHTTPServer(("0.0.0.0",PORT),Handler).serve_forever()

async def main():
    loop=asyncio.get_running_loop(); await loop.run_in_executor(None,http_server); await asyncio.Future()

if __name__=="__main__":
    asyncio.run(main())
