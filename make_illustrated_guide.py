"""Generate original wiring illustrations and a beginner PDF; not hardware proof."""
from html import escape
from pathlib import Path
import re
import fitz

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "docs" / "images"
OUTPUT = ROOT / "guia-ilustrado-iniciantes.pdf"
VERSION = "v0.1.2"
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
    body += line(625, 110, 625, 190, "#333", 3)
    body += text(650, 182, "GND", 11, True, "end")
    for x1, y1, x2, y2 in [(210, 100, 260, 100), (260, 100, 260, 305),
                           (260, 305, 400, 305), (400, 305, 400, 100), (400, 100, 430, 100)]:
        body += line(x1, y1, x2, y2, "#333", 3)
    body += text(200, 104, "GND", 10, True, "end")
    body += text(440, 104, "GND", 10, True)
    body += text(330, 293, "Referencia GND", 13, True, "middle")
    body += text(320, 340, "Corrente dos motores retorna direto a fonte externa.", 13, False, "middle")
    body += text(320, 378, "NAO unir os positivos. LiPo fora do circuito.", 17, True, "middle", "#a61b1b")
    body += text(320, 413, "Diagrama de arquitetura: nao e instrucao para ligar motores agora.", 12, False, "middle")
    return svg(body)


def mechanics_diagram():
    body = text(340, 26, "PROPOSTA MECANICA: SEM MEDIDAS OU ENCAIXES CONFIRMADOS", 13, True, "middle")
    body += rect(240, 65, 200, 95, BLUE, "#6c8ebf")
    body += text(340, 103, "OLED MOVEL", 20, True, "middle")
    body += text(340, 134, "leve, sem camera", 13, anchor="middle")
    body += rect(295, 175, 90, 60, YELLOW, "#d6b656")
    body += text(340, 211, "pan-tilt", 15, True, "middle")
    body += line(340, 160, 340, 175, "#666", 3)
    body += line(340, 235, 340, 260, "#666", 3)
    body += '<path d="M 430 155 C 540 175 510 225 435 265" fill="none" stroke="#2563a6" stroke-width="3"/>'
    body += text(565, 240, "Folga nos 4 fios", 12, True, "middle")
    body += rect(65, 260, 550, 125, GREEN, "#82b366")
    body += text(340, 290, "BASE FIXA, ESTAVEL E NAO CONDUTIVA", 16, True, "middle")
    body += rect(90, 310, 220, 48, BLUE, "#6c8ebf")
    body += text(200, 340, "XIAO + CAMERA", 16, True, "middle")
    body += text(455, 340, "Amplificador + falante", 14, True, "middle")
    body += text(340, 422, "Nao dimensiona suporte nem libera montagem energizada dos motores.", 12, anchor="middle")
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


def module_diagram(module):
    body = text(340, 26, "LER O NOME NO MODULO, NAO ADIVINHAR PELA COR DO FIO", 14, True, "middle")
    if module == "OLED":
        body += rect(150, 65, 380, 185, BLUE, "#6c8ebf")
        body += rect(180, 90, 320, 120, "#1c2834", "#666")
        body += text(340, 155, "TELA OLED", 26, True, "middle", "#ffffff")
        for index, name in enumerate(["GND", "VCC", "SCL", "SDA"]):
            x = 200 + index * 90
            body += text(x, 238, name, 15, True, "middle")
            body += rect(x - 5, 250, 10, 40, "#aaa", "#777", 1)
        body += text(340, 335, "Ordem mostrada na foto do anuncio JAMHER enviado.", 13, True, "middle")
        body += text(340, 363, "Conferir as letras na SUA unidade; nao e foto da unidade recebida.", 12, anchor="middle")
        body += text(340, 410, "VCC -> 3V3 | SCL -> D1 | SDA -> D0 | GND -> GND", 14, True, "middle")
    else:
        body += rect(100, 65, 480, 275, BLUE, "#6c8ebf")
        body += text(340, 100, "MAX98357: MAPA DE NOMES", 18, True, "middle")
        for index, (name, value) in enumerate([
            ("VIN", "alimentacao"), ("GND", "terra"), ("BCLK", "clock"),
            ("LRC / LRCK", "canal"), ("DIN", "dados")]):
            y = 145 + index * 37
            body += text(125, y, name, 15, True)
            body += text(270, y, value, 13)
        body += rect(410, 145, 130, 135, YELLOW, "#d6b656")
        body += text(475, 185, "SPK+", 16, True, "middle")
        body += text(475, 225, "SPK-", 16, True, "middle")
        body += text(340, 375, "Caixas agrupam funcoes: NAO sao a ordem fisica dos pinos AITRIP.", 12, True, "middle")
        body += text(340, 405, "Se nao encontrar as inscricoes, nao ligar ate identificar a unidade.", 12, anchor="middle")
    return svg(body)


def headers_diagram():
    body = text(340, 28, "ANTES DO PRIMEIRO JUMPER: O HEADER PRECISA ESTAR SOLDADO", 14, True, "middle")
    body += rect(25, 70, 300, 290, GREEN, "#82b366")
    body += text(175, 103, "CORTE LATERAL GENERICO", 13, True, "middle")
    body += rect(70, 195, 205, 18, BLUE, "#6c8ebf", 1)
    body += text(175, 285, "PLACA", 13, True, "middle")
    for x in [110, 175, 240]:
        body += rect(x - 5, 140, 10, 130, "#aaa", "#777", 1)
        body += rect(x - 20, 214, 40, 20, "#333", "#333", 2)
        body += f'<path d="M {x-16} 195 L {x} 174 L {x+16} 195 Z" fill="#aaa" stroke="#666"/>'
    body += text(175, 305, "Junta une pino + pad da placa.", 12, True, "middle")
    body += rect(350, 70, 305, 290, RED, "#b85450")
    body += text(502, 103, "NAO FUNCIONA ASSIM", 13, True, "middle")
    body += rect(390, 195, 230, 18, BLUE, "#6c8ebf", 1)
    body += rect(498, 130, 10, 135, "#aaa", "#777", 1)
    body += text(502, 302, "Pino apenas encostado no furo.", 12, True, "middle")
    body += text(340, 403, "Confirmar o lado do header para nao bloquear USB, expansao e encaixes.", 12, anchor="middle")
    return svg(body)


