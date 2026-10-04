import random

# Trivia tuples: question, choices, correct_index
TRIVIA = [
("Which animal has fingerprints so similar to humans they can potentially confuse forensic investigators?", ["Koala","Chimpanzee","Otter","Sloth"], 0),
("What was Viagra originally developed to treat?", ["High blood pressure/heart disease","Insomnia","Migraines","Ulcers"], 0),
("Which mammal is capable of true sustained flight?", ["Flying squirrel","Bat","Sugar glider","Colugo"], 1),
("Which planet has a day shorter than 10 hours?", ["Mars","Jupiter","Venus","Mercury"], 1),
("What is the only bone not connected to another bone?", ["Hyoid","Patella","Femur","Sternum"], 0),
("Which country gifted the Statue of Liberty to the U.S.?", ["France","Spain","Italy","Belgium"], 0),
("Which food is botanically a fruit but legally treated as a vegetable in U.S. tariff law?", ["Tomato","Cucumber","Pumpkin","Avocado"], 0),
("Which spice was once worth roughly its weight in gold in Europe?", ["Black pepper","Cinnamon","Paprika","Nutmeg"], 0),
("Which ancient civilization used crocodile dung in contraceptive recipes?", ["Egyptian","Roman","Viking","Mayan"], 0),
("Which organ can regenerate a significant portion of itself?", ["Liver","Heart","Pancreas","Lung"], 0),
("Which animal has three hearts?", ["Shark","Octopus","Dolphin","Horse"], 1),
("Which famous painting has been stolen multiple times?", ["The Scream","The Starry Night","American Gothic","Guernica"], 0),
("Which planet may have diamond rain deep in its atmosphere?", ["Neptune","Mars","Mercury","Earth"], 0),
("What is the smallest prime number?", ["0","1","2","3"], 2),
("Which band released Bohemian Rhapsody?", ["Queen","ABBA","The Beatles","Fleetwood Mac"], 0),
("What year did the Titanic sink?", ["1905","1912","1918","1923"], 1),
("Which U.S. state was first to legalize recreational cannabis?", ["Colorado","California","Washington","Oregon"], 0),
("What does the G in G-spot stand for?", ["Gräfenberg","Galen","Galileo","Goodman"], 0),
("Which hormone is strongly associated with bonding after orgasm?", ["Oxytocin","Cortisol","Melatonin","Insulin"], 0),
("Which animal has been observed masturbating?", ["Dolphins","Cows","Penguins","All of these"], 3),
("What is the world's most stolen food?", ["Cheese","Chocolate","Bread","Avocados"], 0),
("Which country is often cited for highest chocolate consumption per person?", ["Switzerland","United States","Japan","Brazil"], 0),
("Which sense is especially tied to memory and attraction?", ["Smell","Hearing","Touch","Taste"], 0),
("Which of these was NOT originally marketed as a medical treatment?", ["Cocaine","Heroin","Viagra","Aspirin"], 3),
("Which historical figure was famously buried with a large quantity of alcohol?", ["Alexander the Great","Genghis Khan","William Shakespeare","Benjamin Franklin"], 3),
("Which animal is famous for forming long-term same-sex pair bonds?", ["Penguins","Giraffes","Swans","All of these"], 3),
("Which neurotransmitter is heavily involved in early romantic attraction?", ["Dopamine","GABA","Insulin","Histamine"], 0),
("Which historical contraceptive ingredient came from a plant called silphium?", ["Silphium resin","Vanilla","Peppermint","Sage"], 0),
("Which factor is repeatedly linked with lower libido?", ["Chronic stress","Good sleep","Exercise","Feeling safe"], 0),
("Which common medication class can reduce sexual desire as a side effect?", ["Some antidepressants","Vitamin C","Antacids","Saline"], 0),
]

DIRTY_TRIVIA = [
("What is a commonly reported reason couples give for having less sex?", ["Stress/fatigue","Boredom","Money","Bad breath"], 0),
("Which body part has an unusually high concentration of touch receptors?", ["Fingertips","Elbows","Shins","Shoulder blades"], 0),
("Which hormone is associated with orgasm and social bonding?", ["Oxytocin","Adrenaline","Thyroxine","Glucagon"], 0),
("Which fantasy appears commonly in adult sexuality surveys?", ["Trying a threesome","Sex in public","Being tied up","All of these"], 3),
("Which sense can trigger strong attraction and memory with little conscious processing?", ["Smell","Sight","Hearing","Balance"], 0),
("What was the original medical target of sildenafil, later sold as Viagra?", ["Cardiovascular conditions","Depression","Arthritis","Asthma"], 0),
("Which part of the brain is strongly involved in reward and romantic obsession?", ["Dopamine reward circuitry","Cerebellum only","Brainstem only","Spinal cord"], 0),
("Which of these is a real historical use of cocaine?", ["Early Coca-Cola ingredient","Anesthetic","Toothache medicine","All of these"], 3),
("Which animal is famous for an unusually large penis relative to body size?", ["Barnacle","Elephant","Blue whale","Gorilla"], 0),
("Which common drug can reduce sexual desire as a side effect?", ["Some antidepressants","Vitamin C","Antacids","Saline"], 0),
]

