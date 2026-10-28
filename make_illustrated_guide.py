"""Generate original wiring illustrations and a beginner PDF; not hardware proof."""
from html import escape
from pathlib import Path
import re
import fitz

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "docs" / "images"
OUTPUT = ROOT / "guia-ilustrado-iniciantes.pdf"
FONT = "Segoe UI, Arial, sans-serif"
BLUE, GREEN, YELLOW, RED, GRAY = "#dae8fc", "#d5e8d4", "#fff2cc", "#f8cecc", "#f5f5f5"
NETS = {
    10: ("GND", "GND"),
    11: ("3V3", "3V3"),
    12: ("D0 / GPIO1", "SDA"),
    13: ("D1 / GPIO2", "SCL"),
    15: ("5V", "VIN"),
    16: ("D6 / GPIO43", "BCLK"),
    17: ("D4 / GPIO5", "LRC"),
    18: ("D8 / GPIO7", "DIN"),
    20: ("D7 / GPIO44", "botao"),
    21: ("D3 / GPIO4", "PAN"),
    22: ("D5 / GPIO6", "TILT"),
}
COLORS = {10: "#333333", 11: "#007c57", 15: "#b42318"}
COLORS.update({row: "#2563a6" for row in NETS if row not in COLORS})
WIRES = [
    ("oled-gnd", "01. Terra do OLED", 10, "b", "OLED", "GND",
     "GND da XIAO -> a10", "GND do OLED -> b10", False),
    ("oled-vcc", "02. Alimentacao do OLED", 11, "b", "OLED", "VCC",
     "3V3 da XIAO -> a11", "VCC do OLED -> b11", False),
    ("oled-sda", "03. Dados do OLED", 12, "b", "OLED", "SDA",
     "D0 / GPIO1 da XIAO -> a12", "SDA do OLED -> b12", False),
    ("oled-scl", "04. Clock do OLED", 13, "b", "OLED", "SCL",
     "D1 / GPIO2 da XIAO -> a13", "SCL do OLED -> b13", False),
    ("amp-gnd", "05. Terra do amplificador", 10, "c", "MAX98357", "GND",
     "Manter GND da XIAO -> a10", "GND do MAX98357 -> c10", True),
    ("amp-vin", "06. Alimentacao do amplificador", 15, "b", "MAX98357", "VIN",
     "5V da XIAO -> a15", "VIN do MAX98357 -> b15", False),
    ("amp-bclk", "07. Clock de audio", 16, "b", "MAX98357", "BCLK",
     "D6 / GPIO43 da XIAO -> a16", "BCLK do MAX98357 -> b16", False),
    ("amp-lrc", "08. Canal de audio", 17, "b", "MAX98357", "LRC / LRCK",
     "D4 / GPIO5 da XIAO -> a17", "LRC / LRCK do MAX98357 -> b17", False),
    ("amp-din", "09. Dados de audio", 18, "b", "MAX98357", "DIN",
     "D8 / GPIO7 da XIAO -> a18", "DIN do MAX98357 -> b18", False),
]


def text(x, y, value, size=12, bold=False, anchor="start", color="#222"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{"bold" if bold else "normal"}" fill="{color}">'
            f'{escape(value)}</text>')


def rect(x, y, w, h, fill=GRAY, stroke="#666", rx=6):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')


def line(x1, y1, x2, y2, color="#666", width=2, dash=""):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{width}"'
            + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")


def svg(body, height=440):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 {height}" '
            f'font-family="{FONT}"><rect width="680" height="{height}" fill="white"/>'
            + body + "</svg>")


def hole(col, row):
    index = "abcdefghij".index(col)
    return 222 + index * 19 + (25 if index >= 5 else 0), 83 + (row - 10) * 23


def breadboard(active=(), ports=()):
    body = rect(188, 39, 280, 356, "#f5f5f5", "#888")
    body += rect(307, 65, 17, 310, "#e4e4e4", "#bbb", 2)
    for col in "abcdefghij":
        x, _ = hole(col, 10)
        body += text(x, 58, col.upper(), 11, True, "middle")
    for row in range(10, 23):
        _, y = hole("a", row)
        body += text(204, y + 4, str(row), 10, anchor="end")
        body += text(452, y + 4, str(row), 10)
        if row in active:
            body += rect(213, y - 9, 94, 18, YELLOW, "#d6b656", 4)
        for col in "abcdefghij":
            x, _ = hole(col, row)
            body += f'<circle cx="{x}" cy="{y}" r="3" fill="white" stroke="#777"/>'
    for col, row, label in ports:
        x, y = hole(col, row)
        body += f'<circle cx="{x}" cy="{y}" r="6" fill="{COLORS.get(row, "#2563a6")}" stroke="white"/>'
        if label:
            body += text(x, y - 12, label, 10, True, "middle")
    return body


