from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parent
PAGES = [
("Robô de mesa com IA", """GUIA DE EXECUÇÃO: MONTAGEM, CÓDIGO, NUVEM E TESTES
Projeto em família | Revisão: 24/10/2026
Idioma do robô: inglês. Possível apresentação no clube de robótica.

O QUE VOCÊS VÃO CONSTRUIR
Um robô de mesa que escuta, responde por voz, mostra expressões e texto no OLED SH1106, descreve uma fotografia quando solicitado e movimenta uma cabeça leve com dois servos. Ele usa Wi-Fi e IA na nuvem; não exige computador ligado depois de gravado e configurado.

A primeira versão funciona ligada à energia: USB para a placa/áudio e uma fonte separada para os servos. Isso é funcionamento autônomo, mas não é funcionamento pela LiPo comprada. A LiPo fica guardada, com conector intacto. A versão portátil com essa bateria não está incluída como circuito pronto.

O QUE MUDA EM RELAÇÃO AO PDF ORIGINAL
Vocês não usarão o binário AI Pin. Este pacote fornece uma implementação própria de placa para o XiaoZhi, com SH1106, microfone PDM, câmera e ferramentas MCP de movimento. O tilt vai para GPIO6, não GPIO3. Um botão adicional habilita os motores fisicamente. Atualizações de firmware pela rede são bloqueadas para preservar a pinagem personalizada.

IMPORTANTE SOBRE A VALIDAÇÃO
O firmware completo compilou e passou pelo link com ESP-IDF 6.0.1. O pacote já inclui robot.bin para ensaio, além do código-fonte. Não é necessário instalar o SDK nem recompilar para a primeira gravação.

A imagem ESP32-S3 foi inspecionada, com checksum e hash internos válidos, e cabe na flash. Os testes nas peças reais e a ativação em nuvem continuam pendentes. Ver VALIDACAO.txt. Compilação aprovada não significa funcionamento físico aprovado ou certificação à distância.

Não prossigam se um ponto de controle falhar. Não substituam etapas por frases como 'deve funcionar'. Não há garantia de funcionamento perfeito do serviço externo ou das respostas da IA.

DIVISÃO DO PROJETO
1. Preparar ferramentas e firmware.
2. Montar e validar display, câmera e áudio.
3. Configurar Wi-Fi, conta e inglês.
4. Integrar os motores e testar limites.
5. Fixar a montagem numa base e ensaiar a apresentação.

Não misturar a pinagem deste documento com tutoriais de outras placas ou com o guia original. Guardar este PDF junto do pacote de código."""),
("1. Peças e complementos", """PEÇAS JÁ COMPRADAS
Seeed XIAO ESP32-S3 Sense com câmera e microfone.
JAMHER HXR-1.3inch-1Blue, ASIN B0F3D34FDC: OLED 1,3 pol., 128x64, I2C, SH1106 segundo a descrição do vendedor.
AITRIP MAX98357 I2S: usar um módulo do pacote.
Gikfun EK1794: usar UM alto-falante 4 ohms, 3 W.
Adafruit 1967: conjunto pan-tilt com dois microservos.
Capacitor eletrolítico 470 uF, 25 V: usar um junto dos servos.
Headers OCR 2,54 mm, protoboards e jumpers BOJACK.
Kit de solda Plusivo 60 W / 120 V.
LiPo EEMB 803048, 3,7 V / 1200 mAh: NÃO conectar nesta versão.

COMPLEMENTOS NECESSÁRIOS, SE NÃO HOUVER EM CASA
Multímetro digital para tensão DC e continuidade.
Cabo USB-C de dados e alimentação USB de boa qualidade, 5 V, capacidade mínima proposta de 2 A para placa e áudio; começar com volume baixo. Uma porta fraca do computador pode não sustentar o áudio.
Fonte regulada de 5 V para motores, com margem de corrente: proposta de bancada de 4 A, não consumo esperado constante.
Exemplo documentado: Adafruit 1466, 5 V / 4 A, com adaptador de borne Adafruit 368 (conector 2,1 mm, positivo no centro).
https://www.adafruit.com/product/1466
https://www.adafruit.com/product/368

Um botão momentâneo normalmente aberto, adequado para protoboard.
Interruptor DC para cortar o positivo dos servos, nominal para pelo menos 5 V / 4 A, com terminais isolados.
Fios de potência curtos, por exemplo 22 AWG, e distribuição por bornes adequados, não por longas cadeias de jumpers de sinal.
Termorretrátil/isolamento, proteção ocular, suporte e base resistentes ao calor para solda. Base rígida para o robô e fixadores leves para o OLED.

A fonte maior não força 4 A nos servos, mas pode fornecer corrente perigosa em curto. Usar fonte com proteção documentada e manter todos os condutores isolados. Não abrir fontes de tomada nem trabalhar em tensão de rede.

Não comprar conversor boost, outro display ou outra placa antes dos testes. Não presumir proteção ou corrente máxima da LiPo pelo nome EEMB ou pelo título do anúncio."""),
("2. Distribuição de alimentação", """DOIS CIRCUITOS DE ALIMENTAÇÃO, COM TERRA COMUM
A: alimentação USB -> conector USB-C da XIAO.
XIAO 3V3 -> VCC do OLED.
XIAO 5V -> VIN do amplificador MAX98357.
XIAO GND -> GND do OLED e do amplificador.

B: fonte externa regulada 5 V -> interruptor DC -> positivos dos dois servos.
Negativo da fonte B -> terras dos dois servos.
Negativo da fonte B -> GND da XIAO, por ligação dedicada de referência.
O retorno de corrente dos motores deve voltar diretamente à fonte B, não passar pela placa XIAO.

NÃO UNIR O +5 V DA FONTE B AO PINO 5V DA XIAO.
NÃO UNIR OS POSITIVOS DAS DUAS FONTES.
O GND comum é necessário para a referência do sinal; ele não transforma as fontes numa fonte única.

CAPACITOR
Capacitor 470 uF entre o positivo PÓS-interruptor dos motores e o GND da fonte B, perto dos servos. A faixa marcada '-' identifica o terminal negativo. Conferir a polaridade no componente; comprimento das pernas pode já ter sido alterado.
25 V é a tensão nominal do capacitor, não a tensão de alimentação.

ORDEM DE ENERGIZAÇÃO
1. Interruptor dos motores desligado.
2. Alimentar XIAO por USB e aguardar inicialização.
3. Ligar a fonte/interruptor dos motores.
4. Só habilitar PWM pelo botão físico quando a montagem estiver livre.
Para desligar: cortar motores primeiro, depois desligar USB.

ANTES DO PRIMEIRO USO
Com a fonte B desconectada dos servos, medir tensão e polaridade nos bornes com multímetro em tensão DC. Nunca colocar o multímetro em corrente diretamente entre +5 V e GND: isso cria um curto.
Se houver dúvida sobre medição ou polaridade, parar e pedir ajuda presencial.

Esta arquitetura elimina a ligação improvisada da LiPo. Não promete isolamento de ruído completo; a integração ainda precisa passar pelo ensaio com motores e áudio ao mesmo tempo."""),
("3. Tabela única de ligações", """PLACA DESLIGADA DURANTE TODA ALTERAÇÃO
Identificar os nomes D0...D10 na placa e conferir a pinagem oficial Seeed.

OLED SH1106
GND -> GND da XIAO
VCC -> 3V3 da XIAO
SCL -> D1 / GPIO2
SDA -> D0 / GPIO1
O anúncio declara 3,3-5 V; usar 3,3 V neste projeto para os sinais I2C.
A ordem na foto do anúncio é GND, VCC, SCL, SDA. Conferir na unidade real.

MAX98357
VIN -> 5V da XIAO, disponível com alimentação USB
GND -> GND da XIAO
BCLK -> D6 / GPIO43
LRC ou LRCK -> D4 / GPIO5
DIN -> D8 / GPIO7
SPK+ -> um terminal do alto-falante
SPK- -> outro terminal do mesmo alto-falante
Nenhum terminal do alto-falante vai ao GND. Não ligar dois falantes em paralelo.

Não presumir que pinos SD/GAIN têm a mesma polarização do módulo Adafruit. Na primeira montagem, manter a configuração de fábrica do AITRIP; se não houver áudio, verificar o esquema do módulo antes de alterar SD/GAIN.

MOTORES
Sinal PAN -> D3 / GPIO4
Sinal TILT -> D5 / GPIO6
Alimentação e terra -> fonte B, conforme a página anterior
Identificar sinal/positivo/terra pelo servo real; não adivinhar pela cor.
Este guia NÃO utiliza GPIO3 para motores.

BOTÃO ADICIONAL DE CABEÇA
Um contato -> D7 / GPIO44
Outro contato -> GND
Usa pull-up interno. Se o botão tiver quatro pernas, dois terminais de cada lado podem já estar unidos; identificar com continuidade, sem alimentação.

INTERNOS, SEM NOVOS JUMPERS
Microfone PDM: clock GPIO42, dados GPIO41.
Câmera: conexões da expansão Sense, inicializadas no código fornecido.
BOOT/GPIO0: botão já existente da placa.
Não instalar microSD: este projeto já usa GPIO7 no áudio e não inclui armazenamento SD."""),
("4. Preparar a bancada", """PAPÉIS
Sua filha pode conferir o mapa, organizar fios, acompanhar os logs, testar funções e explicar o projeto. Solda e medições com alimentação exigem supervisão adequada. O adulto revisa potência, fontes e polaridade.

1. Separar e etiquetar placa, OLED, amplificador e fios de cada servo.
2. Fotografar os dois lados das placas antes da montagem.
3. Instalar a antena conforme a orientação da Seeed, alinhando o conector sem forçar lateralmente.
4. Com tudo desligado, conferir o encaixe da expansão Sense.
5. Inspecionar headers. Soldar somente os necessários à montagem; não aquecer ou apoiar o ferro sobre a bateria.
6. Usar suporte do ferro, base resistente ao calor, proteção ocular e ventilação/extração de fumos. Papel ou pano não são proteção de bancada para solda.
7. Inspecionar pontes de solda com ampliação. Soldas sem chumbo nem sempre ficam brilhantes; brilho não é critério suficiente de qualidade.
8. Mapear as trilhas de alimentação da protoboard; algumas têm interrupções no meio.
9. Deixar a LiPo fora da bancada de solda e desconectada.

PONTO DE CONTROLE A: PLACA SOZINHA
Antes de substituir o firmware, conectar apenas a XIAO ao computador por cabo de dados. Confirmar enumeração USB no Gerenciador de Dispositivos. Usar a documentação Seeed para o teste de fábrica/câmera e recuperação, se necessário.
https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/

Não concluir que a placa está defeituosa só porque não aparece em 'Portas': modo USB e drivers podem alterar a enumeração. Tentar cabo de dados conhecido e modo BOOT.

Modo BOOT documentado pela Seeed: desconectar USB, segurar BOOT, conectar USB mantendo BOOT e depois soltar. Fazer com motores e LiPo desconectados. RESET com BOOT pressionado também é uma opção durante alimentação.

Se a placa aquecer anormalmente, houver cheiro ou fonte entrar em proteção, desligar imediatamente. Não continuar conectando componentes para 'ver se melhora'."""),
("5. Preparar o Windows", """CAMINHO MAIS SIMPLES: GRAVAR O BINÁRIO INCLUÍDO
O computador é necessário para gravar, não para operar o robô depois. A compilação já foi executada. ESP-IDF só será necessário se vocês quiserem recompilar ou alterar o código.

1. Extrair robo-de-mesa-completo.zip para C:\\robot.
A pasta deve conter flash.ps1, guia-completo.pdf e firmware-built. Se a extração criar uma pasta adicional, entrar nela ou ajustar o caminho dos comandos.
2. Abrir PowerShell comum e conferir:
python --version
Usar Python 3.11 ou 3.12. Se não houver Python, instalar a partir do site oficial e abrir um novo terminal:
https://www.python.org/downloads/windows/
3. Preparar uma ferramenta de gravação isolada nesta pasta:
Set-Location C:\\robot
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install esptool==5.6.0

Não é necessário ativar a venv nem mudar permanentemente a política do Windows. O flash.ps1 encontra esse Python local automaticamente. Guardar qualquer erro e parar se a instalação falhar.

PONTO DE CONTROLE B
Conferir a ferramenta:
.\\.venv\\Scripts\\python.exe -m esptool version
Deve indicar esptool 5.6.0.
Conferir que existem firmware-built\\robot.bin e firmware-built\\manifest.json.
Ainda não executar a gravação: ela vem depois da revisão das ligações na seção 7.

QUAL É ESTE BINÁRIO
Firmware XiaoZhi 2.5.3 com placa personalizada xiao-family-robot; interface em inglês; wake word desabilitada; flash de 8MB em DIO.
Imagem de aplicação: 2.493.152 bytes, dentro da partição de 3.080.192 bytes. Imagem mesclada: 6.561.337 bytes.
O hash SHA256 da imagem mesclada está em manifest.json e será conferido antes da gravação.

O arquivo não é o binário AI Pin do PDF original. Não misturar imagens, offsets ou pinagens.

RECOMPILAR É OPCIONAL
A próxima página explica como reproduzir ou modificar o software. Para usar o binário incluído sem alterações, seguir diretamente para a seção 7."""),
("6. Recompilar, se necessário", """ESTA PÁGINA É OPCIONAL PARA A PRIMEIRA MONTAGEM
O pacote já traz firmware compilado. Recompilar será necessário para alterações de código, como inverter um eixo após o teste de direção.

1. Instalar o Espressif Installation Manager oficial:
https://dl.espressif.com/dl/eim/
Selecionar ESP-IDF v6.0.1 e ferramentas para ESP32-S3.
2. Abrir o ambiente PowerShell da instalação e conferir:
idf.py --version
Deve indicar v6.0.1.
3. Preparar e compilar:
Set-Location C:\\robot
python .\\prepare_source.py
powershell -ExecutionPolicy Bypass -File .\\build.ps1

O Bypass vale apenas para esse processo, não exige mudar permanentemente a política do Windows. Se a escola ou o computador corporativo bloquearem scripts, usar um computador autorizado; não contornar políticas administrativas.

O preparo baixa a revisão pública fixada:
f443114fe7c3fa26b10d3630090119891cd1c4fd
Verifica hashes dos três arquivos upstream alterados, aplica os patches e copia a resolução de dependências já compilada, preservada em firmware-built\\dependencies.lock.

O fonte fica em C:\\robot\\work\\xiaozhi. Uma pasta existente não será sobrescrita. Para preparar do zero, extrair o pacote em outro diretório vazio.

PONTO DE CONTROLE C
Sem recompilação: o hash de robot.bin deve coincidir com manifest.json, como verifica flash.ps1.
Com recompilação: exigir término sem erros e novos arquivos:
C:\\robot\\firmware-built\\robot.bin
C:\\robot\\firmware-built\\manifest.json
C:\\robot\\firmware-built\\sdkconfig.txt
Guardar também dependencies.lock.

robot.bin é uma imagem mesclada, para gravação a partir de 0x0. Não usar com ela os cinco offsets do PDF antigo. Manifesto e SHA256 serão conferidos pelo script de gravação.

Se houver erro, não substituir o binário aprovado por saída parcial. Guardar o primeiro erro real, não apenas a última linha 'build failed'. A compilação em Windows não foi executada nesta revisão; o binário incluído foi compilado em Linux/WSL.

Atualizações de firmware pela rede são bloqueadas nesta placa personalizada. Atualizações futuras devem ser revisadas, recompiladas e gravadas por USB, preservando a pinagem e as proteções de movimento."""),
("7. Montar display e áudio", """DESLIGAR TODAS AS FONTES
1. Ligar somente o OLED à XIAO, seguindo a tabela única.
2. Ligar o amplificador conforme a mesma tabela.
3. Fixar um único alto-falante aos terminais SPK+ e SPK-.
4. Revisar continuidade e ausência de pontes/curtos com tudo sem energia.
5. Manter fontes dos servos, servos e LiPo desconectados.

O VIN do amplificador vem do pino 5V da XIAO nesta configuração USB. A potência do áudio depende da alimentação real. A documentação de referência do MAX98357A admite 4 ohms; ela não certifica cada módulo AITRIP.

GRAVAÇÃO
Conectar USB de dados, entrar em modo BOOT se necessário e identificar a porta real, por exemplo COM5.
No PowerShell, usando o ambiente local preparado na seção 5:
Set-Location C:\\robot
powershell -ExecutionPolicy Bypass -File .\\flash.ps1 -Port COM5

Trocar COM5 pela porta real. O script verifica o hash e grava em 115200 baud, priorizando confiabilidade. Não precisa apagar toda a flash preventivamente.

Ao terminar, pressionar RESET se necessário. A verificação da gravação confirma a transferência, não o funcionamento do robô.

LOG SERIAL
Para diagnóstico, sem precisar instalar ESP-IDF:
Set-Location C:\\robot
.\\.venv\\Scripts\\python.exe -m serial.tools.miniterm --rts 0 --dtr 0 COM5 115200
Fechar com Ctrl+] antes de tentar gravar novamente. A porta pode mudar depois do reset ou da troca de modo USB.
Abrir o monitor e pressionar RESET para capturar a inicialização. Usar o cabo USB de dados.

PONTO DE CONTROLE D
Logs incluem 'SH1106 initialized' e 'Camera ready', sem erro fatal.
O código procura o display nos endereços 0x3C e 0x3D e exige apenas um responder.
O OLED deve mostrar a interface de inicialização/configuração, sem colunas cortadas ou imagem deslocada.

O código começa com volume 20 e motores desabilitados. Um estalo no alto-falante NÃO prova que o áudio está correto. Se não houver interface, diagnosticar antes de continuar."""),
("8. Wi-Fi e primeira conversa", """CONFIGURAR A REDE
1. Com USB conectado e motores sem energia, aguardar a configuração Wi-Fi.
2. No celular ou computador, escolher a rede criada pelo dispositivo, usando o nome exibido no OLED/log.
3. Abrir o portal indicado pelo dispositivo. Se não abrir automaticamente, usar o endereço mostrado; não presumir um IP universal.
4. Selecionar uma rede de 2,4 GHz compatível e informar a senha.
5. Aguardar reconexão e obter o código de ativação apresentado pelo dispositivo.

NÃO É QUALQUER REDE ESCOLAR
Começar em casa, com rede doméstica autorizada, sem portal cativo ou autenticação corporativa. O suporte a Wi-Fi 2,4 GHz não implica suporte automático a todo método de autenticação de uma escola.

ATIVAR A IA
Abrir https://xiaozhi.me no navegador e seguir o fluxo atual de conta e associação do dispositivo usando o código exibido. Fazer a conta sob responsabilidade do adulto e revisar termos, limites, tratamento de dados e elegibilidade de uso por menores.

Os nomes das opções da interface podem mudar. Esta revisão não acessou uma conta autenticada nem comprovou a disponibilidade do serviço para esta placa personalizada. Se ativação, idioma ou visão não estiverem disponíveis, parar neste ponto; não considerar a integração em nuvem aprovada.

Configurar o assistente para conversar em inglês, com voz em inglês quando disponível e respostas curtas. A linguagem da interface local e a linguagem do modelo/voz são configurações diferentes.

USO DO BOOT
Clique curto durante a operação inicia/alterna a conversa conforme o fluxo XiaoZhi. Clicar novamente permite interromper/encerrar conforme o estado. Observar o indicador de escuta; não confundir isso com push-to-talk garantido.
Manter BOOT pressionado durante a operação entra na configuração Wi-Fi e desabilita os motores. Não confundir com segurar BOOT ao conectar USB, que é modo de gravação.

PONTO DE CONTROLE E
Fazer dez interações curtas em inglês. Exemplos:
'Hello. Please answer in English.'
'Tell me one short robot joke.'
'Set your volume to twenty percent.'
Confirmar que ela é ouvida, a resposta chega pelo alto-falante e não há reinicialização. Não manter o falante colado ao microfone."""),
("9. Fazer a câmera enxergar", """OBJETIVO EXATO
Descrever uma fotografia sob comando. Não é rastreamento contínuo, câmera de segurança ou reconhecimento confiável de pessoas.

1. Manter uma boa iluminação e a câmera desobstruída.
2. Mostrar um objeto simples sem pessoas, documentos ou telas pessoais.
3. Pedir em inglês: 'Take a photo and describe the object in front of you.'
4. Observar no log uma captura de frame e o resultado da chamada de câmera.
5. Trocar o objeto e repetir. Fazer pelo menos três tentativas independentes.

PONTO DE CONTROLE F
Houve captura e envio comprovados no log, e a resposta é coerente com o objeto apresentado. Uma descrição plausível sozinha não comprova uso da câmera: a IA pode responder sem ter recebido a imagem.

O backend precisa disponibilizar interpretação de imagem, não apenas conversa por voz. O código upstream usa configuração de URL/token de explicação recebida do serviço. Não inventar um endpoint nem colar uma chave de API aleatória no firmware para contornar erro.

Se aparecer 'Image explain URL or token is not set', a integração de visão do serviço ainda não foi configurada. Não é defeito que trocar os fios do OLED resolva.

MODELO DA CÂMERA
O código usa o mapa oficial da expansão Sense e o driver esp32-camera do upstream. A unidade real ainda precisa ser aprovada. A Seeed documenta mudanças entre sensores; o log registra o PID detectado.
Este pacote não implementa um ajuste específico de autofoco. Não prometer foco automático só porque determinada versão da câmera dispõe desse recurso.

ONDE A CÂMERA FICA
Nesta montagem inicial, XIAO e câmera ficam juntas no corpo/base. O OLED é o rosto na plataforma móvel. Portanto, mover o rosto NÃO muda o enquadramento da câmera.

Isso evita presumir um extensor de câmera não comprado ou colocar placa, bateria e todos os cabos na cabeça sem medir carga. Se desejarem que a câmera acompanhe o rosto, isso exige uma revisão mecânica e de cabos, não apenas mudar o prompt."""),
("10. Alimentar os motores", """SÓ COMEÇAR APÓS DISPLAY, VOZ E VISÃO APROVADOS
Desligar USB e fonte B. Não instalar carga na plataforma ainda.

1. Identificar qual servo faz pan e qual faz tilt.
2. Montar a distribuição da fonte B por bornes.
3. Positivo da fonte -> interruptor -> positivos dos servos.
4. Negativo da fonte -> terras dos servos e GND da XIAO.
5. Capacitor 470 uF entre positivo pós-interruptor e negativo.
6. Sinal do pan -> D3/GPIO4.
7. Sinal do tilt -> D5/GPIO6.
8. Botão adicional -> D7/GPIO44 e GND.
9. Inspecionar fios e isolar todos os terminais de potência.

VERIFICAR SEM CARGA
Ligar USB primeiro. Aguardar inicialização: log 'Head DISARMED'.
Ligar a alimentação dos servos. O código ainda não envia pulsos. Servos podem ter transientes próprios ao receber energia; manter dedos fora da mecânica.
Segurar o botão adicional por aproximadamente dois segundos para habilitar. O OLED mostra 'HEAD ARMED'. Os dois sinais começam no centro nominal de 1500 us.

PONTO DE CONTROLE G
Nenhum cabo é tracionado, nenhum eixo fica travado ou zumbindo continuamente, a XIAO não reinicia e os servos não aquecem anormalmente.

Se houver esforço contra o batente, cortar a energia dos servos imediatamente. Nunca tentar resolver um travamento mandando girar mais.

IMPORTANTE SOBRE O KIT MONTADO
Ele pode já vir montado mecanicamente fora do centro desejado. Não desmontar sob energia. Para reposicionar um braço, desligar os motores, apoiar a plataforma e seguir a montagem do fabricante.

O sinal é de 3,3 V. A aceitação precisa ser verificada com os servos entregues; não ligar 5 V a um GPIO da XIAO. Se o servo não reconhecer o sinal apesar de alimentação e referência corretas, investigar sua especificação e eventual buffer lógico apropriado, em vez de aplicar tensão maior ao GPIO."""),
("11. Calibração e movimento", """O BOTÃO ADICIONAL TEM DUAS FUNÇÕES
Segurar aproximadamente dois segundos: alterna habilitado/desabilitado.
Clique curto, quando habilitado: próximo passo do teste local.
O teste local não depende de IA e percorre:
centro; pan -5; centro; pan +5;
centro; tilt -5; centro; tilt +5; e repete.

O QUE -5 SIGNIFICA
São posições lógicas, NÃO graus. O código usa centro 1500 us e 10 us por unidade; o intervalo permitido -10...10 corresponde inicialmente a 1400...1600 us. Movimento real depende do servo e da montagem.

O controlador aproxima o pulso do alvo em passos de até 5 us a cada 20 ms depois de habilitado. Isso limita a velocidade do sinal comandado, não mede velocidade física nem impede trancos de energização/centralização.

ANTES DE COLOCAR O OLED
Executar pelo menos dois ciclos locais sem carga. Verificar se pan e tilt correspondem ao esperado.
Se a direção estiver invertida, desligar e alterar apenas kPanSign ou kTiltSign de 1 para -1 em board\\head_policy.h. Não inverter os fios de potência do servo.
Repetir a preparação em pasta nova e recompilar; o diretório work já preparado não se atualiza automaticamente ao editar board.

Não ampliar os limites para 0-180 graus. O curso conservador desta versão é intencional. Qualquer ampliação exige nova revisão da mecânica.

CONTROLE PELA IA
Após aprovação local, clicar BOOT e pedir:
'Use your head tool to set pan to minus five and tilt to zero.'
'Use your head tool to set pan to zero and tilt to five.'
'Center your head.'

As ferramentas fornecidas são self.head.move, self.head.status e self.head.off. A IA não recebe ferramenta para habilitar motores; isso exige o botão local.

PONTO DE CONTROLE H
Vinte movimentos combinados, sem colisão, travamento ou reset. Confirmar logs 'Head target accepted' e movimento real. O código confirma alvo aceito, não posição medida: não há sensor de feedback externo.

'Turn your head off' pode desabilitar PWM e fazer a cabeça relaxar. Apoiar a carga antes. Para emergência, usar o corte físico da fonte dos motores."""),
("12. Montagem final na base", """ACABAMENTO FUNCIONAL SEM IMPRESSÃO 3D OBRIGATÓRIA
Usar uma base rígida e estável, sem condutores expostos embaixo. Uma placa de montagem não condutiva já pronta evita cortar material durante a sessão.

1. Fixar o pan-tilt pelo suporte da base, sem apertar ou deformar os servos.
2. Fixar SOMENTE o OLED na plataforma móvel, usando suporte leve e isolamento da placa.
3. Manter XIAO/câmera, amplificador e alto-falante na parte fixa.
4. Separar o alto-falante do microfone para reduzir realimentação acústica.
5. Deixar lente, microfone, antena e dissipação térmica desobstruídos.
6. Deixar acesso ao BOOT, ao botão adicional e ao corte de energia.
7. Dar folga aos quatro fios do display para todo o curso permitido. Fixar a folga longe das articulações.
8. Substituir ligações frouxas por conexões firmes e isoladas antes de transportar.

Não soldar componentes ou conectores com qualquer fonte ligada. Não apoiar uma placa nua sobre metal ou parafusos.

SE FOREM IMPRIMIR UMA CARCAÇA
Medir as peças reais com régua/paquímetro e testar um molde de papel antes da impressão. Não usar dimensões de furo, encaixe ou lente inventadas a partir do anúncio.
Começar com corpo aberto ou tampa removível. Prever ventilação, fixação, acesso aos controles e alívio de tração dos cabos.
Não colocar a LiPo dentro da carcaça 'para usar depois' enquanto não houver circuito de alimentação validado.

PONTO DE CONTROLE I
Repetir os testes com o OLED instalado: o peso e os cabos mudam o esforço dos motores. Manter a base apoiada e impedir que a cabeça atinja o corpo.
Executar trinta minutos de uso alternando voz, fotografias e movimentos.

Inspecionar resets, quedas de tensão, zumbido, aquecimento, imagem deslocada e cabos tensionados. Não segurar um eixo para simular travamento.

Ao terminar, desligar motores antes de tirar a alimentação USB. O fato de uma sessão ter funcionado não elimina a inspeção antes de cada uso."""),
("13. Uso na escola", """CHECKLIST COM O PROFESSOR
Confirmar autorização para dispositivo com câmera, microfone e IA externa.
Verificar rede 2,4 GHz autorizada e possibilidade de uso de conta/serviço externo. Não tentar contornar filtros da escola.
Combinar como evitar captar colegas. Apresentar objetos sem pessoas, nomes ou documentos na imagem.
Verificar disponibilidade de tomada e uso das fontes, ou outro arranjo de alimentação previamente aprovado.

COMO ELA PODE APRESENTAR EM INGLÊS
Explicar que o microcontrolador captura áudio/imagem e controla display/motores; a IA de conversa e visão está na nuvem.
Mostrar o OLED e o teste local pelo botão.
Fazer uma pergunta curta e mostrar a resposta falada.
Apresentar um objeto e solicitar uma foto.
Mostrar um comando de pan/tilt e explicar os limites e a habilitação física.
Explicar que uma resposta da IA pode estar errada e que o movimento não tem confirmação por sensor.

PLANO SEM INTERNET
O teste local dos motores não depende de chamadas de IA. Ensaiá-lo sem internet ANTES da escola para conferir também o comportamento da inicialização.
Guardar vídeo de uma demonstração doméstica sem dados pessoais, se autorizado, para explicar a parte de conversa/visão caso a rede falhe.
Não prometer conversa offline: este projeto usa nuvem.

TRANSPORTE
Desligar e desconectar todas as fontes. Proteger a montagem contra fios soltos e esforço na plataforma. Transportar o projeto apoiado pela base, nunca pelo OLED ou pelos cabos.
Levar as fontes corretas, cabo, tabela de pinagem e checklist. Não levar a LiPo solta com terminais desprotegidos.

PORTABILIDADE
Não ligar a LiPo comprada diretamente aos pinos de 5 V e não presumir que ela alimentará amplificador e servos pela XIAO. Esta versão pode ser apresentada ligada às fontes, sem computador.
Se uma versão sem tomada for necessária, escolher e testar uma solução regulada completa, como alimentação USB portátil apropriada, com corrente suficiente em cada saída e sem desligamento automático durante uso. Esse arranjo precisa de outro ensaio; nenhum power bank específico foi validado aqui."""),
("14. Diagnóstico sem adivinhação", """FALHA NA PREPARAÇÃO
Erro de hash/anchor: não é a revisão esperada. Não remover as verificações.
Erro de caminho longo: extrair em pasta curta, como C:\\robot.
Pasta work já existe: recompilar ou preparar em outra pasta vazia.

FALHA NA COMPILAÇÃO
idf.py não encontrado: abrir o ambiente correto da instalação ESP-IDF.
Versão diferente: usar v6.0.1. Não misturar SDKs no mesmo terminal.
Download de componente falhou: verificar conexão/proxy e mensagem original.
Erro de API/tipo: guardar o primeiro erro; não gravar um binário de outra placa como substituto.
CreateProcess/comando longo: usar caminho curto; o script habilita response files.

FALHA NA GRAVAÇÃO
Conferir COM, cabo de dados, BOOT, alimentação e monitor serial fechado.
Não usar erase-flash como primeira solução. Apagar toda a flash remove configurações e não corrige porta errada ou cabo ruim.

OLED APAGADO
Verificar 3V3, GND, SDA/SCL e inscrições na peça. O código já procura 0x3C/0x3D; não alterar endereços aleatoriamente. Driver selecionado é SH1106.

CÂMERA NÃO INICIALIZA
Desligar e conferir encaixe da expansão, câmera e modelo. Guardar PID/erro. Não trocar a pinagem interna por uma de ESP32-CAM de outra marca.

SEM ÁUDIO
Conferir VIN, GND, BCLK, LRC e DIN. Confirmar módulo AITRIP e estado de SD/GAIN na documentação do fornecedor. Falante fica entre SPK+ e SPK-.

VOZ FUNCIONA, FOTO NÃO
Verificar ferramenta de câmera e configuração de visão do backend. Uma conta que conversa não prova que oferece interpretação de imagem.

MOTORES NÃO MOVEM
Verificar fonte B, terra comum, botão local, log ARMED e sinais GPIO4/6.
Se o teste local funciona, mas o comando de voz não, revisar descoberta/chamada MCP no backend; não mexer na alimentação como primeira tentativa.

REINICIA COM MOVIMENTO
Cortar motores. Revisar distribuição de retorno, fonte, conexões, quedas de tensão e capacitor. Não aumentar o capacitor indefinidamente como substituto de diagnóstico.

FONTE EM PROTEÇÃO, CHEIRO OU AQUECIMENTO
Desligar imediatamente e inspecionar sem energia. Não insistir."""),
("15. Aprovação final e referências", """REGISTRAR DATA, RESULTADO E EVENTUAL ERRO
A. XIAO enumera por USB e não apresenta aquecimento anormal.
B. Fonte preparada da revisão correta, sem erro de hash/patch.
C. Binário incluído com hash correto, ou recompilação aprovada com manifesto.
D. Display íntegro e câmera inicializada no log.
E. Dez interações em inglês, sem resets.
F. Três fotografias capturadas de objetos diferentes e interpretação testada.
G. Motores sem carga habilitados localmente, sem esforço nos batentes.
H. Vinte movimentos dentro dos limites e corte de energia testado.
I. Trinta minutos com montagem final e fontes adequadas.
J. Inicialização sem computador e uso na rede autorizada confirmados.

Se C falhar, não gravar a imagem nem continuar a integração.
Se F falhar, o robô ainda não tem visão aprovada.
Se G/H falharem, manter a versão sem movimento até corrigir.
Estes são critérios iniciais de protótipo, não certificação de produto.

FONTES DO HARDWARE
https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/
https://wiki.seeedstudio.com/xiao_esp32s3_sense_mic/
https://wiki.seeedstudio.com/xiao_esp32s3_camera_usage/
https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/pinouts
https://www.adafruit.com/product/1967
https://www.adafruit.com/product/169
https://www.adafruit.com/product/1466
https://www.adafruit.com/product/368
OLED: capturas fornecidas por Ricardo do anúncio JAMHER B0F3D34FDC.

FONTES DO SOFTWARE
XiaoZhi ESP32, MIT, revisão fixada:
https://github.com/78/xiaozhi-esp32/tree/f443114fe7c3fa26b10d3630090119891cd1c4fd
Arquivos usados como referência: docs/custom-board.md, docs/mcp-usage.md, main/display/oled_display.h, main/audio/codecs/no_audio_codec.h, main/boards/common/esp32_camera.h, main/mcp_server.h e implementações das placas de protoboard.

Driver SH1106 já declarado no manifest upstream:
https://components.espressif.com/components/tny-robotics/sh1106-esp-idf/versions/1.0.1/readme
ESP-IDF: instalação e PWM:
https://docs.espressif.com/projects/esp-idf/en/v6.0.1/esp32s3/get-started/windows-setup.html
https://docs.espressif.com/projects/esp-idf/en/v6.0.1/esp32s3/api-reference/peripherals/ledc.html

VERIFICAÇÃO: ler também VALIDACAO.txt no pacote. Nenhuma destas referências equivale a um teste físico das peças de vocês."""),
]


