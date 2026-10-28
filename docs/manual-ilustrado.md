# Manual ilustrado para iniciantes

**[Abrir o PDF de 27 páginas](../guia-ilustrado-iniciantes.pdf)**. Os desenhos abaixo são uma prévia; o PDF contém a sequência de ações, os pré-requisitos e as conferências.

**Hardware ainda não testado.** Estes são diagramas de uma ligação proposta, não prova de funcionamento físico. A placa e os módulos ficam **fora** da protoboard, sobre suporte não condutivo; apenas os jumpers entram nos furos. Isso evita depender de uma posição de encaixe da XIAO ainda não conferida.

Não conectar USB, bateria ou fonte dos motores durante qualquer alteração das ligações. A LiPo não faz parte deste circuito.

## 1. Entender a protoboard

![Grupos A-E, grupos F-J e separação entre linhas](images/breadboard-basics.svg)

A10, B10, C10, D10 e E10 pertencem à mesma conexão interna. F10–J10 pertencem a outra. A10 e A11 não são ligados entre si. Confirmar na unidade real por continuidade, sem energia.

![Barramentos laterais, que não serão usados neste layout](images/breadboard-rails.svg)

Não usar barramentos laterais neste layout; eles podem ter interrupções.

![Curto errado e uso correto de linhas separadas](images/avoid-short.svg)

## 2. Reconhecer conectores e orientação

![Jumper fêmea-macho](images/jumper-connectors.svg)

Esta estratégia precisa de jumpers **fêmea-macho** e headers macho **já soldados** nos módulos. Não usar header apenas encostado. Se faltar solda ou o tipo correto de cabo, parar nessa peça.

![Pinagem da XIAO ESP32-S3, USB para cima](images/xiao-top-pinout.svg)

Redesenho funcional a partir da [pinagem oficial Seeed](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/). USB para cima, vista pelo lado dos componentes. Não espelhar. Neste firmware, OLED usa **D0/D1**, não os pinos I2C padrão D4/D5.

## 3. Layout de distribuição

![Mapa de sinais e linhas numeradas](images/layout-summary.svg)

Usar uma protoboard comum A-J com ao menos 22 linhas numeradas. F-J fica vazio. Linhas 14 e 19 ficam vazias. Os nomes de pinos nas caixas dos desenhos seguintes **não representam a ordem física dos conectores**: identificar a inscrição na peça.

| Furo(s) | Ligação proposta |
|---|---|
| A10, B10, C10 | XIAO GND, OLED GND, MAX98357 GND |
| A11, B11 | XIAO 3V3, OLED VCC |
| A12, B12 | XIAO D0/GPIO1, OLED SDA |
| A13, B13 | XIAO D1/GPIO2, OLED SCL |
| A15, B15 | XIAO 5V, MAX98357 VIN |
| A16, B16 | XIAO D6/GPIO43, MAX98357 BCLK |
| A17, B17 | XIAO D4/GPIO5, MAX98357 LRC/LRCK |
| A18, B18 | XIAO D8/GPIO7, MAX98357 DIN |

Cada furo recebe no máximo um fio. Em cada linha, a tira interna faz a conexão entre os dois furos; não adicionar uma ponte entre eles.

## 4. OLED, um sinal por etapa

![OLED GND: XIAO GND em A10 e OLED GND em B10](images/oled-gnd.svg)

![OLED VCC: XIAO 3V3 em A11 e OLED VCC em B11](images/oled-vcc.svg)

![OLED SDA: XIAO D0 em A12 e OLED SDA em B12](images/oled-sda.svg)

![OLED SCL: XIAO D1 em A13 e OLED SCL em B13](images/oled-scl.svg)

## 5. Amplificador, um sinal por etapa

![Amplificador GND em C10; reutilizar o fio XIAO GND já existente em A10](images/amp-gnd.svg)

![Amplificador VIN: XIAO 5V em A15 e VIN em B15](images/amp-vin.svg)

![Amplificador BCLK: XIAO D6 em A16 e BCLK em B16](images/amp-bclk.svg)

![Amplificador LRC: XIAO D4 em A17 e LRC em B17](images/amp-lrc.svg)

![Amplificador DIN: XIAO D8 em A18 e DIN em B18](images/amp-din.svg)

Não alterar SD/GAIN sem identificar a unidade real e sua documentação.

## 6. Falante

![Um único falante entre SPK+ e SPK-, sem ligação a GND](images/speaker-output.svg)

## 7. Botão opcional e limites dos motores

![Botão: identificar pares por continuidade antes de ligar](images/head-button.svg)

O botão de quatro pernas é um exemplo elétrico; confirmar os pares da peça real. Se não souber identificá-los, não montar. A20 recebe D7/GPIO44; B20 recebe um contato de um par; D10 (GND) recebe um contato do outro par. Usar fios e manter o botão fora da protoboard caso o encaixe não esteja confirmado.

![Separação das fontes: planejamento, não instrução de ligação dos motores](images/separate-power.svg)

**Parar antes de montar/energizar os servos.** Fonte, terminais de potência, sinal 3,3 V e mecânica ainda exigem identificação/revisão. Não fazer corrente de motor passar pela XIAO ou pela linha fina de referência GND.

## O que falta comprovar

Gravação e inicialização reais; qualidade do display, áudio e câmera; ativação e visão no backend; estabilidade de alimentação; movimento e corte físico dos servos. O PDF contém os pontos de controle, mas não marca testes não realizados como aprovados.

Fotos das unidades desligadas, com inscrições legíveis, permitirão conferir a orientação dos módulos e fechar as instruções dos conectores dos motores. Não enviar dados pessoais, recibos ou fotografias de pessoas.
