# -*- coding: utf-8 -*-
"""Testes em português do Brasil, com a redação oficial validada de cada escala (GAD-7, PHQ-9 e WHO-5, de uso livre).
Reaproveita a plantilla de tests_en/gen.py e traduz a interface. Saída: publicar/mind.aurzane.com/pt/
Uso: python3 tests_pt/gen.py"""
import os, re, json

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(R, 'tests_en', 'gen.py'), encoding='utf-8').read()
ns = {'__file__': os.path.join(R, 'tests_en', 'gen.py')}
exec(src[:src.index('\nos.makedirs(OUT')], ns)
BASE = 'https://mind.aurzane.com/pt/'
OUT = os.path.join(R, 'publicar', 'mind.aurzane.com', 'pt')
ns['BASE'] = BASE

FREQ = [[0, 'Nenhuma vez'], [1, 'Vários dias'], [2, 'Mais da metade dos dias'], [3, 'Quase todos os dias']]
TESTS = [
 dict(slug='teste-de-ansiedade-gad-7', en='anxiety-test-gad-7', es='https://mind.aurzane.com/test-de-ansiedad/', clave='ansiedad', name='Teste de ansiedade (GAD-7)', scale='GAD-7',
      desc='Faça o GAD-7, o questionário de ansiedade mais usado na atenção primária. 7 perguntas, resultado imediato e explicado. Grátis e anônimo.',
      stem='Durante as últimas 2 semanas, com que frequência você foi incomodado/a pelos problemas abaixo?', ops=FREQ, inv=[],
      items=['Sentir-se nervoso/a, ansioso/a ou muito tenso/a', 'Não ser capaz de impedir ou de controlar as preocupações', 'Preocupar-se muito com diversas coisas', 'Dificuldade para relaxar',
             'Ficar tão agitado/a que se torna difícil permanecer sentado/a', 'Ficar facilmente aborrecido/a ou irritado/a', 'Sentir medo como se algo horrível fosse acontecer'],
      min=0, max=21, levels=[[0, 4, 'ok', 'Ansiedade mínima', 'Seus sintomas de ansiedade são mínimos. Algum nervosismo em períodos exigentes é normal.'],
                             [5, 9, 'mid', 'Ansiedade leve', 'Você tem alguns sintomas leves de ansiedade. Sono, movimento diário e menos cafeína costumam ajudar. Se persistirem, fale com um profissional.'],
                             [10, 14, 'high', 'Ansiedade moderada', 'Sua pontuação está acima de 10, o ponto a partir do qual se recomenda uma avaliação profissional. A ansiedade tem tratamento eficaz.'],
                             [15, 21, 'high', 'Ansiedade grave', 'Sua pontuação indica sintomas intensos de ansiedade. Recomendamos marcar uma consulta com seu médico ou um psicólogo nos próximos dias.']],
      tips=[['Expire mais longo do que inspira', 'Inspire por 4 segundos e expire por 6, durante 5 minutos. A expiração longa ativa o sistema que acalma o corpo.'],
            ['Marque hora para se preocupar', 'Reserve 15 minutos por dia para pensar nas preocupações e anotá-las. Fora desse tempo, lembre-se de que elas já têm o seu momento.'],
            ['Mexa-se todos os dias', 'Uma caminhada rápida de 30 minutos reduz a ansiedade leve.'], ['Reduza cafeína e álcool', 'Ambos aumentam os sintomas físicos da ansiedade e pioram o sono.']],
      ref='Spitzer RL, Kroenke K, Williams JBW, Löwe B. A brief measure for assessing generalized anxiety disorder: the GAD-7. Arch Intern Med. 2006;166(10):1092-1097. Versão oficial em português do Brasil; reprodução livre.'),
 dict(slug='teste-de-depressao-phq-9', en='depression-test-phq-9', es='https://mind.aurzane.com/test-de-depresion/', clave='depresion', name='Teste de depressão (PHQ-9)', scale='PHQ-9',
      desc='Faça o PHQ-9, o questionário de rastreamento de depressão usado por médicos. 9 perguntas, resultado imediato e o que fazer a seguir. Grátis e anônimo.',
      stem='Durante as últimas 2 semanas, com que frequência você foi incomodado/a por qualquer um dos problemas abaixo?', ops=FREQ, inv=[], crisis=8,
      items=['Pouco interesse ou pouco prazer em fazer as coisas', 'Se sentir "para baixo", deprimido/a ou sem perspectiva', 'Dificuldade para pegar no sono ou permanecer dormindo, ou dormir mais do que de costume',
             'Se sentir cansado/a ou com pouca energia', 'Falta de apetite ou comendo demais', 'Se sentir mal consigo mesmo/a, ou achar que você é um fracasso ou que decepcionou sua família ou você mesmo/a',
             'Dificuldade para se concentrar nas coisas, como ler o jornal ou ver televisão',
             'Lentidão para se movimentar ou falar, a ponto das outras pessoas perceberem. Ou o oposto: estar tão agitado/a ou inquieto/a que você fica andando de um lado para o outro muito mais do que de costume',
             'Pensar em se ferir de alguma maneira ou que seria melhor estar morto/a'],
      min=0, max=27, levels=[[0, 4, 'ok', 'Depressão mínima ou ausente', 'Suas respostas mostram sintomas depressivos mínimos.'],
                             [5, 9, 'mid', 'Depressão leve', 'Você tem sintomas depressivos leves. Cuide da rotina, do sono e do contato com pessoas. Se durarem mais de algumas semanas, fale com um profissional.'],
                             [10, 14, 'high', 'Depressão moderada', 'Sua pontuação é 10 ou mais, o ponto a partir do qual se recomenda uma avaliação profissional. A depressão responde bem ao tratamento.'],
                             [15, 19, 'high', 'Depressão moderadamente grave', 'Sua pontuação indica sintomas depressivos importantes. Marque uma consulta com seu médico ou um psicólogo em breve.'],
                             [20, 27, 'high', 'Depressão grave', 'Sua pontuação indica sintomas depressivos graves. Procure ajuda profissional nos próximos dias.']],
      tips=[['Faça uma pequena coisa agradável por dia', 'A depressão tira a motivação primeiro. Agir antes de ter vontade, mesmo pouco, ajuda o humor a acompanhar.'],
            ['Mantenha horários regulares de sono', 'Acordar sempre na mesma hora estabiliza a energia e o humor.'],
            ['Fale com alguém todos os dias', 'Uma mensagem ou ligação curta reduz o isolamento, que alimenta o desânimo.'], ['Saia à luz do dia', 'A luz da manhã e uma caminhada curta têm efeito comprovado no humor.']],
      ref='Kroenke K, Spitzer RL, Williams JBW. The PHQ-9: validity of a brief depression severity measure. J Gen Intern Med. 2001;16(9):606-613. Versão oficial em português do Brasil; reprodução livre.'),
 dict(slug='teste-de-bem-estar-who-5', en='wellbeing-test-who-5', es='https://live.aurzane.com/test-de-bienestar/', clave='bienestar', name='Teste de bem-estar (WHO-5)', scale='WHO-5',
      desc='Faça o Índice de Bem-Estar WHO-5 da Organização Mundial da Saúde. 5 afirmações sobre as últimas duas semanas, pontuação de 0 a 100. Grátis e anônimo.',
      stem='Indique, para cada uma das cinco afirmações, a que mais se aproxima de como você tem se sentido nas últimas duas semanas.',
      ops=[[5, 'Todo o tempo'], [4, 'A maior parte do tempo'], [3, 'Mais da metade do tempo'], [2, 'Menos da metade do tempo'], [1, 'Algumas vezes'], [0, 'Em nenhum momento']], inv=[], mult=4,
      items=['Eu me senti alegre e de bom humor', 'Eu me senti calmo/a e tranquilo/a', 'Eu me senti ativo/a e enérgico/a', 'Eu acordei me sentindo descansado/a e revigorado/a', 'Meu dia a dia tem sido preenchido com coisas que me interessam'],
      min=0, max=100, levels=[[0, 28, 'high', 'Bem-estar baixo', 'Sua pontuação é baixa. Vale a pena conversar sobre o seu humor com um profissional, sobretudo se isso dura semanas.'],
                              [29, 50, 'mid', 'Bem-estar reduzido', 'Seu bem-estar está abaixo do habitual. Pequenas mudanças no descanso, na atividade e no contato com pessoas ajudam.'],
                              [51, 100, 'ok', 'Bom bem-estar', 'Seu bem-estar nas últimas duas semanas é bom.']],
      tips=[['Planeje algo agradável por dia', 'O bem-estar cresce com pequenos momentos bons que você realmente agenda.'], ['Pegue luz pela manhã', 'Uma caminhada curta cedo melhora a energia e o sono.'],
            ['Durma em horário regular', 'Acordar descansado/a é uma das cinco perguntas por um bom motivo.'], ['Mantenha contato', 'Conviver com pessoas de confiança protege o bem-estar.']],
      ref='Organização Mundial da Saúde. WHO-5 Well-Being Index. 1998. Uso livre; ver Topp CW et al. Psychother Psychosom. 2015;84(3):167-176.'),
]

