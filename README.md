# Family AI Robot

Um robô de mesa construído em família para aprender eletrônica, programação e IA. O objetivo é conversar em inglês, ouvir pelo microfone, descrever fotografias e movimentar uma cabeça leve.

**Estado do projeto: protótipo em desenvolvimento, não um kit validado.** O firmware completo compilou com ESP-IDF 6.0.1; a montagem física e a integração com o serviço de IA ainda não foram testadas. A XIAO da compra inicial não foi localizada, e sua reposição está pendente.

## Começar

1. **Começar pelo [manual ilustrado para iniciantes, 43 páginas](guia-ilustrado-iniciantes.pdf)**: protoboard, materiais, headers, prática de solda, identificação dos módulos, ligações uma a uma, dois desenhos do conjunto completo e cinco etapas de preparação/gravação no Windows.
2. O [guia de execução de 16 páginas](guia-completo.pdf) registra a proposta técnica anterior. Para a sequência inicial e instalação no Windows, seguir o manual ilustrado atualizado.
3. Para gravar o firmware compilado, baixar o pacote na página de [releases](https://github.com/ricmmartins/family-ai-robot/releases). O ZIP contém `firmware-built/robot.bin`, o manifesto com SHA256 e os scripts.
4. Antes de energizar, revisar os pontos de controle do guia e as limitações em [VALIDACAO.txt](VALIDACAO.txt).

O manual ilustrado usa um **layout proposto de distribuição**: XIAO e módulos ficam fora da protoboard, ligados por jumpers fêmea-macho. Os furos A10–E22 devem ser conferidos na protoboard real antes do uso. Não é uma montagem testada. O desenho final dos conectores de potência dos servos ainda depende de identificar as unidades recebidas.

![Como se conectam os furos da protoboard](docs/images/breadboard-basics.svg)

[Ler o manual completo no navegador](docs/manual-ilustrado.md). Ele é gerado da mesma fonte do PDF, para não haver duas sequências divergentes. A LiPo continua fora do circuito.

**Atalhos no PDF:** p. 8, materiais e quantidade de cabos; p. 10–14, headers/solda e reconhecimento dos módulos; p. 20, OLED com os oito fios; p. 27, núcleo com os 17 jumpers; p. 29–33, Windows; p. 35, captura real da entrada da Console; p. 37, diagnóstico; p. 42, ficha de ensaio.

O mapa do amplificador identifica funções, **não a ordem física do AITRIP recebido**. A captura da nuvem foi feita sem login; as telas autenticadas de pareamento/configuração não foram verificadas. Essas lacunas e a alimentação dos servos não são resolvidas inventando posições ou menus.

## Hardware previsto

| Componente | Identificação / situação |
|---|---|
| Controlador | Seeed Studio **XIAO ESP32-S3 Sense**, com expansão de câmera e microfone; reposição pendente |
| Display | JAMHER HXR-1.3inch-1Blue, 128×64 I2C; anúncio identifica **SH1106** |
| Amplificador | Um módulo AITRIP MAX98357 I2S |
| Falante | Um Gikfun EK1794, 4 ohms / 3 W |
| Movimento | Pan-tilt Adafruit 1967, dois servos |
| Montagem | Protoboard, jumpers, headers e base não condutiva |
| Habilitação dos motores | Botão momentâneo adicional e corte físico de alimentação |
| Alimentação inicial | USB para placa/áudio e fonte regulada separada para os motores |
| LiPo EEMB 3,7 V / 1200 mAh | **Não conectar nesta versão**; circuito portátil ainda não projetado/validado |

Confirmar a versão **Sense**, e não apenas a placa ESP32-S3 sem câmera/microfone, ao comprar a reposição. O modelo exato da câmera e as características dos servos recebidos ainda precisam ser conferidos.

## Pinagem proposta

Esta tabela não substitui a identificação das inscrições nas peças nem é um desenho de encaixe na protoboard.

| Ligação | XIAO |
|---|---|
| OLED SDA / SCL | D0 / GPIO1 e D1 / GPIO2 |
| OLED VCC / GND | 3V3 e GND |
| MAX98357 BCLK / LRC / DIN | D6 / GPIO43, D4 / GPIO5 e D8 / GPIO7 |
| MAX98357 VIN / GND | 5V da XIAO com alimentação USB e GND |
| Pan / tilt | D3 / GPIO4 e **D5 / GPIO6**, não GPIO3 |
| Botão de habilitação | D7 / GPIO44 e GND |

O falante liga **entre SPK+ e SPK-**, nunca entre uma saída e GND. Os motores não recebem alimentação dos GPIOs ou do 3V3. Não unir os positivos das duas fontes.

## O que está e não está validado

**Executado:** compilação e link completos, inspeção da imagem ESP32-S3, verificação de tamanho/hash, 17 testes Python, teste C++ da política de movimento e análise sintática dos scripts PowerShell. A revisão do manual inclui verificação de limites do PDF e inspeção visual das novas figuras.

**Pendente:** gravação na placa real; alimentação, temperatura e estabilidade; display, áudio, câmera e servos; ativação da placa personalizada e visão no backend; rede e autorização da escola.

Compilar não comprova funcionamento físico. Não prometemos 100% de funcionamento, disponibilidade da nuvem ou respostas corretas da IA.

## Arquivos

| Caminho | Conteúdo |
|---|---|
| `board/` | Integração da placa personalizada e política de movimento |
| `prepare_source.py` | Baixa a revisão fixada do XiaoZhi e aplica os patches |
| `build.ps1` | Recompilação opcional com ESP-IDF 6.0.1 |
| `package_firmware.py` | Empacotamento e manifesto do firmware |
| `flash.ps1` | Gravação com conferência de identidade/hash |
| `requirements-flash.txt` | Versão fixada do esptool para o ambiente virtual local |
| `firmware-built/` | Configuração, manifesto e lockfile da compilação; o `.bin` fica na release |
| `tests/` | Testes de preparação, empacotamento e política de movimento |
| `docs/` | Estado do manual ilustrado e decisões do projeto |
| `make_guide.py`, `make_start_guide.py` | Geradores dos PDFs; exigem PyMuPDF |
| `make_illustrated_guide.py` | Gera o PDF de 43 páginas, 28 SVGs originais e o manual Markdown correspondente; exige PyMuPDF |

A [revisão técnica inicial](robo-de-mesa-revisao-tecnica.pdf) é um registro histórico anterior à compilação. Não é o guia atual de montagem.

## Desenvolvimento

Testes Python, sem dependências adicionais:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Para recompilar, usar um terminal ESP-IDF **6.0.1**:

```powershell
python .\prepare_source.py
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

O fonte upstream é fixado em `f443114fe7c3fa26b10d3630090119891cd1c4fd`. A preparação reutiliza `firmware-built/dependencies.lock`. Não vendorizamos o SDK ou o checkout inteiro do upstream. A compilação executada foi em Linux/WSL; a recompilação no Windows ainda precisa de confirmação.

## Segurança e privacidade

- Alterar ligações e soldar apenas com **todas** as fontes desconectadas.
- Deixar a LiPo intacta e desconectada; não improvisar carregamento ou conversão de tensão.
- A habilitação dos motores exige um botão local; software não substitui o corte físico de energia.
- Câmera e microfone usam um serviço externo. Revisar os termos e evitar captar pessoas ou documentos pessoais.
- Uso escolar depende de autorização e rede compatível; não contornar políticas da escola.
- Não publicar senhas de Wi-Fi, chaves, dados de conta, fotografias de crianças ou comprovantes de compra com dados pessoais.

## Licenças

O código próprio usa [MIT](LICENSE). Os padrões de integração vêm do [XiaoZhi ESP32](https://github.com/78/xiaozhi-esp32); preservar [NOTICE.txt](NOTICE.txt). O firmware também contém componentes de terceiros, sujeitos às respectivas licenças reunidas em `third_party/`.

**English summary:** A family-built ESP32-S3 Sense desktop robot with English voice interaction, on-demand camera descriptions, an SH1106 OLED and locally armed pan/tilt servos. Firmware compilation has passed; hardware and cloud integration remain untested.