def wire_diagram(row, column, module, pin, reuse=False):
    _, y = hole("a", row)
    color = COLORS[row]
    body = text(340, 23, "SEM USB, SEM BATERIA, SEM FONTE DOS MOTORES", 13, True, "middle", "#a61b1b")
    body += breadboard([row], [("a", row, ""), (column, row, "")])
    body += rect(8, y - 29, 162, 58, BLUE, "#6c8ebf")
    body += text(89, y - 9, "PINO DA XIAO", 11, True, "middle")
    body += text(89, y + 13, NETS[row][0], 15, True, "middle")
    body += rect(490, y - 29, 181, 58, GREEN, "#82b366")
    body += text(580, y - 9, module, 11, True, "middle")
    body += text(580, y + 13, pin, 15, True, "middle")
    ax, _ = hole("a", row)
    bx, _ = hole(column, row)
    body += line(170, y, ax, y, color, 3, "5,3" if reuse else "")
    body += line(bx, y, bx, y + 12, color, 3)
    body += line(bx, y + 12, 480, y + 12, color, 3)
    body += line(480, y + 12, 480, y, color, 3)
    body += line(480, y, 490, y, color, 3)
    body += text(70, 407, f"XIAO -> A{row}", 12, True)
    body += text(430, 407, f"{module} -> {column.upper()}{row}", 12, True)
    body += text(340, 430, "Caixas = nomes dos pinos. NAO mostram a ordem fisica dos conectores.", 11, False, "middle")
    return svg(body)


def basics_diagram():
    body = breadboard([10, 12], [("a", 10, ""), ("e", 10, ""), ("f", 10, ""), ("a", 12, "")])
    body += rect(10, 60, 160, 95, GREEN, "#82b366")
    for n, value in enumerate(["A10, B10, C10,", "D10 e E10:", "MESMA conexao"]):
        body += text(90, 85 + n * 23, value, 12, True, "middle")
    body += line(170, 88, 215, 83, "#2e7d32", 2)
    body += rect(490, 60, 180, 95, RED, "#b85450")
    for n, value in enumerate(["F10 ate J10:", "OUTRA conexao", "Separada pelo vao"]):
        body += text(580, 85 + n * 23, value, 12, True, "middle")
    body += line(490, 88, hole("f", 10)[0], 83, "#b85450", 2)
    body += rect(10, 190, 160, 86, YELLOW, "#d6b656")
    for n, value in enumerate(["A10 e A12:", "NAO sao ligados", "por dentro"]):
        body += text(90, 215 + n * 21, value, 12, True, "middle")
    body += text(340, 420, "Recorte de uma protoboard comum. Conferir letras, numeros e continuidade.", 11, anchor="middle")
    return svg(body)


def no_short_diagram():
    body = text(340, 30, "DOIS PINOS DIFERENTES NA MESMA TIRA = CURTO", 15, True, "middle", "#a61b1b")
    for x, good in [(22, False), (362, True)]:
        body += rect(x, 60, 292, 305, GREEN if good else RED, "#82b366" if good else "#b85450")
        body += text(x + 146, 90, "CERTO: LINHAS DIFERENTES" if good else "ERRADO: MESMA LINHA", 12, True, "middle")
        for row in range(2):
            y = 160 + row * 80
            body += line(x + 50, y, x + 240, y, "#777", 9)
            for col in range(5):
                body += f'<circle cx="{x + 50 + col * 47}" cy="{y}" r="5" fill="white" stroke="#333"/>'
        body += text(x + 50, 140, "GND", 13, True, "middle")
        body += text(x + 240, 220 if good else 140, "3V3", 13, True, "middle")
        body += line(x + 50, 145, x + 50, 160, "#333", 3)
        body += line(x + 240, 225 if good else 145, x + 240, 240 if good else 160, "#007c57", 3)
        body += text(x + 146, 302, "Cada sinal tem sua propria tira." if good else "A tira une GND e 3V3.", 12, True, "middle")
    body += text(340, 407, "Nao apoiar pinos soltos sem solda para fingir que o contato esta pronto.", 12, anchor="middle")
    return svg(body)


def rails_diagram():
    body = text(340, 30, "NESTE LAYOUT, NAO USAMOS OS BARRAMENTOS LATERAIS", 14, True, "middle")
    for x, color, name in [(95, "#b42318", "+"), (155, "#2563a6", "-")]:
        body += text(x, 65, name, 23, True, "middle", color)
        body += line(x, 80, x, 190, color, 4)
        body += line(x, 230, x, 340, color, 4)
        for y in range(90, 341, 25):
            if 190 < y < 230:
                continue
            body += f'<circle cx="{x}" cy="{y}" r="5" fill="white" stroke="#555"/>'
    body += rect(255, 82, 395, 100, YELLOW, "#d6b656")
    for i, value in enumerate(["Uma faixa colorida nao cria energia.", "Alguns barramentos sao interrompidos no meio.", "Os dois lados nao sao unidos automaticamente."]):
        body += text(275, 110 + i * 25, value, 12)
    body += line(160, 211, 255, 211, "#b85450", 2, "5,4")
    body += text(273, 217, "Possivel interrupcao: medir sem energia.", 12, True)
    body += rect(255, 255, 395, 95, BLUE, "#6c8ebf")
    for i, value in enumerate(["Usaremos A10-E10 como ponto GND.", "A11-E11 sera 3V3. A15-E15 sera 5V.", "Nenhuma ponte entre essas tres linhas."]):
        body += text(275, 283 + i * 25, value, 12, i == 2)
    return svg(body)