UI = [
    ('<html lang="en">', '<html lang="pt-BR">'), ('"inLanguage": "en"', '"inLanguage": "pt-BR"'),
    (': free online questionnaire | AURZANE', ': questionário grátis online | AURZANE'),
    ('>All tests<', '>Todos os testes<'), ('See my result', 'Ver meu resultado'), ('Save as PDF', 'Salvar em PDF'), ('Take another test', 'Fazer outro teste'),
    ('<h2>About this test</h2>', '<h2>Sobre este teste</h2>'), ('is a validated, widely used questionnaire. Scores range from', 'é um questionário validado e muito usado. A pontuação vai de'),
    (' to ', ' a '), ('Reference: ', 'Referência: '),
    ('This test is for guidance only and does not replace an assessment by a health professional. ¿Prefieres hacerlo en español?', 'Este teste é apenas orientativo e não substitui a avaliação de um profissional de saúde. ¿Prefieres hacerlo en español?'),
    (" answered'", " respondidas'"), (' answered<', ' respondidas<'), ("' of '", "' de '"), (' of ', ' de '),
    ("'Please answer question '", "'Responda primeiro à pergunta '"), ("' first.'", "''"),
    ('out of ', 'de '), ("'What you can do'", "'O que você pode fazer'"), ('>What you can do<', '>O que você pode fazer<'),
    ('<b>What you feel matters, and help is available now.</b> You said you have had thoughts of hurting yourself or that you would be better off dead. Please talk to someone today: in the US call or text <a href="tel:988">988</a>, in the UK and Ireland call Samaritans on <a href="tel:116123">116 123</a>, or call your local emergency number if you are in danger.',
     '<b>O que você sente importa, e há ajuda agora.</b> Você disse que teve pensamentos de se ferir ou de que seria melhor estar morto/a. Fale com alguém hoje: no Brasil, ligue para o CVV no <a href="tel:188">188</a> (gratuito, 24 horas) ou acesse cvv.org.br. Se estiver em perigo, ligue para o 192 (SAMU).'),
    ('<b>Asking for help works.</b> Your doctor can refer you to psychological therapy, or you can contact a licensed psychologist directly.',
     '<b>Pedir ajuda funciona.</b> Seu médico pode encaminhar você para psicoterapia, ou você pode procurar diretamente um psicólogo.'),
    ('Tests created and reviewed by a clinical psychologist (Psi. Cl. Adrian Sánchez Samaniego). These questionnaires are screening tools and do not replace a professional assessment. Your answers are not sent anywhere unless you are signed in and choose to save them.',
     'Testes criados e revisados por um psicólogo clínico (Psi. Cl. Adrian Sánchez Samaniego). Estes questionários são ferramentas de rastreamento e não substituem uma avaliação profissional. Suas respostas não são enviadas a lugar nenhum, a menos que você esteja conectado/a e escolha salvá-las.'),
    ('>Privacy<', '>Privacidade<'),
    ('What is the ', 'O que é o '), ('It is a validated questionnaire. Source: ', 'É um questionário validado. Fonte: '), ('How is it scored?', 'Como é a pontuação?'),
    ('Scores range from', 'A pontuação vai de'), ('Is this a diagnosis?', 'Isto é um diagnóstico?'),
    ('No. It is a screening tool. Only a qualified professional can make a diagnosis after an interview.', 'Não. É uma ferramenta de rastreamento. Só um profissional qualificado pode fazer um diagnóstico após uma entrevista.'),
]