WHO = """Who would accidentally send a nude to their boss?
Who would sleep with their ex and immediately regret it?
Who would sleep with their ex and absolutely NOT regret it?
Who would get caught having sex somewhere they absolutely should not?
Who would have the weirdest search history?
Who would survive a threesome?
Who would absolutely NOT survive a threesome?
Who would fall in love after one hookup?
Who would ghost someone and then be offended when they get ghosted?
Who would have a secret sugar daddy or sugar mommy?
Who would date someone solely because they're hot?
Who would marry for money?
Who would fake an orgasm?
Who would lie about their body count?
Who would have the most embarrassing sex story?
Who would get arrested on vacation?
Who would hook up with a celebrity if given the opportunity?
Who would accidentally sleep with two people in the same friend group?
Who would be the best stripper?
Who would be the worst stripper?
Who would have a secret kink nobody knows about?
Who is most likely to actually have a sex dungeon?
Who would send a risky text and immediately throw their phone across the room?
Who would stalk an ex's new partner?
Who would fall for a scam because the scammer was hot?
Who would say 'it's complicated' about a relationship?
Who would get back together with someone everyone hates?
Who would hook up with someone they met tonight?
Who would get caught lying about where they were last night?
Who would say 'I'm never drinking again' and drink again tomorrow?
Who would disappear at a party and return three hours later with no explanation?
Who would have a completely different personality in bed?
Who would be the easiest person in this room to seduce?
Who would be most likely to have a fake Instagram account?
Who would have the most suspicious work trip?
Who would be first to join a reality dating show?
Who would get kicked off a reality dating show for fighting?
Who would accidentally reveal someone's secret?
Who would somehow become famous for something embarrassing?
Who would you trust least with your unlocked phone?
Who would be most likely to get banned from a casino?
Who would survive a zombie apocalypse purely through dumb luck?
Who would become a cult leader by accident?
Who would absolutely say 'I can fix him' and try?
Who would send a text meant for their best friend to their crush?
Who would get married in Vegas after knowing someone for 72 hours?
Who would be most likely to have a secret OnlyFans?
Who would get away with murder because nobody would suspect them?
Who would flirt their way out of a parking ticket?
Who would hook up with someone they absolutely should not?""".splitlines()

FUNNY = """Your date goes to the bathroom and never comes back. What's the most likely reason?
You're on a first date. Everything is going perfectly until they casually mention ______.
What's the worst possible thing to hear immediately after a one-night stand?
Your FBI agent quits because of your browser history. What was the final search?
What's the worst possible thing your Uber driver could say before you get out?
You wake up next to someone you don't remember meeting. What's the first thing you say?
Your friend says, 'Promise you won't judge me.' What are they about to confess?
What's the worst possible thing to find in someone's nightstand?
Your hookup texts 'we need to talk.' What did you do?
What's the worst possible tattoo to discover your partner has?
You accidentally like a photo from 2018 while stalking someone. What's your recovery strategy?
Your boss texts 'We need to talk' at 11:47 p.m. What is the worst possible reason?
Your Uber driver says, 'You're the third person I've picked up from this house tonight.' What happened?
What's the worst possible name for a sex toy?
Your ex gets one sentence at your funeral. What do they say?
Your dating profile has to include one completely honest sentence. What does it say?
What's the worst thing someone could whisper in your ear at a wedding?
You have to describe your sex life using the title of a children's movie. Which one?
What's the worst possible thing to hear from the bathroom at a house party?
Someone you're flirting with says, 'My partner won't mind.' What is your response?
Your friend hands you their phone and says, 'Delete anything suspicious.' What do you find?
You are arrested. Your friends know exactly why. What did you do?
What's the worst thing someone could say immediately before 'Trust me'?
Your date says, 'I have something to confess.' What's your worst-case scenario?
What's something you'd absolutely never admit to your parents?
What's the most chaotic text currently in your phone?
What is a red flag you have that you personally refuse to consider a red flag?
What's the most embarrassing thing you've done because you liked someone?
What's the worst decision you've made because you were horny?
If your sex life had a Yelp review, what would the headline be?""".splitlines()