def speaker_diagram():
    body = rect(30, 95, 250, 225, BLUE, "#6c8ebf")
    body += text(155, 132, "MAX98357", 19, True, "middle")
    body += text(245, 202, "SPK+", 16, True, "end")
    body += text(245, 265, "SPK-", 16, True, "end")
    body += '<circle cx="540" cy="226" r="95" fill="#f5f5f5" stroke="#666" stroke-width="3"/>'
    body += '<circle cx="540" cy="226" r="55" fill="#dae8fc" stroke="#6c8ebf" stroke-width="2"/>'
    body += text(540, 224, "UM FALANTE", 13, True, "middle")
    body += text(540, 244, "4 ohms / 3 W", 13, False, "middle")
    body += line(280, 196, 445, 196, "#2563a6", 4)
    body += line(280, 259, 445, 259, "#2563a6", 4)
    body += text(340, 385, "Nenhum dos dois fios do falante vai para GND.", 16, True, "middle", "#a61b1b")
    body += text(340, 416, "Bornes SPK+ e SPK- sao SAIDA de audio, nao alimentacao.", 12, False, "middle")
    return svg(body)


def power_diagram():
    body = rect(15, 40, 195, 70, BLUE, "#6c8ebf") + text(112, 80, "USB -> XIAO", 17, True, "middle")
    body += rect(430, 40, 230, 70, YELLOW, "#d6b656") + text(545, 70, "Fonte externa 5V", 16, True, "middle")
    body += text(545, 94, "Somente para motores", 12, False, "middle")
    body += rect(15, 190, 195, 65, GREEN, "#82b366") + text(112, 227, "OLED + audio", 17, True, "middle")
    body += rect(430, 190, 230, 65, GREEN, "#82b366") + text(545, 227, "Dois servos", 17, True, "middle")
    body += line(112, 110, 112, 190, "#2563a6", 3)
    body += line(545, 110, 545, 145, "#b42318", 3)
    body += rect(485, 145, 120, 25, RED, "#b85450") + text(545, 163, "CORTE FISICO", 10, True, "middle")
    body += line(545, 170, 545, 190, "#b42318", 3)
    body += line(210, 305, 430, 305, "#333", 3)
    body += text(320, 293, "GND de referencia comum", 13, True, "middle")
    body += text(320, 340, "Corrente dos motores retorna direto a fonte externa.", 13, False, "middle")
    body += text(320, 378, "NAO unir os positivos. LiPo fora do circuito.", 17, True, "middle", "#a61b1b")
    body += text(320, 413, "Diagrama de arquitetura: nao e instrucao para ligar motores agora.", 12, False, "middle")
    return svg(body)


def summary_diagram():
    body = text(340, 24, "LADO A-E: CADA LINHA E UM SINAL DIFERENTE", 14, True, "middle")
    body += breadboard(list(NETS))
    for row, (pin, name) in NETS.items():
        _, y = hole("a", row)
        body += text(175, y + 4, pin, 12, True, "end", COLORS[row])
        body += text(485, y + 4, name, 12, True, color=COLORS[row])
    body += text(340, 423, "F-J fica vazio. Linhas 14 e 19 ficam vazias. Sem barramentos laterais.", 11, anchor="middle")
    return svg(body)


def button_diagram():
    body = rect(20, 50, 280, 300, YELLOW, "#d6b656")
    body += text(160, 80, "EXEMPLO DE BOTAO 4 PINOS", 13, True, "middle")
    points = [(80, 145), (80, 270), (240, 145), (240, 270)]
    for x, y in points:
        body += f'<circle cx="{x}" cy="{y}" r="9" fill="white" stroke="#666" stroke-width="2"/>'
    body += line(80, 145, 80, 270, "#333", 4)
    body += line(240, 145, 240, 270, "#333", 4)
    body += line(80, 207, 135, 207, "#333", 3)
    body += line(135, 207, 215, 180, "#333", 3)
    body += line(215, 207, 240, 207, "#333", 3)
    body += text(80, 310, "PAR A", 13, True, "middle")
    body += text(240, 310, "PAR B", 13, True, "middle")
    for i, value in enumerate(["Confirmar os pares com multimetro.", "A orientacao real pode ser diferente.", "D7/GPIO44 -> A20.", "Um contato do PAR A -> B20.", "Um contato do PAR B -> D10 (GND).", "Solto: A e B separados.", "Pressionado: A e B unidos."]):
        body += text(320, 100 + i * 32, value, 12, i in [2, 3, 4])
    body += text(340, 407, "Se nao souber identificar os pares, deixar o botao desconectado.", 12, True, "middle", "#a61b1b")
    return svg(body)


def xiao_diagram():
    body = text(340, 24, "VISTA DE CIMA DA PLACA BASE: USB PARA CIMA", 15, True, "middle")
    body += rect(232, 60, 216, 315, BLUE, "#6c8ebf")
    body += rect(290, 40, 100, 65, GRAY, "#666")
    body += text(340, 80, "USB-C", 16, True, "middle")
    body += rect(265, 150, 150, 170, GRAY, "#888")
    body += text(340, 220, "XIAO", 21, True, "middle")
    body += text(340, 245, "ESP32-S3", 15, True, "middle")
    left = ["D0 / GPIO1", "D1 / GPIO2", "D2 / GPIO3", "D3 / GPIO4",
            "D4 / GPIO5", "D5 / GPIO6", "D6 / GPIO43"]
    right = ["5V / VBUS", "GND", "3V3", "D10 / GPIO9",
             "D9 / GPIO8", "D8 / GPIO7", "D7 / GPIO44"]
    for index, (a, b) in enumerate(zip(left, right)):
        y = 124 + index * 36
        body += rect(223, y - 9, 23, 18, YELLOW, "#d6b656", 3)
        body += rect(434, y - 9, 23, 18, YELLOW, "#d6b656", 3)
        body += text(211, y + 4, a, 15, True, "end")
        body += text(470, y + 4, b, 15, True)
    body += text(340, 408, "Redesenho funcional da pinagem Seeed; nao esta em escala.", 12, anchor="middle")
    body += text(340, 430, "Nao espelhar. A expansao Sense pode esconder parte da placa base.", 12, anchor="middle")
    return svg(body)


