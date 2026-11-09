# -*- coding: utf-8 -*-
"""English versions of the AURZANE tests, using the original validated English wording of each scale.
Output: publicar/mind.aurzane.com/en/<slug>/index.html and publicar/mind.aurzane.com/en/index.html
Usage: python3 tests_en/gen.py
Only scales whose authors allow free use are included (GAD-7, PHQ-9, RSES, SWLS, BRS, GSE)."""
import json, os, html

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(R, 'publicar', 'mind.aurzane.com', 'en')
BASE = 'https://mind.aurzane.com/en/'
E = lambda s: html.escape(str(s), quote=True)

FREQ = [[0, 'Not at all'], [1, 'Several days'], [2, 'More than half the days'], [3, 'Nearly every day']]
TESTS = [
 dict(slug='anxiety-test-gad-7', es='https://mind.aurzane.com/test-de-ansiedad/', clave='ansiedad', short='Anxiety', name='Anxiety test (GAD-7)', scale='GAD-7',
      desc='Take the GAD-7, the most widely used anxiety questionnaire in primary care. 7 questions, instant score with a clear explanation. Free and anonymous.',
      stem='Over the last 2 weeks, how often have you been bothered by the following problems?', ops=FREQ, inv=[],
      items=['Feeling nervous, anxious, or on edge', 'Not being able to stop or control worrying', 'Worrying too much about different things', 'Trouble relaxing',
             'Being so restless that it is hard to sit still', 'Becoming easily annoyed or irritable', 'Feeling afraid, as if something awful might happen'],
      min=0, max=21, levels=[[0, 4, 'ok', 'Minimal anxiety', 'Your anxiety symptoms are minimal. Some nervousness in demanding periods is normal.'],
                             [5, 9, 'mid', 'Mild anxiety', 'You have some mild symptoms of anxiety. Sleep, daily movement and less caffeine usually help. If they persist or get worse, talk to a professional.'],
                             [10, 14, 'high', 'Moderate anxiety', 'Your score is above 10, the cut-off at which a professional assessment is recommended. Anxiety is very treatable, especially with psychological therapy.'],
                             [15, 21, 'high', 'Severe anxiety', 'Your score suggests intense anxiety symptoms. We recommend booking an appointment with your doctor or a psychologist in the next few days.']],
      tips=[['Breathe out longer than you breathe in', 'Inhale for 4 seconds and exhale for 6, for 5 minutes. A longer exhale activates the system that calms you down.'],
            ['Schedule your worry', 'Set aside 15 minutes a day to think about your worries and write them down. Outside that time, remind yourself they already have a slot.'],
            ['Move every day', 'A brisk 30-minute walk reduces mild anxiety noticeably.'], ['Cut down on caffeine and alcohol', 'Both increase the physical symptoms of anxiety and worsen sleep.']],
      ref='Spitzer RL, Kroenke K, Williams JBW, Löwe B. A brief measure for assessing generalized anxiety disorder: the GAD-7. Arch Intern Med. 2006;166(10):1092-1097. No permission required to reproduce.'),
 dict(slug='depression-test-phq-9', es='https://mind.aurzane.com/test-de-depresion/', clave='depresion', short='Depression', name='Depression test (PHQ-9)', scale='PHQ-9',
      desc='Take the PHQ-9, the standard depression screening questionnaire used by doctors. 9 questions, instant score and what to do next. Free and anonymous.',
      stem='Over the last 2 weeks, how often have you been bothered by any of the following problems?', ops=FREQ, inv=[], crisis=8,
      items=['Little interest or pleasure in doing things', 'Feeling down, depressed, or hopeless', 'Trouble falling or staying asleep, or sleeping too much',
             'Feeling tired or having little energy', 'Poor appetite or overeating', 'Feeling bad about yourself, or that you are a failure or have let yourself or your family down',
             'Trouble concentrating on things, such as reading the newspaper or watching television',
             'Moving or speaking so slowly that other people could have noticed. Or the opposite: being so fidgety or restless that you have been moving around a lot more than usual',
             'Thoughts that you would be better off dead, or of hurting yourself in some way'],
      min=0, max=27, levels=[[0, 4, 'ok', 'Minimal or no depression', 'Your answers show minimal depressive symptoms.'],
                             [5, 9, 'mid', 'Mild depression', 'You have mild depressive symptoms. Keep an eye on them and look after routines, sleep and contact with people. If they last more than a few weeks, talk to a professional.'],
                             [10, 14, 'high', 'Moderate depression', 'Your score is at or above 10, the cut-off at which a professional assessment is recommended. Depression responds well to treatment.'],
                             [15, 19, 'high', 'Moderately severe depression', 'Your score suggests significant depressive symptoms. Please book an appointment with your doctor or a psychologist soon.'],
                             [20, 27, 'high', 'Severe depression', 'Your score suggests severe depressive symptoms. Please seek professional help in the next few days.']],
      tips=[['Do one small pleasant thing a day', 'Depression lowers motivation first. Acting before you feel like it, even a little, helps mood follow.'],
            ['Keep a regular sleep schedule', 'Getting up at the same time every day stabilises energy and mood.'],
            ['Stay in touch with someone', 'A short message or call a day reduces isolation, which feeds low mood.'], ['Get outside in daylight', 'Morning light and a short walk have a measurable effect on mood.']],
      ref='Kroenke K, Spitzer RL, Williams JBW. The PHQ-9: validity of a brief depression severity measure. J Gen Intern Med. 2001;16(9):606-613. No permission required to reproduce.'),
 dict(slug='self-esteem-test-rosenberg', es='https://mind.aurzane.com/test-de-autoestima/', clave='autoestima', short='Self-esteem', name='Self-esteem test (Rosenberg)', scale='RSES',
      desc='Take the Rosenberg Self-Esteem Scale, the most used self-esteem questionnaire in the world. 10 statements, instant result with an explanation. Free and anonymous.',
      stem='Below is a list of statements dealing with your general feelings about yourself. Indicate how strongly you agree or disagree with each statement.',
      ops=[[3, 'Strongly agree'], [2, 'Agree'], [1, 'Disagree'], [0, 'Strongly disagree']], inv=[1, 4, 5, 7, 8], invBase=3,
      items=['On the whole, I am satisfied with myself.', 'At times I think I am no good at all.', 'I feel that I have a number of good qualities.',
             'I am able to do things as well as most other people.', 'I feel I do not have much to be proud of.', 'I certainly feel useless at times.',
             "I feel that I'm a person of worth, at least on an equal plane with others.", 'I wish I could have more respect for myself.',
             'All in all, I am inclined to feel that I am a failure.', 'I take a positive attitude toward myself.'],
      min=0, max=30, levels=[[0, 14, 'high', 'Low self-esteem', 'Your score is below 15, which suggests low self-esteem right now. It is a common experience and it can change with practice and support.'],
                             [15, 25, 'ok', 'Self-esteem in the normal range', 'Your score is within the usual range: you value yourself in a balanced way.'],
                             [26, 30, 'ok', 'High self-esteem', 'Your score shows a solid, positive view of yourself.']],
      tips=[['Write down three things you did well each day', 'Training attention towards what works counters the habit of only noticing mistakes.'],
            ['Talk to yourself as you would to a friend', 'Notice harsh self-criticism and rephrase it in a fair, kind way.'],
            ['Keep small promises to yourself', 'Self-esteem grows with evidence: small goals you actually meet.'], ['Limit comparisons', 'Comparing your inside with other people\'s outside is never a fair contest.']],
      ref='Rosenberg M. Society and the Adolescent Self-Image. Princeton University Press; 1965. The scale is free to use for research and education.'),
 dict(slug='life-satisfaction-test-swls', es='https://mind.aurzane.com/test-de-satisfaccion-con-la-vida/', clave='satisfaccion-con-la-vida', short='Life satisfaction', name='Life satisfaction test (SWLS)', scale='SWLS',
      desc='Take the Satisfaction With Life Scale (Diener), the classic measure of how satisfied you are with your life. 5 statements, instant result. Free and anonymous.',
      stem='Below are five statements that you may agree or disagree with. Indicate your agreement with each item.',
      ops=[[1, 'Strongly disagree'], [2, 'Disagree'], [3, 'Slightly disagree'], [4, 'Neither agree nor disagree'], [5, 'Slightly agree'], [6, 'Agree'], [7, 'Strongly agree']], inv=[],
      items=['In most ways my life is close to my ideal.', 'The conditions of my life are excellent.', 'I am satisfied with my life.',
             'So far I have gotten the important things I want in life.', 'If I could live my life over, I would change almost nothing.'],
      min=5, max=35, levels=[[5, 9, 'high', 'Extremely dissatisfied', 'You are very dissatisfied with your life right now. It may help to talk it through with a professional.'],
                             [10, 14, 'high', 'Dissatisfied', 'You are dissatisfied with several areas of your life. Identifying which ones weigh most is a good first step.'],
                             [15, 19, 'mid', 'Slightly below average', 'You are somewhat dissatisfied: there are areas you would like to improve.'],
                             [20, 20, 'mid', 'Neutral', 'You are neither satisfied nor dissatisfied overall.'],
                             [21, 25, 'ok', 'Slightly satisfied', 'You are reasonably satisfied with your life, with some room for improvement.'],
                             [26, 30, 'ok', 'Satisfied', 'You are satisfied with your life: most areas are going well for you.'],
                             [31, 35, 'ok', 'Extremely satisfied', 'You are very satisfied with your life.']],
      tips=[['Look at areas, not your whole life', 'Rate work, relationships, health and leisure separately to see where a change would matter most.'],
            ['Invest in relationships', 'Close relationships are the most consistent predictor of life satisfaction.'],
            ['Practise gratitude in writing', 'Writing down specific good things each week raises satisfaction over time.'], ['Set one meaningful goal', 'Progress towards something you value matters more than reaching it fast.']],
      ref='Diener E, Emmons RA, Larsen RJ, Griffin S. The Satisfaction With Life Scale. J Pers Assess. 1985;49(1):71-75. Free to use with citation.'),
 dict(slug='resilience-test-brs', es='https://mind.aurzane.com/test-de-resiliencia/', clave='resiliencia', short='Resilience', name='Resilience test (Brief Resilience Scale)', scale='BRS',
      desc='Take the Brief Resilience Scale (Smith et al.), which measures your ability to bounce back from stress. 6 statements, instant result. Free and anonymous.',
      stem='Please indicate the extent to which you agree with each of the following statements.',
      ops=[[1, 'Strongly disagree'], [2, 'Disagree'], [3, 'Neutral'], [4, 'Agree'], [5, 'Strongly agree']], inv=[1, 3, 5], invBase=6, media=True,
      items=['I tend to bounce back quickly after hard times.', 'I have a hard time making it through stressful events.', 'It does not take me long to recover from a stressful event.',
             'It is hard for me to snap back when something bad happens.', 'I usually come through difficult times with little trouble.', 'I tend to take a long time to get over set-backs in my life.'],
      min=1, max=5, levels=[[1, 2.99, 'high', 'Low resilience', 'Right now it costs you more than average to recover after stressful situations. Resilience is a skill that can be trained.'],
                            [3, 4.30, 'ok', 'Normal resilience', 'You recover from difficulties like most people do.'],
                            [4.31, 5, 'ok', 'High resilience', 'You bounce back from difficult moments quickly.']],
      tips=[['Name what you can control', 'In a setback, separate what depends on you from what does not, and act on the first.'],
            ['Lean on people', 'Asking for support early speeds recovery more than any other strategy.'],
            ['Look after the basics', 'Sleep, movement and regular meals are the foundation of recovering from stress.'], ['Remember past recoveries', 'Recalling difficulties you have already overcome strengthens the belief that you can do it again.']],
      ref='Smith BW, Dalen J, Wiggins K, Tooley E, Christopher P, Bernard J. The Brief Resilience Scale: assessing the ability to bounce back. Int J Behav Med. 2008;15(3):194-200.'),
 dict(slug='self-efficacy-test-gse', es='https://mind.aurzane.com/test-de-autoeficacia/', clave='autoeficacia', short='Self-efficacy', name='Self-efficacy test (General Self-Efficacy Scale)', scale='GSE',
      desc='Take the General Self-Efficacy Scale (Schwarzer and Jerusalem): how confident you are in handling difficult situations. 10 statements, instant result. Free and anonymous.',
      stem='How true is each statement for you?', ops=[[1, 'Not at all true'], [2, 'Hardly true'], [3, 'Moderately true'], [4, 'Exactly true']], inv=[],
      items=['I can always manage to solve difficult problems if I try hard enough.', 'If someone opposes me, I can find the means and ways to get what I want.',
             'It is easy for me to stick to my aims and accomplish my goals.', 'I am confident that I could deal efficiently with unexpected events.',
             'Thanks to my resourcefulness, I know how to handle unforeseen situations.', 'I can solve most problems if I invest the necessary effort.',
             'I can remain calm when facing difficulties because I can rely on my coping abilities.', 'When I am confronted with a problem, I can usually find several solutions.',
             'If I am in trouble, I can usually think of a solution.', 'I can usually handle whatever comes my way.'],
      min=10, max=40, levels=[[10, 24, 'mid', 'Lower than average', 'You trust your ability to cope with difficulties less than most people. It grows with small, repeated successes.'],
                              [25, 32, 'ok', 'Average', 'Your confidence in handling difficult situations is in the usual range.'],
                              [33, 40, 'ok', 'Higher than average', 'You feel very capable of handling challenges and unexpected events.']],
      tips=[['Break goals into small steps', 'Each step you complete is evidence that you can do it.'], ['Learn from people like you', 'Seeing someone similar succeed raises your own confidence.'],
            ['Track your progress', 'Writing down what you achieved makes your abilities visible to yourself.'], ['Reframe nerves', 'Physical activation before a challenge is energy, not a sign that you cannot do it.']],
      ref='Schwarzer R, Jerusalem M. Generalized Self-Efficacy scale. In: Weinman J, Wright S, Johnston M, eds. Measures in health psychology. NFER-NELSON; 1995:35-37. Free to use.'),
]