def solder_diagram():
    body = text(340, 26, "TREINAR EM PLACA DE PRATICA, NAO NA XIAO", 16, True, "middle")
    body += rect(100, 235, 480, 22, BLUE, "#6c8ebf", 1)
    body += rect(326, 115, 18, 220, "#aaa", "#777", 1)
    body += '<path d="M 300 235 Q 315 230 326 207 L 344 207 Q 355 230 370 235 Z" fill="#aaa" stroke="#666"/>'
    body += '<path d="M 70 95 L 110 75 L 326 226 L 307 235 Z" fill="#666" stroke="#333"/>'
    body += line(535, 105, 350, 218, "#999", 5)
    body += text(90, 55, "FERRO", 14, True)
    body += text(495, 82, "SOLDA", 14, True)
    body += text(340, 365, "Aquecer pino E pad; alimentar a junta, nao so a ponta do ferro.", 13, True, "middle")
    body += text(340, 404, "Depois: tirar o fio de solda, retirar o ferro e deixar esfriar sem mover.", 12, anchor="middle")
    return svg(body)


def cumulative_diagram(include_amp):
    wires = [wire for wire in WIRES if include_amp or wire[4] == "OLED"]
    rows = sorted({wire[2] for wire in wires})
    body = text(340, 23, "CONJUNTO COMPLETO: DIAGRAMA ELETRICO, NAO FOTO", 14, True, "middle")
    ports = [("a", row, "") for row in rows] + [(wire[3], wire[2], "") for wire in wires]
    body += breadboard(rows, ports)
    right_names = {row: f"{'AMP' if module == 'MAX98357' else module} {pin.split(' / ')[0]}"
                   for _, _, row, col, module, pin, *_ in wires if col == "b"}
    for row in rows:
        a, y = hole("a", row)
        b, _ = hole("b", row)
        body += rect(5, y - 10, 164, 20, BLUE, "#6c8ebf", 3)
        body += text(162, y + 4, "XIAO " + NETS[row][0], 11, True, "end")
        body += line(169, y, a, y, COLORS[row], 3)
        body += line(b, y, 484, y, COLORS[row], 2)
        body += text(490, y + 4, right_names[row], 12, True)
    if include_amp:
        c, y = hole("c", 10)
        body += line(c, y, c, y - 17, COLORS[10], 2)
        body += line(c, y - 17, 484, y - 17, COLORS[10], 2)
        body += text(490, y - 13, "AMP GND (C10)", 11, True)
    body += text(340, 408, "So as pontas entram nos furos. Cruzamentos de fios nao sao emendas.", 12, anchor="middle")
    body += text(340, 430, "Todos os fios sao mantidos entre etapas. F-J e barramentos ficam vazios.", 11, anchor="middle")
    return svg(body)


def windows_diagram(kind):
    body = text(340, 26, "DESENHO EXPLICATIVO: NAO E CAPTURA DO SEU COMPUTADOR", 13, True, "middle")
    body += rect(25, 55, 630, 330, GRAY, "#666")
    body += rect(25, 55, 630, 40, BLUE, "#6c8ebf")
    if kind == "files":
        body += text(45, 80, "Explorador: C:\\robot", 15, True)
        for i, value in enumerate(["flash.ps1", "requirements-flash.txt", "guia-ilustrado-iniciantes.pdf",
                                   "firmware-built", "     robot.bin", "     manifest.json"]):
            body += text(65, 130 + i * 36, value, 15, i in [0, 3, 4])
        body += text(340, 418, "Se vir outra pasta dentro de C:\\robot, conferir onde ficou flash.ps1.", 12, anchor="middle")
    elif kind == "com":
        body += text(45, 80, "Gerenciador de Dispositivos: exemplo", 15, True)
        for i, value in enumerate(["Computador", "  > Portas (COM e LPT)", "       USB Serial ... (COM7)", "",
                                   "O numero real pode ser diferente.", "Anote a porta que aparece ao conectar a placa."]):
            body += text(65, 135 + i * 35, value, 15, i == 2)
        body += text(340, 418, "COM7 e exemplo. Nao copiar sem conferir a SUA porta.", 13, True, "middle")
    else:
        body += text(45, 80, "Sequencia de recuperacao BOOT", 15, True)
        for i, value in enumerate(["1. Retirar USB; servos e bateria desconectados.",
                                   "2. Segurar o botao BOOT da placa.",
                                   "3. Conectar USB de dados mantendo BOOT.",
                                   "4. Soltar BOOT e procurar a porta COM.",
                                   "5. Gravar. Depois, pressionar RESET se necessario."]):
            body += text(50, 140 + i * 43, value, 15)
        body += text(340, 418, "Identificar BOOT pelas inscricoes; nao pelo lado do desenho.", 12, anchor="middle")
    return svg(body)


PAGES = []


def add(title, body, image=None, checkpoint=""):
    PAGES.append((re.sub(r"^\d+\. ", "", title), body, image, checkpoint))