def jumper_diagram():
    body = rect(35, 145, 110, 75, "#333", "#333")
    body += rect(27, 159, 24, 47, "white", "#666", 2)
    body += line(145, 182, 490, 182, "#2563a6", 12)
    body += rect(490, 145, 85, 75, "#333", "#333")
    body += rect(575, 177, 64, 10, "#aaa", "#777", 1)
    body += text(90, 110, "FEMEA: ENCAIXE", 14, True, "middle")
    body += text(557, 110, "MACHO: PINO", 14, True, "middle")
    body += text(90, 265, "No header macho", 13, True, "middle")
    body += text(90, 290, "ja soldado do modulo", 13, False, "middle")
    body += text(557, 265, "No furo da", 13, True, "middle")
    body += text(557, 290, "protoboard", 13, False, "middle")
    body += text(340, 365, "Ilustracao de tipo de conector, nao de um produto especifico.", 12, anchor="middle")
    body += text(340, 408, "Header solto encostado no furo da placa NAO substitui solda.", 13, True, "middle", "#a61b1b")
    return svg(body)


PAGES = []


def add(title, body, image=None, checkpoint=""):
    PAGES.append((title, body, image, checkpoint))


def compose():
    add("Antes de comecar: o que este guia prova",
        "Este e o manual visual da montagem ELETRICA INICIAL: protoboard, OLED, amplificador e falante. "
        "O firmware compilou; nao tenho as pecas em bancada e nao posso comprovar seu funcionamento fisico a distancia.\n\n"
        "Os desenhos sao originais, explicativos e nao fotografias das suas pecas. "
        "As coordenadas foram escolhidas para distribuir os sinais em uma protoboard comum A-J. "
        "Precisam coincidir com as letras/numeros e a continuidade da unidade real.\n\n"
        "A XIAO e os modulos ficarao FORA da protoboard, sobre suporte nao condutivo. "
        "So os fios entram nos furos indicados. Isso evita inventar a posicao de encaixe da placa ou esconder furos debaixo dela.\n\n"
        "Motores: apenas planejamento neste PDF, nao ligacao energizada. LiPo: desconectada em todas as etapas. "
        "O guia de execucao de 16 paginas continua sendo a referencia para nuvem e ensaios posteriores.\n\n"
        "Se sua placa ou os nomes dos pinos diferirem, pare. Nao escolha um pino por parecer estar na posicao do desenho.",
        checkpoint="Pode seguir: leitura e preparacao sem energia. Nao pode: energizar pecas que nao foram conferidas.")
    add("1. Aprender o mapa dos furos",
        "Segure a protoboard com as letras A-J legiveis. Numero = linha; letra = coluna. "
        "A10 significa o furo da coluna A, linha 10. Neste recorte mostramos somente 10 a 22.\n\n"
        "A10-B10-C10-D10-E10 sao uma unica conexao interna. "
        "F10-G10-H10-I10-J10 formam OUTRA conexao. O vao no meio separa os dois grupos.\n\n"
        "A10 NAO e ligado a A11. Para unir linhas diferentes seria preciso um fio; neste layout nao faremos isso.",
        "breadboard-basics", "Aponte A10, E10, F10 e A11 antes de continuar.")
    add("2. Entender os barramentos laterais",
        "As faixas compridas marcadas + e - sao chamadas barramentos. Elas nao geram eletricidade. "
        "Podem ter interrupcao no meio e os lados esquerdo/direito podem ser independentes.\n\n"
        "Para reduzir as chances de erro, este manual NAO usa os barramentos. "
        "Vamos usar somente as tiras A-E de cada linha numerada. Nao acrescente pontes nas faixas + e -.",
        "breadboard-rails", "Deixe todas as faixas laterais sem fios.")
    add("3. Praticar continuidade, sem energia",
        "Use uma protoboard VAZIA, sem placa, USB, bateria ou fontes. "
        "No multimetro, ponta preta em COM; vermelha no borne V/ohm conforme o manual. "
        "Nao usar a entrada de corrente A/mA.\n\n"
        "1. Selecione continuidade. Encoste uma ponta na outra para conhecer o sinal do aparelho.\n"
        "2. Teste A10 e E10: devem estar ligados.\n"
        "3. Teste A10 e F10: devem estar separados.\n"
        "4. Teste A10 e A11: devem estar separados.\n\n"
        "Se as pontas nao entrarem, usar dois jumpers macho como extensoes, sem forcar o furo. "
        "Teste com cuidado para as pontas nao encostarem entre si.\n\n"
        "Se os resultados forem diferentes, nao use as coordenadas deste manual ate entender sua protoboard. "
        "Nao remova a base adesiva para abrir a peca.", "breadboard-basics",
        "Na protoboard vazia: A10-E10 ligado; A10-F10 e A10-A11 separados.")
    add("4. Evitar o erro que causa curto",
        "Dois pinos diferentes nao podem cair na mesma tira interna por acidente. "
        "Por exemplo: GND em A10 e 3V3 em E10 ficam unidos e causam curto quando houver energia.\n\n"
        "Nao force as duas fileiras de uma placa sobre uma regiao sem conhecer quais furos ficam ligados. "
        "Neste manual a placa fica fora da protoboard e cada pino e levado por um fio ao seu ponto.",
        "avoid-short", "GND na linha 10; 3V3 na 11; 5V na 15. Nunca unir essas linhas.")
    add("5. Pecas, conectores e fios certos",
        "Separar: XIAO ESP32-S3 SENSE com expansao de camera/microfone; OLED SH1106; "
        "um MAX98357; um falante 4 ohms/3 W; protoboard A-J; multimetro; cabo USB de dados.\n\n"
        "Para esta montagem fora da protoboard, voce precisa de jumpers FEMEA-MACHO: "
        "o lado femea encaixa no pino macho ja soldado do modulo; o lado macho entra na protoboard. "
        "Confira seu pacote: ter jumpers nao garante que ele inclua esse tipo.\n\n"
        "Se uma peca tiver somente furos sem pinos soldados, ela ainda nao esta pronta para receber o jumper. "
        "Um header encostado sem solda NAO e conexao confiavel. Nao usar a XIAO como primeira pratica de solda. "
        "Pedir ajuda presencial para soldar e inspecionar, ou obter conectores ja montados.\n\n"
        "Fixar placas em suporte nao condutivo sem tapar microfone, lente ou antena. "
        "Nao apoiar pinos sobre metal, parafusos ou fios soltos.\n\n"
        "Cores ajudam a organizar, mas nao definem a funcao. Etiquetar as duas pontas de cada fio pelo nome do sinal.",
        checkpoint="Se faltar jumper femea-macho ou header soldado, parar a montagem eletrica nessa peca.")
    add("Escolher o tipo certo de jumper",
        "O cabo deste desenho tem uma ponta femea e outra macho. "
        "A ponta femea recebe o pino metalico do header; a ponta macho entra no furo da protoboard.\n\n"
        "Pegar pelo conector plastico, nao puxar pelo fio. Encaixar sem forcar. "
        "Nao deixar parte metalica exposta encostar no pino vizinho.\n\n"
        "Se o modulo nao tiver header macho ja soldado, obter a conexao correta antes. "
        "Nao prender um fio solto dentro de um furo metalizado da placa.",
        "jumper-connectors", "Identifique as duas pontas antes de usar o primeiro cabo.")
    add("Localizar os pinos na XIAO",
        "O desenho mostra a placa base pelo lado dos componentes, com USB em cima. "
        "Nao mostra o lado de baixo: olhar por baixo espelha esquerda/direita.\n\n"
        "Compare com a pinagem oficial Seeed e a unidade recebida. "
        "Nao force nem retire a expansao Sense para encontrar um nome; use a documentacao e as inscricoes acessiveis.\n\n"
        "ATENCAO: neste firmware o OLED usa D0 e D1. "
        "Embora tutoriais genericos chamem D4/D5 de SDA/SCL, NAO os use para o OLED aqui. "
        "D4 e audio LRC; D5 sera sinal TILT.\n\n"
        "Se comprar outra placa, como ESP32-S3 Plus ou uma ESP32-CAM, este mapa nao se aplica.",
        "xiao-top-pinout", "D0 e GPIO1 sao nomes do mesmo pino; D1 e GPIO2 tambem.")
    add("6. Preparar o layout escolhido",
        "Nao encaixe XIAO, OLED ou MAX98357 nos furos: eles ficam apoiados e presos fora da protoboard. "
        "Os quadros dos proximos desenhos sao etiquetas dos pinos, NAO a ordem real do conector.\n\n"
        "Escolher uma protoboard com A-J e pelo menos 22 linhas numeradas. "
        "So usar A-E. F-J e barramentos ficam vazios. "
        "Deixar linhas 14 e 19 vazias para separacao visual.\n\n"
        "Em cada etapa: primeiro ligar o fio da XIAO ao furo A indicado; "
        "depois ligar o pino do modulo ao outro furo da MESMA linha. "
        "A tira interna faz a ponte entre eles. Nao inserir dois fios no mesmo furo.\n\n"
        "Todos os passos de ligacao: USB fora, LiPo fora, fonte dos motores fora.",
        "layout-summary", "Confirme as inscricoes nas pecas. Nao use pino 'vizinho' como substituto.")
    for name, title, row, col, module, pin, first, second, reuse in WIRES:
        body = (f"1. {first}. " + ("Esse fio ja existe; NAO adicionar outro no mesmo furo.\n" if reuse else "Usar um jumper.\n")
                + f"2. {second}. Usar outro jumper.\n"
                + f"3. Ler o numero {row} nos dois furos. Eles devem estar no grupo A-E, nao do outro lado do vao.\n\n"
                + f"Por que funciona: A{row} e {col.upper()}{row} sao ligados pela tira metalica interna. "
                "Nao e necessario colocar fio entre eles.\n\n")
        if row == 11:
            body += "OLED VCC recebe 3V3, NAO 5V. Nao confundir o nome VCC do display com VIN do amplificador.\n\n"
        if row == 15:
            body += "O 5V vem do pino da XIAO quando alimentada por USB. NAO conectar fonte externa nessa linha.\n\n"
        if row == 10 and reuse:
            body += "Agora A10 = GND da XIAO, B10 = GND do OLED, C10 = GND do amplificador. Sao tres furos diferentes.\n\n"
        body += "Se o pino nao estiver identificado, pare. Fios cruzados no desenho nao significam conexao; so as pontas entram nos furos marcados."
        add(title, body, name, f"Conferido: {first}; {second}. Continuar com tudo DESLIGADO.")
    add("10. Ligar um unico alto-falante",
        "O falante NAO usa as linhas GND, 3V3 ou 5V da protoboard. "
        "Ele recebe dois fios diretamente das saidas do amplificador.\n\n"
        "1. Ligar um terminal do falante a SPK+ do MAX98357.\n"
        "2. Ligar o outro terminal do MESMO falante a SPK-.\n"
        "3. Se houver borne de parafuso: prender apenas o trecho desencapado dentro do borne, "
        "sem filamentos para fora. Puxar suavemente para conferir que ficou preso.\n\n"
        "Nao unir os dois terminais, nao ligar SPK- ao GND e nao colocar dois falantes em paralelo. "
        "Se as inscricoes da sua unidade forem outras, confirmar antes de conectar.",
        "speaker-output", "So um falante. Nenhum fio do falante vai ao GND.")
    add("11. Conferir todos os fios antes do USB",
        "Leia em voz alta e siga cada fio com o dedo, sem energia:\n\n"
        "A10 XIAO GND; B10 OLED GND; C10 MAX98357 GND.\n"
        "A11 XIAO 3V3; B11 OLED VCC.\n"
        "A12 XIAO D0/GPIO1; B12 OLED SDA.\n"
        "A13 XIAO D1/GPIO2; B13 OLED SCL.\n"
        "A15 XIAO 5V; B15 MAX98357 VIN.\n"
        "A16 XIAO D6/GPIO43; B16 MAX98357 BCLK.\n"
        "A17 XIAO D4/GPIO5; B17 MAX98357 LRC/LRCK.\n"
        "A18 XIAO D8/GPIO7; B18 MAX98357 DIN.\n\n"
        "Nao alterar SD/GAIN do AITRIP por adivinhacao. Manter a configuracao de fabrica. "
        "A camera/microfone usam a expansao Sense; nao recebem jumpers desta tabela.\n\n"
        "Fotografar de cima com as inscricoes legiveis. Se nao souber confirmar uma ligacao, "
        "nao energizar para experimentar. Uma revisao remota da foto tambem nao substitui medicao.",
        "layout-summary", "Sem servos, sem LiPo, sem microSD. Sem pontes de 3V3/5V para GND.")
    add("12. Gravar o firmware: computador",
        "Baixar o ZIP da pre-release v0.1.0 de ricmmartins/family-ai-robot. "
        "Extrair em C:\\robot, sem misturar arquivos de outros tutoriais.\n\n"
        "Com Python 3.11 ou 3.12 instalado, abrir PowerShell e executar, uma linha por vez:\n\n"
        "Set-Location C:\\robot\n"
        "python -m venv .venv\n"
        ".\\.venv\\Scripts\\python.exe -m pip install esptool==5.6.0\n\n"
        "Parar se um comando falhar. O binario ja compilou; nao e necessario instalar o SDK para grava-lo.\n\n"
        "Apos revisao eletrica: conectar somente USB de dados a XIAO, sem motores nem bateria. "
        "Identificar a porta COM no Gerenciador de Dispositivos. "
        "Se necessario, com USB desconectado, segurar BOOT, conectar USB e soltar BOOT.\n\n"
        "Trocar COM5 pela porta real:\n"
        "powershell -ExecutionPolicy Bypass -File .\\flash.ps1 -Port COM5\n\n"
        "O script confere SHA256 e grava a imagem mesclada em 0x0. Nao usar o binario AI Pin. "
        "Em computador gerenciado, seguir as politicas; nao contornar restricoes.",
        checkpoint="Gravacao sem erro so comprova transferencia. Ainda nao comprova funcionamento do conjunto.")
    add("13. Primeiro teste energizado",
        "Este teste exige nova XIAO Sense com expansao corretamente encaixada e a montagem eletrica "
        "ja conferida. Se isso ainda nao foi possivel, PARE ANTES DO USB.\n\n"
        "1. Manter fonte dos motores e LiPo desconectadas.\n"
        "2. Usar cabo USB de dados e fonte/porta adequada. Comecar com audio baixo; "
        "uma porta USB fraca pode nao sustentar os picos do conjunto.\n"
        "3. Abrir o log no PowerShell e pressionar RESET:\n\n"
        ".\\.venv\\Scripts\\python.exe -m serial.tools.miniterm --rts 0 --dtr 0 COM5 115200\n\n"
        "4. Procurar 'SH1106 initialized' e 'Camera ready'. "
        "O display deve mostrar interface sem deslocamento ou corte. Fechar monitor com Ctrl+].\n\n"
        "Se houver calor anormal, cheiro, fumaca, erro fatal ou reinicializacoes: desconectar USB. "
        "Nao mexer em fios com energia nem insistir ligando repetidamente.\n\n"
        "Nao ligar so o OLED e interpretar falha da camera como defeito do display. "
        "O firmware atual exige a expansao da camera e verifica seu sensor na inicializacao.\n\n"
        "Falta de audio deve ser investigada pelos pinos e pela documentacao do modulo AITRIP. "
        "Nao improvisar pontes SD/GAIN.",
        checkpoint="Avancar so com display legivel, camera inicializada e sem resets/aquecimento anormal.")
    add("14. Wi-Fi, voz e foto: testes separados",
        "Usar primeiro a rede domestica 2,4 GHz autorizada. "
        "Seguir o nome da rede e portal mostrados no OLED/log; nao assumir um IP fixo.\n\n"
        "Abrir xiaozhi.me e seguir o fluxo atual de conta/ativacao usando o codigo do dispositivo. "
        "Nao publicar senha, token ou codigo de conta. A ativacao desta placa personalizada ainda nao foi testada.\n\n"
        "Configurar idioma da IA e voz para ingles. Clique curto no BOOT alterna a conversa conforme o estado; "
        "nao ha wake word nesta primeira versao.\n\n"
        "Teste voz: 'Hello. Please answer in English.' Fazer dez interacoes curtas, "
        "confirmando que ela ouve e responde sem reset.\n\n"
        "Teste foto: mostrar um objeto simples e pedir "
        "'Take a photo and describe the object in front of you.' "
        "Nao mostrar rostos, documentos ou telas pessoais.\n\n"
        "Visao precisa de configuracao enviada pelo backend. Voz funcionando NAO comprova visao. "
        "Se falhar, guardar erro do log; nao trocar fios ao acaso.\n\n"
        "Os testes sao criterios de aceitacao A EXECUTAR. Nao foram feitos remotamente nestas pecas.",
        checkpoint="Registrar separadamente: ativacao; voz; fotografia; descricao. Nao marcar tudo como aprovado de uma vez.")
    add("15. Botao de cabeca: preparacao opcional",
        "Deixar motores e suas fontes desconectados. Se o botao tiver quatro pernas, "
        "primeiro identificar os dois pares com continuidade, fora do circuito e sem energia.\n\n"
        "Um par ja tem continuidade sem pressionar. Os dois pares so devem se unir ao pressionar. "
        "O desenho mostra uma possibilidade, NAO a orientacao garantida da sua peca.\n\n"
        "1. D7/GPIO44 da XIAO -> A20.\n"
        "2. Um contato do primeiro par -> B20.\n"
        "3. Um contato do outro par -> D10, GND ja existente.\n\n"
        "Manter o botao fora da protoboard se seus pinos nao couberem sem curto. "
        "Nao tentar encaixa-lo conforme o desenho sem confirmar os pares. "
        "O codigo usa pull-up interno; nao adicionar resistor ou ligacao a 5V por conta propria.",
        "head-button", "Sem identificar os pares com certeza, nao instalar o botao. Nao habilitar motores agora.")
    add("16. Motores: entender antes de montar",
        "Esta pagina explica a separacao de alimentacao. Nao e desenho de montagem em furos para os servos, "
        "pois os conectores, fonte e corte fisico reais ainda precisam ser identificados.\n\n"
        "A fonte externa alimenta os dois servos; seus retornos vao direto a essa fonte. "
        "Um fio dedicado de referencia une GND da fonte a GND da XIAO. "
        "Nunca fazer corrente dos motores passar pela XIAO ou pela linha GND fina da protoboard.\n\n"
        "Sinais previstos: PAN em D3/GPIO4; TILT em D5/GPIO6. "
        "A aceitacao de sinal 3,3V precisa ser verificada nos servos reais.\n\n"
        "Nao ligar o positivo da fonte externa a A15 nem ao 5V da XIAO. "
        "Nao colocar capacitor invertido nem conectar a LiPo. "
        "A etapa seguinte exige fonte regulada adequada, bornes/fios de potencia, "
        "interruptor de corte e conferencia de polaridade.",
        "separate-power", "PARADA DOS MOTORES: fonte, conectores e mecanica ainda exigem identificacao e revisao.")
    add("17. Montagem fisica e pontos de parada",
        "No primeiro corpo, somente o OLED fica na cabeca movel. Camera, XIAO, amplificador e falante ficam na base fixa. "
        "Portanto virar a cabeca NAO gira a camera.\n\n"
        "Planejar suporte leve para OLED, base estavel e folga dos quatro fios. "
        "Nao colar o OLED no pan-tilt antes de centralizar/testar os servos sem carga. "
        "Nao forcar os eixos nem ajustar bracos com energia.\n\n"
        "Este manual entrega diagramas de protoboard e ligacoes centrais. "
        "Nao entrega prova de funcionamento fisico nem desenho fiel dos conectores ainda nao fotografados.\n\n"
        "PARE se: nao ha headers soldados; faltam jumpers corretos; nao sabe identificar pino; "
        "protoboard nao corresponde ao mapa; teste de continuidade diverge; polaridade nao e clara; "
        "fonte entra em protecao; ha resets, aquecimento ou mecanica presa.\n\n"
        "Para fechar a montagem exata: fotos de cima e de lado das pecas desligadas, "
        "inscricoes legiveis, modelo da camera/servos e fonte dos motores. "
        "Nao precisa enviar comprovantes, endereco ou fotos de pessoas.\n\n"
        "Proximo objetivo verificavel: ligar o nucleo OLED/audio/camera sem motores e registrar "
        "os resultados individuais da pagina de testes.",
        checkpoint="Nao chamar o robo de funcional ate testar fisicamente cada subsistema e a nuvem.")
    add("18. Fontes e significado das cores",
        "Desenhos originais gerados para este projeto em 28/10/2026. "
        "Sao diagramas de ligacao, nao fotos nem certificacao de seguranca.\n\n"
        "Preto/cinza escuro: GND. Verde: 3V3. Vermelho: 5V. Azul: sinais. "
        "As cores dos jumpers reais podem diferir; o NOME e o DESTINO identificam o fio.\n\n"
        "Protoboard: grupos de cinco, vao central e barramentos:\n"
        "https://learn.sparkfun.com/tutorials/how-to-use-a-breadboard/all\n\n"
        "XIAO ESP32-S3 Sense, identificacao/pinagem oficial:\n"
        "https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/\n\n"
        "Saida do MAX98357, referencia funcional; conferir AITRIP real:\n"
        "https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/pinouts\n\n"
        "Software e codigo exato dos pinos do projeto:\n"
        "https://github.com/ricmmartins/family-ai-robot\n\n"
        "Base de software:\n"
        "https://github.com/78/xiaozhi-esp32\n\n"
        "Comprovado: compilacao/link do firmware publicado. "
        "Nao comprovado: montagem, funcionamento nas suas pecas, ativacao em nuvem e uso escolar.")