FREQ_CBI = [[100, 'Always'], [75, 'Often'], [50, 'Sometimes'], [25, 'Seldom'], [0, 'Never or almost never']]
TESTS += [
 dict(slug='stress-test-dass-21', es='https://mind.aurzane.com/test-de-estres/', clave='estres', short='Stress', name='Stress test (DASS-21 stress scale)', scale='DASS-21 (stress)',
      desc='Take the stress scale of the DASS-21, a widely used and validated questionnaire. 7 statements about the past week, instant result. Free and anonymous.',
      stem='Please read each statement and indicate how much the statement applied to you over the past week.',
      ops=[[0, 'Did not apply to me at all'], [1, 'Applied to me to some degree, or some of the time'], [2, 'Applied to me to a considerable degree, or a good part of time'], [3, 'Applied to me very much, or most of the time']], inv=[], mult=2,
      items=['I found it hard to wind down', 'I tended to over-react to situations', 'I felt that I was using a lot of nervous energy', 'I found myself getting agitated',
             'I found it difficult to relax', 'I was intolerant of anything that kept me from getting on with what I was doing', 'I felt that I was rather touchy'],
      min=0, max=42, levels=[[0, 14, 'ok', 'Normal stress', 'Your stress level is within the usual range. Some tense days are normal.'],
                             [15, 18, 'mid', 'Mild stress', 'You are under some stress. Look after rest and breaks before it builds up.'],
                             [19, 25, 'mid', 'Moderate stress', 'Your stress is noticeably high. It is worth reviewing your workload and finding ways to switch off.'],
                             [26, 33, 'high', 'Severe stress', 'Your stress level is high. If it has lasted for weeks, talking to a professional can help a lot.'],
                             [34, 42, 'high', 'Extremely severe stress', 'Your stress level is very high. We recommend talking to your doctor or a psychologist soon.']],
      tips=[['Protect a daily switch-off time', 'Thirty minutes without screens or obligations lowers physical tension.'], ['Move your body', 'Exercise is one of the most effective ways to discharge accumulated stress.'],
            ['Write down what worries you', 'Putting it on paper and listing the next step reduces mental load.'], ['Sleep comes first', 'Lack of sleep makes everything feel more stressful.']],
      ref='Lovibond SH, Lovibond PF. Manual for the Depression Anxiety Stress Scales. 2nd ed. Sydney: Psychology Foundation; 1995. The DASS is in the public domain.'),
 dict(slug='wellbeing-test-who-5', es='https://live.aurzane.com/test-de-bienestar/', clave='bienestar', short='Wellbeing', name='Wellbeing test (WHO-5)', scale='WHO-5',
      desc='Take the WHO-5 Well-Being Index from the World Health Organization. 5 statements about the last two weeks, score from 0 to 100. Free and anonymous.',
      stem='Please indicate for each of the five statements which is closest to how you have been feeling over the last two weeks.',
      ops=[[5, 'All of the time'], [4, 'Most of the time'], [3, 'More than half of the time'], [2, 'Less than half of the time'], [1, 'Some of the time'], [0, 'At no time']], inv=[], mult=4,
      items=['I have felt cheerful and in good spirits', 'I have felt calm and relaxed', 'I have felt active and vigorous', 'I woke up feeling fresh and rested', 'My daily life has been filled with things that interest me'],
      min=0, max=100, levels=[[0, 28, 'high', 'Low wellbeing', 'Your score is low. It may be worth checking your mood with a professional, especially if it has lasted for weeks.'],
                              [29, 50, 'mid', 'Reduced wellbeing', 'Your wellbeing is below the usual range. Small changes in rest, activity and contact with people can help.'],
                              [51, 100, 'ok', 'Good wellbeing', 'Your wellbeing over the last two weeks is good.']],
      tips=[['Plan one enjoyable thing a day', 'Wellbeing grows with small pleasant moments you actually schedule.'], ['Get morning light', 'A short walk early in the day improves energy and sleep.'],
            ['Keep a regular sleep time', 'Waking up rested is one of the five questions for a reason.'], ['Stay connected', 'Contact with people you trust is a strong protector of wellbeing.']],
      ref='World Health Organization. WHO-5 Well-Being Index. 1998. Free to use; see Topp CW et al. Psychother Psychosom. 2015;84(3):167-176.'),
 dict(slug='burnout-test-cbi', es='https://mind.aurzane.com/test-de-burnout/', clave='burnout', short='Burnout', name='Work burnout test (Copenhagen Burnout Inventory)', scale='CBI (work-related)',
      desc='Take the work-related scale of the Copenhagen Burnout Inventory, a free and validated burnout questionnaire. 7 questions, instant result. Free and anonymous.',
      stem='Answer each question about your work.',
      ops=[[100, 'To a very high degree'], [75, 'To a high degree'], [50, 'Somewhat'], [25, 'To a low degree'], [0, 'To a very low degree']], ops2=FREQ_CBI, ops2items=[3, 4, 5, 6], inv=[6], invBase=100, media=True,
      items=['Is your work emotionally exhausting?', 'Do you feel burnt out because of your work?', 'Does your work frustrate you?', 'Do you feel worn out at the end of the working day?',
             'Are you exhausted in the morning at the thought of another day at work?', 'Do you feel that every working hour is tiring for you?', 'Do you have enough energy for family and friends during leisure time?'],
      min=0, max=100, levels=[[0, 49.99, 'ok', 'No burnout', 'Your level of work exhaustion is below the cut-off. Keep protecting your rest.'],
                              [50, 74.99, 'mid', 'Moderate burnout', 'Your work is wearing you down. It is a good moment to adjust workload, breaks and boundaries.'],
                              [75, 99.99, 'high', 'High burnout', 'Your level of work exhaustion is high. Talk to your doctor or a psychologist, and to your employer if possible.'],
                              [100, 100, 'high', 'Severe burnout', 'Your answers show severe work exhaustion. Please seek professional support soon.']],
      tips=[['Set a clear end to the working day', 'Closing tasks and notifications at a fixed time helps you recover.'], ['Take real breaks', 'Short breaks away from the screen during the day reduce exhaustion.'],
            ['Talk about workload', 'Burnout comes from the job as much as from you: raising it is legitimate.'], ['Recover energy outside work', 'Sleep, exercise and time with people refill what work drains.']],
      ref='Kristensen TS, Borritz M, Villadsen E, Christensen KB. The Copenhagen Burnout Inventory: a new tool for the assessment of burnout. Work & Stress. 2005;19(3):192-207. Free to use.'),
 dict(slug='self-compassion-test-scs-sf', es='https://mind.aurzane.com/test-de-autocompasion/', clave='autocompasion', short='Self-compassion', name='Self-compassion test (Neff, short form)', scale='SCS-SF',
      desc='Take the Self-Compassion Scale short form by Kristin Neff. 12 statements, instant result with an explanation. Free and anonymous.',
      stem='How I typically act towards myself in difficult times. Indicate how often you behave in the stated manner.',
      ops=[[1, 'Almost never'], [2, 'Rarely'], [3, 'Sometimes'], [4, 'Often'], [5, 'Almost always']], inv=[0, 3, 7, 8, 10, 11], invBase=6, media=True,
      items=['When I fail at something important to me I become consumed by feelings of inadequacy.', "I try to be understanding and patient towards those aspects of my personality I don't like.",
             'When something painful happens I try to take a balanced view of the situation.', "When I'm feeling down, I tend to feel like most other people are probably happier than I am.",
             'I try to see my failings as part of the human condition.', "When I'm going through a very hard time, I give myself the caring and tenderness I need.",
             'When something upsets me I try to keep my emotions in balance.', "When I fail at something that's important to me, I tend to feel alone in my failure.",
             "When I'm feeling down I tend to obsess and fixate on everything that's wrong.", 'When I feel inadequate in some way, I try to remind myself that feelings of inadequacy are shared by most people.',
             "I'm disapproving and judgmental about my own flaws and inadequacies.", "I'm intolerant and impatient towards those aspects of my personality I don't like."],
      min=1, max=5, levels=[[1, 2.49, 'mid', 'Low self-compassion', 'You tend to be hard on yourself in difficult moments. Self-compassion can be learned with practice.'],
                            [2.5, 3.5, 'ok', 'Moderate self-compassion', 'You treat yourself with kindness in some situations and are harder on yourself in others.'],
                            [3.51, 5, 'ok', 'High self-compassion', 'You usually treat yourself with kindness and understanding when things go wrong.']],
      tips=[['Talk to yourself like a good friend', 'Notice harsh inner criticism and answer it with the words you would use with someone you love.'], ['Remember you are not alone', 'Difficulties are part of being human, not proof that something is wrong with you.'],
            ['Use a soothing gesture', 'A hand on your chest and a few slow breaths calm the body in hard moments.'], ['Take a self-compassion break', 'Name the moment as difficult, remember others feel this too, and offer yourself kindness.']],
      ref='Raes F, Pommier E, Neff KD, Van Gucht D. Construction and factorial validation of a short form of the Self-Compassion Scale. Clin Psychol Psychother. 2011;18(3):250-255. Free to use.'),
]