def traducir(h):
    for a, b in sorted(UI, key=lambda z: -len(z[0])): h = h.replace(a, b)
    return h


os.makedirs(OUT, exist_ok=True)
for t in TESTS:
    h = ns['pagina'](t)
    h = h.replace(ns['BASE'] + t['slug'] + '/', BASE + t['slug'] + '/')
    h = traducir(h)
    url = BASE + t['slug'] + '/'
    alt = (f'<link rel="alternate" hreflang="pt-BR" href="{url}"><link rel="alternate" hreflang="en" href="https://mind.aurzane.com/en/{t["en"]}/">'
           f'<link rel="alternate" hreflang="es" href="{t["es"]}"><link rel="alternate" hreflang="x-default" href="{t["es"]}">')
    h = re.sub(r'<link rel="alternate" hreflang="en"[^\n]*', alt, h, count=1)
    h = h.replace('href="https://mind.aurzane.com/en/" ', 'href="' + BASE + '" ').replace('<a href="https://mind.aurzane.com/en/">', '<a href="' + BASE + '">')
    os.makedirs(os.path.join(OUT, t['slug']), exist_ok=True)
    open(os.path.join(OUT, t['slug'], 'index.html'), 'w', encoding='utf-8').write(h)
cards = ''.join(f'<a class="card" href="{BASE}{t["slug"]}/"><b>{t["name"]}</b><span>{len(t["items"])} perguntas · {t["scale"]}</span></a>' for t in TESTS)
idx = ns['indice']()
idx = idx[:idx.index('<main')] + ('<main class="w"><h1>Testes psicológicos grátis</h1><p class="lead">Questionários validados na versão oficial em português, com resultado imediato e explicado. '
       'Criados e revisados por um psicólogo clínico. Grátis e anônimos.</p><div class="grid">' + cards + '</div><p class="small">Também em <a href="https://mind.aurzane.com/en/" hreflang="en">inglês</a> e '
       '<a href="https://mind.aurzane.com/" hreflang="es">espanhol</a>.</p></main>') + idx[idx.index('<footer'):]
idx = traducir(idx).replace('Free psychological tests in English | AURZANE', 'Testes psicológicos grátis em português | AURZANE')
idx = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{BASE}">', idx)
idx = re.sub(r'<link rel="alternate" hreflang="en"[^\n]*', f'<link rel="alternate" hreflang="pt-BR" href="{BASE}"><link rel="alternate" hreflang="en" href="https://mind.aurzane.com/en/"><link rel="alternate" hreflang="es" href="https://mind.aurzane.com/"><link rel="alternate" hreflang="x-default" href="https://mind.aurzane.com/">', idx, count=1)
idx = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Questionários psicológicos validados em português: ansiedade (GAD-7), depressão (PHQ-9) e bem-estar (WHO-5). Grátis e anônimos.">', idx)
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(idx)
print('ok', len(TESTS))