SABOTAGE = """STEAL 200 POINTS: Take them from the person most likely to have cheated on a test.
CURSE SOMEONE: Pick a player. Their next correct trivia answer is worth half points.
PUBLIC ENEMY: Pick a player to lose 150 points.
TAX THE RICH: Pick the current leader. They lose 200 points.
REVENGE: Pick someone who has voted for you before. They lose 100 points.
HUMBLE THEM: Take 100 points from the player with the most confidence.
THROW THEM UNDER THE BUS: Pick who you would trust least with your phone unlocked. They lose 150.
THE CURSE: Choose someone. If they get the next trivia question right, you get 100 points.
POOR DECISION: The player in last place may steal 150 points from anyone.
MUTUAL DESTRUCTION: Choose someone. You both risk 200 points on the next trivia question.
CHAOS BUTTON: Everyone votes for one player to lose 50 points.
EX-FRIEND: Pick someone you would least want as a roommate. They lose 100 points.
VILLAIN ARC: Pick someone. They must answer the next question before everyone else.
UNPOPULAR OPINION: Pick someone to lose 100 points because you simply don't like their vibe.
KARMA: Give 100 points to the player who has annoyed you the least. Yes, that's the rule.""".splitlines()

CHAOS = """What's the worst possible thing to hear immediately after sex?
Your FBI agent has finally quit because of your browser history. What was the search that broke them?
You're on a first date and your date says, 'My mom has your number.' Explain.
You wake up famous. What incredibly stupid thing are you famous for?
What's the worst possible thing to discover about someone after you've already slept with them?
Your ex gets one final text before you block them. What does it say?
Your friend asks you to lie about where they were last night. What is the lie?
What's the worst thing your hookup could say immediately afterward?
You're meeting someone's parents. What's the worst possible thing they could say?
What's the worst possible thing to find in a stranger's bathroom?
You have to explain your browser history to a judge. Which search gets you convicted?
What's the worst possible thing to hear from a bathroom at a house party?
You have to describe your last situationship in five words or fewer.
What's your biggest red flag if we're being brutally honest?
What's the most irrational sexual turn-on you can admit to?
What's the most irrational sexual turn-off you can admit to?
What's the most embarrassing thing you've done because you liked someone?
What would your ex say is your biggest problem?
What's your 'I absolutely should have known better' story?
Describe your dating history as a movie title.""".splitlines()

FINAL = """What's something you'd absolutely never tell your parents?
Describe your dating history as a movie title.
Describe your last situationship in five words or fewer.
What's your biggest red flag if we're being brutally honest?
What's the most embarrassing thing you've done because you liked someone?
What's the worst decision you've made because you were horny?
What's one thing you would change about your dating life if nobody could judge you?
What's the most chaotic text currently in your phone?
What would your ex say is your biggest problem?
What's your 'I absolutely should have known better' story?
If your sex life had a Yelp review, what would the headline be?
What's something you've done that you hope nobody in this room ever finds out about?
What's a red flag you have that you personally refuse to consider a red flag?
What is your most irrational sexual turn-on?
What is your most irrational sexual turn-off?
What's the lie you've told most often while dating?""".splitlines()

TRANSITIONS = {
"lobby":["Gather your degenerates.","Waiting for the rest of the bad decisions…","Someone invite that friend who knows way too much.","The group chat has become a game.","Please ensure everyone has accepted that friendships may be damaged."],
"trivia":["Consulting the Council of Bad Ideas…","Googling something you definitely shouldn't know.","Selecting your next opportunity to embarrass yourself.","Time to find out who actually knows things.","Your useless knowledge has entered the chat."],
"who":["TIME TO JUDGE EACH OTHER.","Friendship is about to become significantly more complicated.","Please vote responsibly. Or don't.","This is your opportunity to weaponize your opinions.","Think carefully. They'll remember this."],
"sabotage":["WELCOME TO THE PART WHERE WE STOP PRETENDING TO LIKE EACH OTHER.","Choose violence. Strategically.","Someone's score is about to have a really bad day.","The Geneva Convention does not apply here.","Friendship was a mistake anyway."],
"funny":["Your dignity is optional.","Time to type something you'll regret.","Comedy is subjective. Your friends are not.","Make us laugh. No pressure.","Someone in this room is about to reveal too much."],
"final":["THIS IS IT.","Everything you've done up to this point has led to this stupid little moment.","Time to ruin the leaderboard.","Your dignity is already gone. You might as well win.","The final opportunity to make everyone question your character."]}
OUTCOMES=["Friendship status: questionable.","That was personal.","We have notified their therapist.","They'll remember this.","Absolutely devastating.","Nobody needed to know that.","The room has spoken.","That felt unnecessarily targeted.","This group needs supervision.","We are learning a lot about you people."]

def unused(pool, used):
    available=[i for i in range(len(pool)) if i not in used]
    if not available:
        used.clear(); available=list(range(len(pool)))
    i=random.choice(available); used.add(i); return pool[i]