CSS = '''
:root{--bg:#0B0E1D;--sup:#141A33;--txt:#F3EFE6;--sua:#B9B3A6;--oro:#E2BF6A;--lin:rgba(255,255,255,.1);--ok:#8CC084;--mid:#E2BF6A;--high:#E39B9B}
*{box-sizing:border-box;margin:0;padding:0}body{background:var(--bg);color:var(--txt);font:17px/1.65 "Instrument Sans",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--oro)}.w{max-width:860px;margin:0 auto;padding:0 20px}
header{border-bottom:1px solid var(--lin)}header .w{display:flex;align-items:center;gap:16px;height:62px}
.logo{font:600 1.1rem "Bodoni Moda",serif;letter-spacing:.06em;text-decoration:none;color:var(--txt)}.logo span{color:var(--oro)}
header nav{margin-left:auto;display:flex;gap:16px;font-size:.9rem}header nav a{color:var(--sua);text-decoration:none}
h1{font:600 clamp(1.9rem,4.6vw,2.7rem)/1.15 "Bodoni Moda",serif;margin:34px 0 12px}h2{font:600 1.35rem "Bodoni Moda",serif;margin:30px 0 10px}
.lead{color:var(--sua);font-size:1.08rem;margin-bottom:22px}.stem{background:var(--sup);border:1px solid var(--lin);border-radius:12px;padding:14px 16px;margin-bottom:16px;font-weight:600}
.q{border-bottom:1px solid var(--lin);padding:16px 0}.q p{margin-bottom:10px}.q p b{color:var(--oro);margin-right:6px}
.ops{display:flex;flex-wrap:wrap;gap:8px}.ops label{cursor:pointer}.ops input{position:absolute;opacity:0}
.ops span{display:inline-block;border:1px solid rgba(255,255,255,.22);border-radius:99px;padding:7px 14px;font-size:.88rem}
.ops input:checked+span{background:var(--oro);color:#1b1440;border-color:var(--oro);font-weight:700}.ops input:focus-visible+span{outline:2px solid var(--oro);outline-offset:2px}
.prog{position:sticky;top:0;background:var(--bg);padding:10px 0;z-index:5;font-size:.85rem;color:var(--sua)}.prog i{display:block;height:4px;background:var(--lin);border-radius:3px;margin-top:6px}.prog i b{display:block;height:100%;width:0;background:var(--oro);border-radius:3px;transition:width .2s}
#resultado{scroll-margin-top:80px;margin:26px 0;padding:22px;border-radius:16px;background:var(--sup);border:1px solid var(--lin)}#resultado[hidden]{display:none}
.score{font:700 2.6rem "Bodoni Moda",serif}.score small{font-size:1rem;color:var(--sua);font-weight:400}
.lvl{display:inline-block;padding:4px 12px;border-radius:99px;font-weight:700;font-size:.9rem;margin:6px 0 12px}.lvl.ok{background:rgba(140,192,132,.18);color:var(--ok)}.lvl.mid{background:rgba(226,191,106,.18);color:var(--mid)}.lvl.high{background:rgba(227,155,155,.18);color:var(--high)}
.tips{list-style:none;display:grid;gap:10px;margin-top:10px}.tips li{padding-left:14px;border-left:2px solid var(--oro)}.tips b{display:block}
.alert{margin-top:16px;padding:14px 16px;border-radius:12px;background:rgba(227,155,155,.12);border:1px solid rgba(227,155,155,.45)}
.btn{display:inline-block;border:0;border-radius:99px;padding:13px 24px;background:var(--oro);color:#1b1440;font-weight:700;font-size:.95rem;font-family:inherit;cursor:pointer;margin-top:18px;text-decoration:none}
.small{font-size:.86rem;color:var(--sua)}.ref{font-size:.82rem;color:var(--sua);margin-top:8px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px;margin:20px 0 40px}.card{display:block;text-decoration:none;color:inherit;background:var(--sup);border:1px solid var(--lin);border-radius:14px;padding:18px}.card b{font:600 1.1rem "Bodoni Moda",serif;display:block;margin-bottom:6px}.card span{font-size:.9rem;color:var(--sua)}
footer{border-top:1px solid var(--lin);margin-top:40px;padding:26px 0 40px;font-size:.84rem;color:var(--sua)}
'''
HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="aurzane-idiomas" content="no">
<script src="https://aurzane.com/aurzane-paleta.js"></script>
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
{alt}
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og}">
<link rel="icon" href="https://aurzane.com/favicon.ico" sizes="48x48">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@600;700&family=Instrument+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{ld}</script>
<style>{css}</style>
</head>
<body>
<header><div class="w"><a class="logo" href="https://aurzane.com/">AUR<span>Z</span>ANE</a><nav><a href="{base}">All tests</a><a href="{es}" hreflang="es" lang="es">Español</a></nav></div></header>
'''
FOOT = '''<footer><div class="w"><p>AURZANE · Tests created and reviewed by a clinical psychologist (Psi. Cl. Adrian Sánchez Samaniego). These questionnaires are screening tools and do not replace a professional assessment. Your answers are not sent anywhere unless you are signed in and choose to save them.</p><p style="margin-top:6px"><a href="https://aurzane.com/privacidad.html">Privacy</a> · <a href="https://aurzane.com/">aurzane.com</a></p></div></footer>
</body></html>'''

JS = r'''<script>
var CFG = %s;
(function(){
  var R = {}, $ = function(id){ return document.getElementById(id); };
  var q = '';
  CFG.items.forEach(function(t, i){
    q += '<fieldset class="q"><legend class="sr" style="position:absolute;left:-9999px">' + (i + 1) + '</legend><p><b>' + (i + 1) + '.</b>' + t + '</p><div class="ops">' +
      ((CFG.ops2items || []).indexOf(i) >= 0 ? CFG.ops2 : CFG.ops).map(function(o){ return '<label><input type="radio" name="i' + i + '" value="' + o[0] + '"><span>' + o[1] + '</span></label>'; }).join('') + '</div></fieldset>';
  });
  $('items').innerHTML = q;
  $('items').addEventListener('change', function(e){
    R[e.target.name] = +e.target.value; var n = Object.keys(R).length;
    $('cuenta').textContent = n + ' of ' + CFG.items.length + ' answered'; $('barra').style.width = (n / CFG.items.length * 100) + '%%';
  });
  $('calc').addEventListener('click', function(){
    var falta = CFG.items.findIndex(function(_, i){ return R['i' + i] === undefined; });
    if (falta >= 0) { $('msg').textContent = 'Please answer question ' + (falta + 1) + ' first.'; document.getElementsByName('i' + falta)[0].closest('.q').scrollIntoView({behavior: 'smooth', block: 'center'}); return; }
    $('msg').textContent = '';
    var total = 0; CFG.items.forEach(function(_, i){ var v = R['i' + i]; total += CFG.inv.indexOf(i) >= 0 ? (CFG.invBase - v) : v; });
    if (CFG.media) total = Math.round(total / CFG.items.length * 100) / 100;
    if (CFG.mult) total = total * CFG.mult;
    var nv = CFG.levels.filter(function(x){ return total >= x[0] && total <= x[1] + 0.0001; })[0] || CFG.levels[CFG.levels.length - 1];
    var shown = CFG.media ? total.toFixed(2) : total;
    var h = '<div class="score">' + shown + ' <small>out of ' + CFG.max + '</small></div><span class="lvl ' + nv[2] + '">' + nv[3] + '</span><p>' + nv[4] + '</p>';
    if (CFG.crisis != null && R['i' + CFG.crisis] > 0) h += '<div class="alert"><b>What you feel matters, and help is available now.</b> You said you have had thoughts of hurting yourself or that you would be better off dead. Please talk to someone today: in the US call or text <a href="tel:988">988</a>, in the UK and Ireland call Samaritans on <a href="tel:116123">116 123</a>, or call your local emergency number if you are in danger.</div>';
    else if (nv[2] === 'high') h += '<div class="alert"><b>Asking for help works.</b> Your doctor can refer you to psychological therapy, or you can contact a licensed psychologist directly.</div>';
    h += '<h2 style="font-size:1.1rem">What you can do</h2><ul class="tips">' + CFG.tips.map(function(t){ return '<li><b>' + t[0] + '</b>' + t[1] + '</li>'; }).join('') + '</ul>';
    $('resultado').innerHTML = h; $('resultado').hidden = false; $('accRes').hidden = false;
    window.__res = { titulo: CFG.titulo, valor: shown, max: CFG.max, nivel: nv[3], unidad: 'out of ' + CFG.max };
    document.body.classList.add('hecho');
    $('resultado').scrollIntoView({behavior: 'smooth', block: 'start'});
  });
})();
</script>'''


def pagina(t):
    url = BASE + t['slug'] + '/'
    cfg = {k: t.get(k) for k in ['items', 'ops', 'inv', 'min', 'max', 'levels', 'tips', 'clave']}
    cfg.update({'mult': t.get('mult'), 'ops2': t.get('ops2'), 'ops2items': t.get('ops2items'), 'invBase': t.get('invBase', 0), 'media': bool(t.get('media')), 'crisis': t.get('crisis'), 'titulo': t['name']})
    cfg['clave'] = t['clave'] + '-en'
    lv = '; '.join(f"{l[0]} to {l[1]}: {l[3].lower()}" for l in t['levels'])
    faq = [(f"What is the {t['scale']}?", f"It is a validated questionnaire. Source: {t['ref']}"),
           ('How is it scored?', f"Scores range from {t['min']} to {t['max']}. {lv}."),
           ('Is this a diagnosis?', 'No. It is a screening tool. Only a qualified professional can make a diagnosis after an interview.')]
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebApplication', 'name': t['name'], 'url': url, 'applicationCategory': 'HealthApplication', 'operatingSystem': 'Web', 'inLanguage': 'en', 'isAccessibleForFree': True,
         'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}, 'publisher': {'@type': 'Organization', 'name': 'AURZANE', 'url': 'https://aurzane.com/'}},
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': a, 'acceptedAnswer': {'@type': 'Answer', 'text': b}} for a, b in faq]}]}
    alt = f'<link rel="alternate" hreflang="en" href="{url}"><link rel="alternate" hreflang="es" href="{t["es"]}"><link rel="alternate" hreflang="x-default" href="{t["es"]}">'
    h = HEAD.format(title=E(t['name'] + ': free online questionnaire | AURZANE'), desc=E(t['desc']), url=url, alt=alt, og=t['es'] + 'og.jpg',
                    ld=json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'), css=CSS, base=BASE, es=t['es'])
    h += f'''<main class="w">
