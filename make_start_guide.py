from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parent
PAGES = [
    ("Comecem por aqui", """ROBÔ DE MESA COM IA | ETAPA QUE JÁ PODEM ADIANTAR
Projeto em família | 24 de outubro de 2026

Este PDF é independente da compilação do firmware. Ele permite preparar as peças, a bancada, a base e as ligações SEM ENERGIA. Não é uma autorização para ligar o conjunto nem uma declaração de que o firmware foi aprovado.

A REGRA DESTA ETAPA
USB desconectado. LiPo desconectada. Fonte dos motores desconectada.
Nenhuma exceção durante a montagem ou a solda.

RESULTADO ESPERADO AO TERMINAR
[ ] Peças identificadas e organizadas.
[ ] Placa, display e amplificador posicionados sem curtos mecânicos.
[ ] Ligações de display e áudio preparadas e conferidas, ainda desligadas.
[ ] Base planejada com acesso aos controles e folga para os cabos.
[ ] Fotos e lista de pendências prontas para a próxima etapa.

O QUE DEIXAR PARA DEPOIS
Não gravar binário de outra placa. Não ligar motores. Não carregar nem adaptar a LiPo. Não testar o conjunto completo energizado. Não instalar a cabeça com carga ou ajustar os braços dos servos antes de centralização e teste local aprovados.

O QUE ESTÁ DEFINIDO PARA ESTE PROJETO
XIAO ESP32-S3 Sense; OLED JAMHER SH1106; áudio com MAX98357 e um falante de 4 ohms; dois servos do conjunto Adafruit 1967. O robô usará inglês e IA na nuvem por Wi-Fi.

A primeira versão planejada usa alimentação USB para placa/áudio e fonte separada para os motores. Não precisa de computador durante o uso, mas não funciona pela LiPo comprada nesta etapa.

COMO TRABALHAR EM DUPLA
Uma pessoa faz cada ligação e a outra lê a tabela e confere. Alternar as funções ajuda as duas a entenderem o circuito. Ricardo supervisiona solda e uso de ferramentas.

Se a inscrição de qualquer pino não combinar com a tabela, parar nessa peça. Não adivinhar a função pelo lado da placa, pela cor do fio ou pela foto de um módulo parecido."""),
    ("1. Organizar e identificar", """PREPARAR A BANCADA
[ ] Mesa seca, iluminada e sem peças metálicas soltas.
[ ] Ferro de solda em suporte próprio e superfície resistente ao calor.
[ ] Proteção ocular e ventilação adequada para solda.
[ ] Todas as fontes desconectadas; bateria afastada da área de solda.

SEPARAR AS PEÇAS
[ ] XIAO ESP32-S3 Sense e expansão de câmera/microfone.
[ ] OLED JAMHER 1,3 pol., 128x64, SH1106 segundo o anúncio enviado.
[ ] Um MAX98357 do pacote AITRIP.
[ ] Um falante Gikfun 4 ohms / 3 W. Guardar o segundo.
[ ] Pan-tilt Adafruit 1967 com os dois servos.
[ ] Headers, protoboard e jumpers.
[ ] Capacitor de 470 uF / 25 V, reservado para a futura etapa dos motores.
[ ] LiPo EEMB: guardar com o conector intacto, protegida contra curto.

FOTOGRAFAR ANTES DE MONTAR
Fotos nítidas da frente e verso da XIAO, OLED e MAX98357. Registrar também a etiqueta dos servos e os conectores da câmera. Não precisam enviar número de pedido, endereço ou outros dados pessoais.

CONFERIR INSCRIÇÕES NAS PEÇAS REAIS
Na XIAO: localizar D0, D1, D3, D4, D5, D6, D7, D8, 3V3, 5V e GND. Usar os nomes impressos e a pinagem oficial, não uma contagem visual de pinos.
No OLED: localizar GND, VCC, SCL e SDA. A foto do anúncio mostra essa ordem, mas a inscrição da unidade real é a referência final.
No amplificador: localizar VIN, GND, BCLK, LRC/LRCK, DIN e os dois terminais de saída do falante.

HEADERS E PROTOBOARD
Se os headers já estão soldados, inspecionar se estão retos e sem pontes de solda. Se faltam headers e vocês não têm experiência, fazer primeiro uma prática em material de treino ou pedir ajuda presencial. Não usar a XIAO como primeira tentativa de solda.
Não aquecer bateria, lente, cabo flexível ou microfone. Não soldar sobre uma montagem energizada.

Medir o encaixe na protoboard antes de apertar: fileiras opostas da placa não podem cair na mesma ligação elétrica. Evitar forçar a expansão Sense ou dobrar o cabo da câmera. Se houver dúvida no encaixe, deixar a peça fora e avançar só no planejamento."""),
    ("2. Preparar display e áudio", """TODAS AS LIGAÇÕES DESTA PÁGINA SÃO COM TUDO DESLIGADO
Fixar os módulos para que suas partes metálicas não encostem entre si. Usar fios curtos e etiquetas. Não confiar somente nas cores.

OLED SH1106 -> XIAO
GND -> GND
VCC -> 3V3
SCL -> D1 / GPIO2
SDA -> D0 / GPIO1

[ ] Conferir cada uma das quatro ligações na inscrição real.
[ ] VCC do OLED está em 3V3, não em 5V.
[ ] SDA e SCL não estão trocados.
[ ] Nenhum pino ou fio desencapado encosta no vizinho.

MAX98357 -> XIAO
VIN -> 5V
GND -> GND
BCLK -> D6 / GPIO43
LRC ou LRCK -> D4 / GPIO5
DIN -> D8 / GPIO7

FALANTE -> MAX98357
Um terminal do falante -> SPK+.
Outro terminal do mesmo falante -> SPK-.
Nenhum terminal do falante vai ao GND. Não conectar dois falantes em paralelo.
Se o módulo usar outra identificação para suas saídas, conferir a documentação da unidade antes de conectar. Não confundir saída do falante com pino de alimentação.

[ ] Usar somente um falante.
[ ] Manter SD/GAIN na configuração de fábrica; não improvisar pontes.
[ ] O terminal 5V da XIAO não recebe fonte externa nesta etapa.
[ ] USB continua fora da placa.

IMPORTANTE SOBRE A ALIMENTAÇÃO FUTURA
O 5V da XIAO usado no amplificador dependerá da alimentação USB. Não presumir que esse pino fornecerá 5V quando a placa estiver alimentada apenas pela LiPo.

CÂMERA E MICROFONE
São os componentes da expansão Sense, não módulos a ligar pelos jumpers desta tabela. Não conectar fios aos seus pinos internos.
Não inserir microSD neste projeto. Não alterar o cabo flexível nem seu conector sem seguir as instruções oficiais da Seeed para a revisão recebida."""),
    ("3. Preparar a base e os controles", """MONTAGEM MECÂNICA SEM ALIMENTAÇÃO
[ ] Escolher uma base rígida, estável e não condutiva.
[ ] Posicionar XIAO/câmera, amplificador e falante na parte fixa.
[ ] Deixar lente, microfone e antena desobstruídos.
[ ] Deixar acesso ao USB, BOOT e aos conectores.
[ ] Separar fisicamente o falante do microfone.
[ ] Não apoiar placas nuas sobre metal ou cabeças de parafuso.

O QUE FAZER AGORA COM O PAN-TILT
Conferir peças e fixadores. Planejar onde a base do conjunto será presa e medir o espaço para os cabos. Não forçar os eixos manualmente, não reposicionar braços com energia e não colar o OLED na cabeça ainda.
O ajuste de centro e a montagem da carga ficam para depois do teste dos servos sem carga. O código proposto usa limites conservadores, mas isso não prova que a posição mecânica inicial esteja correta.

QUAL PARTE VAI SE MOVER
A primeira montagem prevê somente o OLED na cabeça móvel. XIAO e câmera ficam no corpo fixo. Portanto, virar a cabeça não mudará a direção da câmera nessa versão.
Preparar uma folga nos quatro fios do OLED, longe das articulações. A fixação final será feita depois dos testes.

BOTÃO ADICIONAL, SE VOCÊS JÁ TIVEREM
É um botão momentâneo normalmente aberto. A ligação prevista é um contato em D7 / GPIO44 e outro em GND.
Botões de quatro pernas costumam ter pares já ligados internamente. Confirmar os pares com multímetro antes de montar; não escolher pernas pela aparência.
Se ainda não houver o botão, apenas reservar o espaço. O BOOT da XIAO não substitui o botão físico de habilitação dos motores.

RESERVAR ESTES SINAIS, SEM CONECTAR OS SERVOS AGORA
PAN: D3 / GPIO4.
TILT: D5 / GPIO6.
Não usar GPIO3 para o tilt.

O QUE NÃO IMPROVISAR
Não alimentar os servos pelo 3V3 da XIAO, por GPIO ou pelos fios de sinal. Não unir os positivos de duas fontes.
A etapa dos motores exigirá fonte e distribuição adequadas, corte físico de energia e terra comum, conforme o guia completo. O capacitor de 470 uF não substitui uma fonte adequada.
Não ligar o capacitor nem a LiPo para 'ver se resolve'. Guardar ambos separados nesta etapa."""),
    ("4. Conferência e ponto de parada", """CONFERIR SEM ENERGIA
[ ] Bateria, USB e fonte dos motores continuam desconectados.
[ ] Ler cada linha da tabela enquanto a outra pessoa segue o fio.
[ ] Conferir 3V3, 5V e GND pela inscrição na XIAO.
[ ] Procurar pontes de solda, fios soltos e filamentos entre terminais.
[ ] Confirmar que as trilhas da protoboard não unem sinais diferentes.
[ ] Fotografar a montagem de cima e de lado com os rótulos legíveis.

MULTÍMETRO, SE VOCÊS SOUBEREM USAR
Em continuidade, trabalhar apenas sem energia. Começar numa protoboard vazia: descobrir quais furos são interligados e se os barramentos de alimentação são interrompidos no meio.
Usar continuidade para seguir um fio ou verificar os contatos do botão. Não usar a escala de corrente entre alimentação e GND.
Um apito em um circuito com componentes não é diagnóstico suficiente de curto: capacitores e outras cargas podem afetar a leitura. Se houver dúvida, não energizar para descobrir.

ANOTAR PARA A PRÓXIMA ETAPA
[ ] Modelo/etiqueta da câmera recebida, se identificável.
[ ] Modelo/etiqueta dos servos.
[ ] Inscrições e eventuais diferenças no módulo AITRIP.
[ ] Headers já montados ou solda ainda necessária.
[ ] Cabo USB-C de dados disponível.
[ ] Multímetro, botão e fonte dos motores disponíveis ou faltantes.

PAREM AQUI
Vocês já terão adiantado a preparação e a montagem passiva. Não ligar USB com a montagem conectada nesta etapa, não conectar a bateria e não energizar os servos.

A próxima etapa só deve começar com instruções de gravação e um firmware cuja compilação tenha sido aprovada. Mesmo assim, inicialização, corrente, áudio, câmera, display, rede e movimento precisarão de testes nas peças reais.
Não há como garantir remotamente 100% de funcionamento ou segurança de uma montagem física.

REFERÊNCIAS PARA IDENTIFICAR AS PEÇAS
Pinagem e introdução da XIAO:
https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/
Câmera Sense:
https://wiki.seeedstudio.com/xiao_esp32s3_camera_usage/
Funções do MAX98357: referência Adafruit, sem presumir SD/GAIN idênticos no AITRIP:
https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/pinouts
Pan-tilt comprado:
https://www.adafruit.com/product/1967
SH1106: identificação do anúncio JAMHER B0F3D34FDC nas capturas enviadas por Ricardo."""),
]