def compose():
    PAGES.clear()
    add("Antes de comecar: o que este guia prova",
        "Este e o manual visual da montagem ELETRICA INICIAL: protoboard, OLED, amplificador e falante. "
        "O firmware compilou; nao tenho as pecas em bancada e nao posso comprovar seu funcionamento fisico a distancia.\n\n"
        "Os desenhos sao originais, explicativos e nao fotografias das suas pecas. "
        "As coordenadas foram escolhidas para distribuir os sinais em uma protoboard comum A-J. "
        "Precisam coincidir com as letras/numeros e a continuidade da unidade real.\n\n"
        "A XIAO e os modulos ficarao FORA da protoboard, sobre suporte nao condutivo. "
        "So os fios entram nos furos indicados. Isso evita inventar a posicao de encaixe da placa ou esconder furos debaixo dela.\n\n"
        "Motores: apenas planejamento neste PDF, nao ligacao energizada. LiPo: desconectada em todas as etapas. "
        "O guia de execucao de 16 paginas registra a proposta tecnica anterior. "
        "Para a sequencia inicial de montagem e Windows, usar este manual atualizado.\n\n"
        "Se sua placa ou os nomes dos pinos diferirem, pare. Nao escolha um pino por parecer estar na posicao do desenho.",
        checkpoint="Pode seguir: leitura e preparacao sem energia. Nao pode: energizar pecas que nao foram conferidas.")
    add("Roteiro: uma etapa por vez",
        "COMO USAR: acompanhem a sequencia do PDF, sem saltar etapas. O indice lateral do leitor de PDF permite "
        "voltar a um assunto. As caixas CONFERENCIA dizem o que deve estar certo antes de avancar.\n\n"
        "ETAPA A - Sem energia: conhecer a protoboard, conferir conectores e preparar headers. "
        "Se faltam cabos ou uma solda segura, parar aqui. O ferro de solda pode causar queimaduras; "
        "nao e uma atividade para fazer sem supervisao e preparo.\n\n"
        "ETAPA B - Sem energia: montar OLED, depois audio, mantendo todos os fios anteriores. "
        "Comparar com as duas figuras de conjunto completo.\n\n"
        "ETAPA C - Computador Windows: extrair arquivos, preparar Python, descobrir a porta e gravar. "
        "Um comando por vez; nao copiar o 'PS C:\\robot>' de exemplos.\n\n"
        "ETAPA D - Energia USB: ler logs e conferir display/camera. "
        "So depois configurar rede e conta. Se surgir erro, registrar o primeiro e parar.\n\n"
        "ETAPA E - Motores: permanece bloqueada ate identificar fonte, conectores e servos reais. "
        "Nao usar a LiPo. Nao interpretar o diagrama de alimentacao como autorizacao de montagem.\n\n"
        "Nao estimamos tempo de montagem. Uma etapa pode terminar em 'falta uma peca' ou 'precisa de ajuda presencial'. "
        "Isso e um resultado correto, nao motivo para improvisar.",
        checkpoint="Os resultados esperados sao criterios a testar, nao resultados ja observados nas suas pecas.")
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
    add("Checklist de materiais antes da montagem",
        "NUCLEO: uma XIAO ESP32-S3 SENSE com expansao e antena; um OLED SH1106; "
        "um MAX98357; um falante 4 ohms/3 W; uma protoboard A-J com pelo menos 22 linhas.\n\n"
        "LIGACOES: 17 jumpers femea-macho para OLED e amplificador, mais dois fios adequados para o falante. "
        "O botao opcional usa mais tres ligacoes. Separe alguns jumpers macho-macho para testar continuidade.\n\n"
        "FERRAMENTAS: multimetro com continuidade; cabo USB-C de DADOS; computador Windows com internet; "
        "suporte nao condutivo; etiquetas; descascador de fio apropriado; pequena chave se houver bornes.\n\n"
        "SE FALTAM HEADERS: barras macho 2,54 mm compativeis, solda eletronica apropriada, "
        "ferro em suporte, ventilacao/extracao, protecao ocular e placa de treino. "
        "O kit de solda comprado nao garante que todos os consumiveis e cabos estejam presentes.\n\n"
        "Nao comprar a fonte dos motores como substituto de um item faltante no nucleo. "
        "A montagem de motores sera tratada separadamente.\n\n"
        "Marque na lista: tenho / falta / nao sei identificar. Se marcar 'nao sei', fotografe a peca desligada "
        "e resolva a identificacao antes de conectar.",
        checkpoint="Conte 17 cabos femea-macho e confira headers firmes; nao presumir que o pacote de jumpers os inclui.")
    add("Escolher o tipo certo de jumper",
        "O cabo deste desenho tem uma ponta femea e outra macho. "
        "A ponta femea recebe o pino metalico do header; a ponta macho entra no furo da protoboard.\n\n"
        "Pegar pelo conector plastico, nao puxar pelo fio. Encaixar sem forcar. "
        "Nao deixar parte metalica exposta encostar no pino vizinho.\n\n"
        "Se o modulo nao tiver header macho ja soldado, obter a conexao correta antes. "
        "Nao prender um fio solto dentro de um furo metalizado da placa.",
        "jumper-connectors", "Identifique as duas pontas antes de usar o primeiro cabo.")
    add("Headers: pronto ou ainda sem solda?",
        "Olhe os contatos com boa luz, sem USB nem bateria. Um pino firme deve atravessar seu furo e ter "
        "uma junta de solda ligando o metal do pino ao pad (ilha metalica em volta do furo). "
        "Header e a barra de pinos. Se ha somente furos dourados, falta header.\n\n"
        "1. Se os headers ja vieram soldados: verificar pinos retos e nenhuma ponte para o vizinho. "
        "Nao refazer uma solda boa so porque o desenho tem outra aparencia.\n"
        "2. Se faltam headers: decidir entre ajuda presencial para preparar as pecas ou aprender primeiro na placa de treino.\n\n"
        "Na XIAO base ha duas fileiras de sete contatos laterais. O OLED do anuncio tem quatro contatos. "
        "No AITRIP, a quantidade e o lado de insercao precisam ser conferidos na unidade.\n\n"
        "Antes de soldar, verificar o lado de insercao SEM ENERGIA: depois de montado deve ser possivel "
        "encaixar o jumper sem bloquear USB, expansao ou componentes. O corte abaixo e generico, "
        "nao define qual lado soldar em cada placa.",
        "header-readiness", "Nao soldar com USB, bateria ou expansoes sensiveis ligadas; nao escolher o lado por este desenho.")
    add("Solda: primeiro treinar, depois preparar",
        "O adulto deve preparar bancada resistente ao calor, suporte do ferro, ventilacao e protecao ocular. "
        "Nao comer na bancada. Lavar as maos ao terminar. Manter a bateria longe da area quente.\n\n"
        "Use uma placa de treino separada e header de sobra; nao comece pela XIAO. "
        "Usar solda para eletronica, nao fluxo acido de encanamento. "
        "Seguir temperatura e preparo indicados para o ferro e a liga utilizados; nao adivinhar uma temperatura universal.\n\n"
        "1. Prender a placa de treino e o header para que nao se movam.\n"
        "2. Limpar/estanhar a ponta conforme o manual do ferro.\n"
        "3. Encostar a ponta no pino E no pad. Alimentar pouca solda na junta aquecida.\n"
        "4. Retirar o fio de solda, depois o ferro. Deixar esfriar sem mover.\n"
        "5. Inspecionar: junta molha pino e pad, sem bola solta ou ponte para outro pino.\n\n"
        "Se nao fluir, houver plastico deformado ou precisar insistir aquecendo, parar e pedir ajuda. "
        "Nao cortar pinos de header que ainda serao usados pelos jumpers. "
        "Brilho sozinho nao comprova qualidade; algumas ligas ficam foscas.",
        "solder-practice", "So passar as pecas do robo a solda apos pratica satisfatoria e orientacao do lado correto.")
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
    add("Reconhecer o OLED comprado",
        "A tela e a regiao escura; os quatro contatos levam alimentacao e dados. "
        "Na imagem do anuncio fornecida, a ordem e GND, VCC, SCL, SDA. "
        "O desenho abaixo reproduz essa identificacao, nao uma foto da unidade que chegou.\n\n"
        "1. Encontrar e ler as quatro inscricoes na placa real, com boa iluminacao.\n"
        "2. Etiquetar GND, VCC, SCL e SDA nas pontas dos quatro cabos.\n"
        "3. Se a ordem ou as letras forem diferentes, nao espelhar mentalmente nem usar a ordem por memoria. "
        "Confirmar os nomes antes de continuar.\n\n"
        "VCC e o nome da entrada do display; neste projeto ela vai a 3V3. "
        "SCL leva clock e SDA leva dados. Nao e necessario decorar esses termos: "
        "seguir a ligacao nome a nome.",
        "identify-oled", "Nao usar display de seis/sete contatos SPI como substituto deste OLED I2C de quatro contatos.")
    add("Reconhecer o amplificador comprado",
        "O MAX98357 e a placa que recebe dados digitais da XIAO e alimenta o falante. "
        "Localize VIN, GND, BCLK, LRC/LRCK e DIN. Ha tambem duas saidas para o falante.\n\n"
        "O AITRIP nao tem necessariamente os pinos na ordem de fotos Adafruit. "
        "Este desenho e um mapa de NOMES e FUNCOES; nao e o desenho fisico da sua unidade.\n\n"
        "1. Ler frente e verso do modulo sem energia.\n"
        "2. Fazer etiquetas nos cinco cabos correspondentes.\n"
        "3. Localizar SPK+ e SPK- sem confundi-los com VIN/GND.\n\n"
        "Se houver SD, SD_MODE ou GAIN: nao conectar por adivinhacao. "
        "Uma unidade sem polarizacao apropriada pode ficar muda; isso exige esquema/documentacao do fornecedor.\n\n"
        "Se nao for possivel identificar essas inscricoes, essa e uma parada obrigatoria. "
        "Nenhum desenho generico resolve com seguranca uma pinagem desconhecida.",
        "identify-amplifier", "Encontrou todos os nomes? Pode montar. Nao encontrou? Falta identificar a unidade real.")
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
        if name == "oled-scl":
            add("Comparar: OLED com os oito fios",
                "Nao tirar os fios de uma etapa anterior. Ao terminar o OLED existem oito jumpers: "
                "quatro saindo da XIAO e quatro saindo do display.\n\n"
                "No desenho completo: cada linha une um pino da XIAO a um pino do OLED. "
                "Nao ha conexao entre linhas diferentes. Fios que passam por cima de outros furos nao entram neles.\n\n"
                "Confira A10/B10, A11/B11, A12/B12 e A13/B13. "
                "A imagem mostra ligacoes eletricas, nao as posicoes fisicas dos modulos. "
                "Use a pagina de pinagem da XIAO e as letras do OLED para achar as pontas reais.\n\n"
                "Ainda nao conectar USB: falta integrar audio e revisar o nucleo.",
                "complete-oled", "Oito jumpers no total; nenhuma ligacao do display vai para 5V.")
    add("10. Ligar um unico alto-falante",
        "O falante NAO usa as linhas GND, 3V3 ou 5V da protoboard. "
        "Ele recebe dois fios diretamente das saidas do amplificador.\n\n"
        "1. Preparar dois fios flexiveis para eletronica. Desencapar apenas o necessario para a conexao, "
        "com descascador adequado, sem cortar os filamentos. Nao usar chama nem morder a isolacao.\n"
        "2. Se o falante vier com abas sem fios: soldar um fio por aba, somente apos a pratica de solda. "
        "Nao encostar o ferro no cone ou na isolacao. Se nao souber prender e soldar essas abas, obter ajuda presencial.\n"
        "3. Ligar um terminal do falante a SPK+ do MAX98357; o outro terminal a SPK-. "
        "Se o falante tiver + marcado, usar esse terminal em SPK+.\n"
        "4. Se houver borne de parafuso no modulo: prender apenas o trecho desencapado, "
        "sem filamentos para fora. Puxar suavemente para conferir. Se houver apenas furos, "
        "identificar a conexao/solda apropriada; fio solto encostado nao serve.\n\n"
        "Nao unir os dois terminais, nao ligar SPK- ao GND e nao colocar dois falantes em paralelo. "
        "Se as inscricoes da sua unidade forem outras, confirmar antes de conectar.",
        "speaker-output", "So um falante. Nenhum fio do falante vai ao GND.")
    add("Conjunto completo: todos os 17 jumpers",
        "Agora ha oito cabos da XIAO para a protoboard e nove dos modulos para ela: total 17. "
        "O falante usa dois fios adicionais diretos, mostrados na pagina propria.\n\n"
        "GND e compartilhado em tres furos diferentes: A10 XIAO; B10 OLED; C10 amplificador. "
        "Nao colocar dois conectores no mesmo furo.\n\n"
        "F-J fica vazio. Linhas 14 e 19 ficam vazias. "
        "A20/A21/A22 ainda nao recebem fios nesta montagem inicial.\n\n"
        "A linha preta de AMP GND usa C10. Os outros destinos usam B na mesma linha do pino da XIAO. "
        "Cruzamentos de linhas no desenho nao sao emendas.",
        "complete-core", "Comparar ponta por ponta, nao apenas se o conjunto tem 'cores parecidas'.")
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
    add("Windows 1: baixar e extrair o pacote",
        "1. No navegador, abrir a release " + VERSION + ":\n"
        "https://github.com/ricmmartins/family-ai-robot/releases\n"
        "2. Na lista Assets dessa release, baixar robo-de-mesa-completo.zip. "
        "NAO escolher 'Source code (zip)': ele nao inclui o binario robot.bin.\n"
        "3. No Explorador de Arquivos, ir a Downloads. Clicar com botao direito no ZIP e usar "
        "'Extrair Tudo' / 'Extract All'. Nao executar arquivos dentro da janela do ZIP.\n"
        "4. Escolher uma pasta nova, curta e permitida, por exemplo C:\\robot. "
        "Se ela ja tiver arquivos, escolher outra pasta vazia e adaptar todos os comandos do guia.\n\n"
        "Ao terminar, flash.ps1 e a pasta firmware-built devem estar diretamente na pasta de trabalho. "
        "Dentro de firmware-built devem existir robot.bin e manifest.json.\n\n"
        "Se so existir outra subpasta, abrir essa subpasta: esse e o caminho a usar no PowerShell. "
        "Nao misturar arquivos de releases diferentes.",
        "windows-files", "Conferir os arquivos pelo nome. Nao precisa instalar ESP-IDF para gravar este binario.")
    add("Windows 2: abrir PowerShell e Python",
        "Este roteiro usa Windows com permissao para instalar aplicativos. Em computador escolar/gerenciado, "
        "pedir autorizacao; nao contornar bloqueios.\n\n"
        "1. Instalar o Python install manager pelo site oficial ou Microsoft Store, conforme as instrucoes:\n"
        "https://docs.python.org/3/using/windows.html\n"
        "2. Fechar terminais antigos. Abrir Iniciar, digitar PowerShell e abrir uma janela comum, "
        "sem 'Executar como administrador'.\n\n"
        "3. Digitar cada comando abaixo e pressionar Enter. Esperar o comando acabar e aparecer de novo "
        "a linha iniciada por PS. Nao digitar o PS: ele e o prompt, nao parte do comando.\n\n"
        "CMD: pymanager install 3.12\n"
        "CMD: py -V:3.12 --version\n\n"
        "Resultado esperado do segundo comando: Python 3.12.x, com x variavel. "
        "Isso instala/seleciona uma versao compativel sem remover outros Pythons do computador.\n\n"
        "Se pymanager nao for reconhecido, confirmar que instalou o install manager, nao apenas um "
        "Python antigo; reabrir o terminal e consultar a secao Troubleshooting da documentacao oficial. "
        "Se py nao localizar 3.12, nao trocar de versao por tentativa: resolver a instalacao primeiro.",
        checkpoint="Antes de continuar, py -V:3.12 --version deve funcionar. Nenhuma placa precisa estar conectada.")
    add("Windows 3: preparar as ferramentas",
        "Manter a janela PowerShell aberta. Digitar uma linha por vez. "
        "Se usou outra pasta, substituir C:\\robot pelo caminho real entre aspas.\n\n"
        "CMD: Set-Location 'C:\\robot'\n"
        "CMD: Test-Path .\\flash.ps1\n"
        "CMD: Test-Path .\\firmware-built\\robot.bin\n\n"
        "Os dois Test-Path devem responder True. False significa pasta/pacote errado, nao defeito da placa.\n\n"
        "CMD: py -V:3.12 -m venv .venv\n"
        "CMD: .\\.venv\\Scripts\\python.exe -m pip install -r requirements-flash.txt\n"
        "CMD: .\\.venv\\Scripts\\python.exe -m esptool version\n\n"
        "O ultimo comando deve informar esptool 5.6.0. A pasta .venv guarda as ferramentas somente aqui. "
        "Nao e preciso ativar ambiente virtual, alterar PATH ou mudar a politica global de scripts.\n\n"
        "Se qualquer linha falhar: parar nessa linha. Guardar o texto do erro. "
        "Nao copiar uma sequencia inteira presumindo que os passos anteriores deram certo.\n\n"
        "Erro de rede ao instalar: conferir internet/proxy autorizado. Falta de python.exe dentro de .venv "
        "indica que a criacao do ambiente nao terminou.",
        checkpoint="True, True e esptool 5.6.0. Instalar a ferramenta ainda nao testa a placa.")
    add("Windows 4: descobrir a porta COM",
        "Primeiro concluir a revisao eletrica; fonte dos servos e LiPo continuam desconectadas.\n\n"
        "1. Com USB retirado, clicar com botao direito em Iniciar e abrir Gerenciador de Dispositivos "
        "/ Device Manager. Observar Portas / Ports (COM & LPT), se existir.\n"
        "2. Conectar a XIAO com cabo USB de DADOS. Observar a porta que apareceu. "
        "Ela pode ter outro nome e numero, nao necessariamente COM7.\n"
        "3. Retirar USB e verificar se essa porta desaparece. Reconectar e confirmar novamente.\n\n"
        "Anotar: MINHA PORTA = COM____. Usar esse valor no lugar de COM7 nas proximas paginas.\n\n"
        "Se nada aparecer: testar cabo de dados conhecido e outra porta USB. "
        "Se persistir, usar BOOT como na pagina seguinte. "
        "Nao baixar drivers de sites aleatorios nem selecionar outra porta que ja existia.",
        "windows-com", "COM7 no desenho e EXEMPLO. Se nao identificar a sua porta, nao tentar gravar.")
    add("Windows 5: BOOT e gravacao",
        "Se a porta normal ja estiver identificada, tentar o comando de gravacao abaixo. "
        "Se a conexao falhar, entrar em BOOT conforme o desenho e identificar a porta novamente: "
        "ela pode mudar no modo de gravacao.\n\n"
        "Trocar COM7 pela porta real. Fechar monitores seriais antes de gravar.\n"
        "CMD: powershell -ExecutionPolicy Bypass -File .\\flash.ps1 -Port COM7\n\n"
        "Isso aplica a politica somente ao processo do script, nao permanentemente ao computador. "
        "Nao usar para contornar politicas de um equipamento gerenciado.\n\n"
        "O script verifica identidade e SHA256, depois grava a imagem completa em 0x0. "
        "Nao retirar USB durante a transferencia. Ao terminar deve aparecer "
        "'Flash transfer complete'. Se falhar: nao declarar gravado; resolver o erro.\n\n"
        "BOOT e o botao para modo de download e conversa. RESET reinicia a placa. "
        "Identificar pelas inscricoes/documentacao da unidade, nao pelo lado do desenho.",
        "windows-boot", "Mensagem final confirma transferencia, nao audio, camera, alimentacao ou ativacao na nuvem.")
    add("13. Primeiro teste energizado",
        "Este teste exige nova XIAO Sense com expansao corretamente encaixada e a montagem eletrica "
        "ja conferida. Se isso ainda nao foi possivel, PARE ANTES DO USB.\n\n"
        "1. Manter fonte dos motores e LiPo desconectadas.\n"
        "2. Usar cabo USB de dados e fonte/porta adequada. Comecar com audio baixo; "
        "uma porta USB fraca pode nao sustentar os picos do conjunto.\n"
        "3. Abrir o log no PowerShell e pressionar RESET:\n\n"
        "CMD: .\\.venv\\Scripts\\python.exe -m serial.tools.miniterm `\n"
        "CMD:   --rts 0 --dtr 0 COM7 115200\n\n"
        "Usar a porta real. O acento grave ` ao fim da primeira linha continua o comando na segunda.\n\n"
        "4. Procurar 'SH1106 initialized' e 'Camera ready'. "
        "O display deve mostrar interface sem deslocamento ou corte. Fechar monitor com Ctrl+].\n\n"
        "Se houver calor anormal, cheiro, fumaca, erro fatal ou reinicializacoes: desconectar USB. "
        "Nao mexer em fios com energia nem insistir ligando repetidamente.\n\n"
        "Nao ligar so o OLED e interpretar falha da camera como defeito do display. "
        "O firmware atual exige a expansao da camera e verifica seu sensor na inicializacao.\n\n"
        "Falta de audio deve ser investigada pelos pinos e pela documentacao do modulo AITRIP. "
        "Nao improvisar pontes SD/GAIN.",
        checkpoint="Avancar so com display legivel, camera inicializada e sem resets/aquecimento anormal.")
    add("Nuvem 1: tela de entrada real",
        "Pagina publica conferida em 28/10/2026, sem entrar em nenhuma conta. "
        "O recorte nesta pagina mostra a entrada da Console, nao a tela de pareamento do robo.\n\n"
        "1. Abrir https://xiaozhi.me/ e clicar Console.\n"
        "2. O site direciona para login. Na tela observada ha SMS Code, Username & Password "
        "e Sign in with Google. Escolher um metodo permitido para sua conta; ler termos/privacidade antes de aceitar.\n\n"
        "Nao escolher +86 por copia do exemplo. Nao compartilhar telefone, senha, SMS, token ou codigo de dispositivo. "
        "Nenhuma conta foi criada ou autorizada por nos para produzir este manual.\n\n"
        "Ainda NAO foi inspecionada a area autenticada; os nomes dos menus de pareamento e "
        "configuracao posteriores nao foram confirmados. Se a interface nao orientar a vinculacao, "
        "parar e consultar ajuda do servico; nao instalar firmware de outra placa.",
        "xiaozhi-login-20261028.png", "Captura real de entrada anonima; ativacao do nosso dispositivo continua nao comprovada.")
    add("14. Wi-Fi, voz e foto: testes separados",
        "Usar primeiro a rede domestica 2,4 GHz autorizada. "
        "Seguir o nome da rede e portal mostrados no OLED/log; nao assumir um IP fixo.\n\n"
        "No primeiro provisionamento, usar as instrucoes mostradas no OLED/log para cadastrar Wi-Fi. "
        "No portal autenticado, vincular o dispositivo conforme o fluxo do servico, caso seja oferecido para esta placa. "
        "Nao ha aqui nomes de botoes autenticados confirmados. Se nao houver fluxo compativel, parar nesta etapa.\n\n"
        "Configurar idioma da IA e voz para ingles quando essas opcoes estiverem disponiveis. "
        "A interface inglesa do firmware NAO configura a voz da nuvem. Clique curto no BOOT alterna a conversa conforme o estado; "
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
    add("Se nao funcionar: diagnostico em ordem",
        "CALOR, CHEIRO OU FUMACA: retirar USB imediatamente, sem tocar partes quentes. "
        "Nao insistir, recolocar fios ou energizar para 'ver se passou'.\n\n"
        "SEM PORTA COM: confirmar cabo de dados e porta USB; tentar BOOT; identificar novamente a porta. "
        "Porta ocupada: fechar monitor serial e outros aplicativos que a usam.\n\n"
        "ERRO DE HASH/IDENTIDADE: nao ignorar a verificacao. Baixar novamente o ZIP correto da mesma release. "
        "Falta robot.bin: provavelmente baixou Source code, nao o pacote dos Assets.\n\n"
        "SEM DISPLAY: desligar USB; conferir VCC->3V3, GND, SDA->D0 e SCL->D1. "
        "Pinos D4/D5 de tutoriais I2C genericos NAO sao estes pinos. "
        "Nao tentar 5V para corrigir tela apagada.\n\n"
        "CAMERA FAIL: confirmar placa Sense e expansao instalada conforme manual Seeed. "
        "Identificar sensor real antes de mexer em cabo flat; nao desmontar com energia.\n\n"
        "OUVE MAS NAO FALA: revisar VIN/GND, D6/BCLK, D4/LRC, D8/DIN e falante SPK+/SPK-. "
        "Conferir documentacao AITRIP para SD/GAIN. Nao aterrar uma saida do falante.\n\n"
        "FALA MAS NAO ENXERGA: verificar log e configuracao de visao no backend. "
        "Isso nao comprova defeito de fio da camera.\n\n"
        "RESETS AO FALAR: parar e investigar alimentacao/cabos; nao conectar motores para experimentar.",
        checkpoint="Registrar primeiro erro e etapa. Nao trocar varios fios de uma vez; sempre desligar antes de mexer.")
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
    add("Corpo fixo e cabeca movel",
        "O desenho mostra somente uma proposta de distribuicao das pecas, nao um molde para cortar nem "
        "o encaixe exato do pan-tilt recebido.\n\n"
        "Fixar placas em suporte nao condutivo; proteger a parte inferior e aliviar a tracao dos cabos na base. "
        "Nao deixar pinos expostos encostarem em metal. Manter lente, microfone e antena desobstruidos.\n\n"
        "Reservar folga nos quatro fios do OLED. Fios nao podem esticar, prender no eixo ou servir de sustentacao. "
        "Nao fazer teste de movimento antes de revisar fonte/servos e centralizar sem carga.\n\n"
        "Para a primeira prova de voz/visao, deixar todas as pecas fixas e os motores desconectados. "
        "Nao e preciso montar a cabeca para testar esse nucleo.",
        "fixed-and-moving", "Camera continua fixa. Movimento do OLED nao aponta a camera para outra direcao.")
    add("Ficha de ensaio: preencher, nao presumir",
        "DATA: ____________   Placa/camera identificadas: ___________________\n\n"
        "Marcar cada item como NAO FEITO, PASSOU ou FALHOU; anotar evidencia e erro.\n\n"
        "Protoboard vazia: continuidade igual ao mapa: _______________________\n"
        "Headers e 17 cabos revisados sem energia: __________________________\n"
        "Firmware: transferencia terminou sem erro: _________________________\n"
        "OLED: texto legivel, sem corte/deslocamento: ________________________\n"
        "Camera: log Camera ready e sem erro fatal: _________________________\n"
        "Conta: dispositivo vinculado na nuvem: _____________________________\n"
        "Microfone + voz: dez conversas curtas sem reset: ____________________\n"
        "Foto: envio realizado; descricao compativel com objeto: ______________\n"
        "Alimentacao: sem resets, cheiro ou calor anormal: ___________________\n"
        "Motores: NAO ENSAIADOS enquanto a etapa estiver bloqueada.\n\n"
        "Se precisar de revisao: foto geral de cima e fotos de frente/verso dos modulos, tudo desligado; "
        "nomes dos pinos legiveis; primeiro erro do log, sem credenciais. "
        "Nao incluir rostos, documentos pessoais ou recibos.\n\n"
        "Esta ficha separa o que foi observado do que ainda e uma proposta. "
        "Nem passar todos os itens substitui ensaios de corrente/temperatura ou aprova uso escolar.",
        checkpoint="Nao preencher PASSOU por ter lido o guia. Precisa ter observado o resultado na montagem.")
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
        "Pratica e preparo de solda:\n"
        "https://learn.adafruit.com/adafruit-guide-excellent-soldering/preparation\n"
        "https://learn.adafruit.com/adafruit-guide-excellent-soldering/making-a-good-solder-joint\n\n"
        "Instalacao Python no Windows:\n"
        "https://docs.python.org/3/using/windows.html\n\n"
        "Software e codigo exato dos pinos do projeto:\n"
        "https://github.com/ricmmartins/family-ai-robot\n\n"
        "Base de software:\n"
        "https://github.com/78/xiaozhi-esp32\n\n"
        "Comprovado: compilacao/link do firmware publicado. "
        "Nao comprovado: montagem, funcionamento nas suas pecas, ativacao em nuvem e uso escolar.")