def lines_for(text, width, size):
    lines = []
    for paragraph in text.splitlines():
        if not paragraph:
            lines.append("")
            continue
        words = []
        for word in paragraph.split():
            piece = ""
            for char in word:
                if fitz.get_text_length(piece + char, fontname="helv", fontsize=size) > width:
                    words.append(piece)
                    piece = char
                else:
                    piece += char
            if piece:
                words.append(piece)
        line = ""
        for word in words:
            trial = f"{line} {word}".strip()
            if line and fitz.get_text_length(trial, fontname="helv", fontsize=size) > width:
                lines.append(line)
                line = word
            else:
                line = trial
        lines.append(line)
    return lines


def main():
    document = fitz.open()
    for number, (title, body) in enumerate(PAGES, 1):
        page = document.new_page(width=595, height=842)
        page.draw_rect(fitz.Rect(0, 0, 595, 12), color=None, fill=(0.04, 0.32, 0.45))
        page.insert_text((40, 45), title, fontsize=18, fontname="hebo", color=(0.04, 0.25, 0.36))
        lines = lines_for(body, 515, 10)
        if len(lines) > 59:
            raise ValueError(f"Page {number} overflow: {len(lines)} lines")
        for index, line in enumerate(lines):
            page.insert_text((40, 70 + index * 12.1), line, fontsize=10)
        page.insert_text((40, 820), "XIAO FAMILY ROBOT | Guia de execução | 24/10/2026 | Ver VALIDACAO.txt", fontsize=8)
        page.insert_text((525, 820), f"{number}/{len(PAGES)}", fontsize=8)
    document.set_toc([[1, title, index] for index, (title, _) in enumerate(PAGES, 1)])
    document.set_metadata({"title": "Robô de mesa com IA - Guia completo de execução",
                           "author": "Projeto em família", "subject": "Montagem, firmware, nuvem e testes"})
    output = ROOT / "guia-completo.pdf"
    document.save(output)
    document.close()
    print(output)


if __name__ == "__main__":
    main()