<h1>{E(t['name'])}</h1>
<p class="lead">{E(t['desc'])}</p>
<div class="prog"><span id="cuenta">0 of {len(t['items'])} answered</span><i><b id="barra"></b></i></div>
<p class="stem">{E(t['stem'])}</p>
<form id="items" onsubmit="return false"></form>
<button class="btn" id="calc" type="button">See my result</button> <span id="msg" class="small" role="alert"></span>
<section id="resultado" hidden aria-live="polite"></section>
<div id="accRes" hidden><button class="btn" type="button" onclick="window.print()">Save as PDF</button> <a class="btn" style="background:transparent;border:1px solid var(--oro);color:var(--oro)" href="{BASE}">Take another test</a></div>
<h2>About this test</h2>
<p>{E(t['scale'])} is a validated, widely used questionnaire. Scores range from {t['min']} to {t['max']}. {E(lv)}.</p>
<p class="ref">Reference: {E(t['ref'])}</p>
<p class="small" style="margin-top:12px">This test is for guidance only and does not replace an assessment by a health professional. ¿Prefieres hacerlo en español? <a href="{t['es']}" hreflang="es" lang="es">Versión en español</a>.</p>
</main>
'''
    h += JS % json.dumps(cfg, ensure_ascii=False) + FOOT
    return h


def indice():
    url = BASE
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'Free psychological tests', 'url': url, 'inLanguage': 'en'}
    h = HEAD.format(title='Free psychological tests in English | AURZANE', desc='Validated psychological questionnaires in their original English version: anxiety, depression, self-esteem, life satisfaction, resilience and self-efficacy. Free and anonymous.',
                    url=url, alt=f'<link rel="alternate" hreflang="en" href="{url}"><link rel="alternate" hreflang="es" href="https://mind.aurzane.com/"><link rel="alternate" hreflang="x-default" href="https://mind.aurzane.com/">',
                    og='https://aurzane.com/og-portada.jpg', ld=json.dumps(ld), css=CSS, base=BASE, es='https://mind.aurzane.com/')
    h += '<main class="w"><h1>Free psychological tests</h1><p class="lead">Validated questionnaires in their original English wording, with an instant, clearly explained result. Created and reviewed by a clinical psychologist. Free and anonymous.</p><div class="grid">'
    h += ''.join(f'<a class="card" href="{BASE}{t["slug"]}/"><b>{E(t["name"])}</b><span>{len(t["items"])} questions · {E(t["scale"])}</span></a>' for t in TESTS)
    h += '</div><p class="small">More tests are available in Spanish at <a href="https://mind.aurzane.com/" hreflang="es">mind.aurzane.com</a>.</p></main>' + FOOT
    return h


os.makedirs(OUT, exist_ok=True)
for t in TESTS:
    os.makedirs(os.path.join(OUT, t['slug']), exist_ok=True)
    open(os.path.join(OUT, t['slug'], 'index.html'), 'w', encoding='utf-8').write(pagina(t))
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(indice())
print('ok', len(TESTS))