def wrap(value, width, size):
    result = []
    for paragraph in value.splitlines():
        if paragraph.startswith("CMD: "):
            result.append(paragraph)
            continue
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


def write_online_manual():
    lines = ["# Manual ilustrado para iniciantes", "",
             f"**[{VERSION}: abrir o PDF de {len(PAGES)} paginas](../guia-ilustrado-iniciantes.pdf)**. "
             "Este manual e gerado da mesma fonte do PDF, com a mesma sequencia e conferencias.", "",
             "**Hardware e ativacao ainda nao testados.** Sao diagramas propostos, "
             "nao fotos da montagem real. Motores e LiPo nao estao liberados para montagem energizada.", ""]
    for index, (title, body, image, checkpoint) in enumerate(PAGES, 1):
        lines += [f"## {index}. {title}", ""]
        if image:
            path = image if image.endswith(".png") else f"{image}.svg"
            lines += [f"![{title}](images/{path})", ""]
        in_code = False
        for paragraph in body.splitlines():
            command = paragraph.startswith("CMD: ")
            if command and not in_code:
                lines += ["", "```powershell"]
            elif in_code and not command:
                lines += ["```", ""]
            lines.append(paragraph[5:] if command else paragraph)
            in_code = command
        if in_code:
            lines += ["```"]
        if checkpoint:
            lines += ["", "**Conferencia:** " + checkpoint]
        lines += [""]
    (ROOT / "docs" / "manual-ilustrado.md").write_text("\n".join(lines), encoding="utf-8")


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
        "header-readiness": headers_diagram(),
        "solder-practice": solder_diagram(),
        "identify-oled": module_diagram("OLED"),
        "identify-amplifier": module_diagram("MAX98357"),
        "complete-oled": cumulative_diagram(False),
        "complete-core": cumulative_diagram(True),
        "windows-files": windows_diagram("files"),
        "windows-com": windows_diagram("com"),
        "windows-boot": windows_diagram("boot"),
        "fixed-and-moving": mechanics_diagram(),
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
            path = ASSETS / (image if image.endswith(".png") else f"{image}.svg")
            with fitz.open(path) as vector:
                with fitz.open("pdf", vector.convert_to_pdf()) as rendered:
                    clip = None
                    if path.suffix == ".png":
                        bounds = rendered[0].rect
                        clip = fitz.Rect(bounds.width * .272, bounds.height * .05,
                                         bounds.width * .73, bounds.height * .71)
                    page.show_pdf_page(fitz.Rect(35, 60, 560, 400), rendered, 0, clip=clip)
            y = 414
        lines = wrap(body, 507, 10.5)
        for value in lines:
            if y > 743:
                raise ValueError(f"Page body overflow: {index + 1}, {title}")
            if value.startswith("CMD: "):
                command = value[5:]
                if fitz.get_text_length(command, fontsize=9, fontname="cour") > 507:
                    raise ValueError(f"Command overflow: {command}")
                page.draw_rect(fitz.Rect(40, y - 10, 555, y + 4), fill=(.94, .96, .98), color=None)
                page.insert_text((44, y), command, fontsize=9, fontname="cour")
            else:
                page.insert_text((44, y), value, fontsize=10.5)
            y += 14
        for url in set(re.findall(r"https?://[^\s]+", body)):
            for bounds in page.search_for(url):
                page.insert_link({"kind": fitz.LINK_URI, "from": bounds, "uri": url})
        if checkpoint:
            bounds = fitz.Rect(36, 758, 559, 801)
            page.draw_rect(bounds, fill=(1, 0.95, 0.80), color=(0.84, 0.72, 0.34))
            fit = page.insert_textbox(bounds + (8, 6, -8, -4), "CONFERENCIA: " + checkpoint, fontsize=9.5)
            if fit < 0:
                raise ValueError(f"Checkpoint overflow: {title}")
        page.insert_text((42, 824), f"FAMILY AI ROBOT | {VERSION} | 28/10/2026 | Hardware ainda nao testado", fontsize=8)
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
        for index, (_, _, image, _) in enumerate(PAGES):
            if image in {"complete-core", "complete-oled", "solder-practice", "header-readiness",
                         "identify-amplifier", "identify-oled", "windows-com",
                         "xiaozhi-login-20261028.png", "separate-power", "fixed-and-moving"}:
                check[index].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(ASSETS / f"preview-{index + 1}.png")
    write_online_manual()
    print(f"{OUTPUT}: {len(PAGES)} pages, {len(drawings)} SVG illustrations; layout checks passed")


if __name__ == "__main__":
    generate()