def wrapped_lines(text, width=507, size=10.5):
    result = []
    for paragraph in text.splitlines():
        line = ""
        for word in paragraph.split():
            candidate = (line + " " + word).strip()
            if line and fitz.get_text_length(candidate, fontsize=size) > width:
                result.append(line)
                line = word
            else:
                line = candidate
        result.append(line)
    return result


def main():
    document = fitz.open()
    for number, (title, body) in enumerate(PAGES, 1):
        page = document.new_page(width=595, height=842)
        page.draw_rect(fitz.Rect(0, 0, 595, 12), color=None, fill=(0.04, 0.32, 0.45))
        page.insert_text((44, 46), title, fontsize=19, fontname="hebo", color=(0.04, 0.25, 0.36))
        lines = wrapped_lines(body)
        if len(lines) > 56:
            raise ValueError(f"Page {number} exceeds its layout: {len(lines)} lines")
        for index, line in enumerate(lines):
            page.insert_text((44, 76 + index * 12.7), line, fontsize=10.5)
        page.insert_text((44, 818), "PROJETO EM FAMÍLIA | Preparação sem energia | 24/10/2026", fontsize=8)
        page.insert_text((525, 818), f"{number}/{len(PAGES)}", fontsize=8)
    document.set_toc([[1, title, index] for index, (title, _) in enumerate(PAGES, 1)])
    document.set_metadata({"title": "Robô de mesa - O que já podemos fazer", "author": "Projeto em família"})
    output = ROOT / "robo-comecem-por-aqui.pdf"
    document.save(output)
    document.close()
    print(output)


if __name__ == "__main__":
    main()