def wrap(value, width, size):
    result = []
    for paragraph in value.splitlines():
        current = ""
        for word in paragraph.split():
            trial = (current + " " + word).strip()
            if fitz.get_text_length(trial, fontsize=size) > width:
                if current:
                    result.append(current)
                current = word
                if fitz.get_text_length(word, fontsize=size) > width:
                    raise ValueError(f"Unbreakable text: {word}")
            else:
                current = trial
        result.append(current)
    return result


def generate():
    ASSETS.mkdir(parents=True, exist_ok=True)
    drawings = {
        "breadboard-basics": basics_diagram(),
        "breadboard-rails": rails_diagram(),
        "avoid-short": no_short_diagram(),
        "layout-summary": summary_diagram(),
        "speaker-output": speaker_diagram(),
        "head-button": button_diagram(),
        "separate-power": power_diagram(),
        "xiao-top-pinout": xiao_diagram(),
        "jumper-connectors": jumper_diagram(),
    }
    for name, _, row, col, module, pin, _, _, reuse in WIRES:
        drawings[name] = wire_diagram(row, col, module, pin, reuse)
    for name, value in drawings.items():
        (ASSETS / f"{name}.svg").write_text(value, encoding="utf-8")
    compose()
    document = fitz.open()
    for index, (title, body, image, checkpoint) in enumerate(PAGES):
        page = document.new_page(width=595, height=842)
        page.draw_rect(fitz.Rect(0, 0, 595, 10), fill=(0.04, 0.32, 0.45), color=None)
        if fitz.get_text_length(title, fontname="hebo", fontsize=18) > 511:
            raise ValueError(f"Title overflow: {title}")
        page.insert_text((42, 43), title, fontsize=18, fontname="hebo", color=(0.04, 0.25, 0.36))
        y = 70
        if image:
            with fitz.open(ASSETS / f"{image}.svg") as vector:
                with fitz.open("pdf", vector.convert_to_pdf()) as rendered:
                    page.show_pdf_page(fitz.Rect(35, 60, 560, 400), rendered, 0)
            y = 414
        lines = wrap(body, 507, 10.5)
        for value in lines:
            if y > 743:
                raise ValueError(f"Page body overflow: {index + 1}, {title}")
            page.insert_text((44, y), value, fontsize=10.5)
            y += 14
        if checkpoint:
            bounds = fitz.Rect(36, 758, 559, 801)
            page.draw_rect(bounds, fill=(1, 0.95, 0.80), color=(0.84, 0.72, 0.34))
            fit = page.insert_textbox(bounds + (8, 6, -8, -4), "CONFERENCIA: " + checkpoint, fontsize=9.5)
            if fit < 0:
                raise ValueError(f"Checkpoint overflow: {title}")
        page.insert_text((42, 824), "FAMILY AI ROBOT | Manual visual | 28/10/2026 | Hardware ainda nao testado", fontsize=8)
        page.insert_text((514, 824), f"{index + 1}/{len(PAGES)}", fontsize=8)
    document.set_toc([[1, title, index + 1] for index, (title, _, _, _) in enumerate(PAGES)])
    document.set_metadata({"title": "Family AI Robot - Guia ilustrado para iniciantes", "author": "Family AI Robot"})
    document.save(OUTPUT, garbage=4, deflate=True)
    document.close()
    with fitz.open(OUTPUT) as check:
        assert len(check) == len(PAGES)
        for index, page in enumerate(check):
            for block in page.get_text("dict")["blocks"]:
                for entry in block.get("lines", []):
                    for span in entry["spans"]:
                        x0, y0, x1, y1 = span["bbox"]
                        assert 0 <= x0 < x1 <= 595 and 0 <= y0 < y1 <= 842, (index, span)
        for index in [1, 7, 9, 12]:
            check[index].get_pixmap(matrix=fitz.Matrix(1.2, 1.2)).save(ASSETS / f"preview-{index + 1}.png")
    print(f"{OUTPUT}: {len(PAGES)} pages, {len(drawings)} SVG illustrations; layout checks passed")


if __name__ == "__main__":
    generate()
