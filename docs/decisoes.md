# Decisões e pendências

Registro em 24 de outubro de 2026.

| Tema | Decisão / evidência |
|---|---|
| Objetivo | Projeto educativo em família; conversa em inglês e possível demonstração escolar |
| Arquitetura | Dispositivo autônomo por Wi-Fi, sem computador ligado durante o uso |
| IA | XiaoZhi e serviço em nuvem; ativação da placa personalizada e interpretação de imagem não testadas |
| Hardware | XIAO ESP32-S3 Sense; unidade inicial não encontrada, reposição pendente |
| Display | SH1106 conforme anúncio exato enviado; falta confirmar funcionamento da unidade |
| Firmware | Integração própria com revisão upstream fixada; não usar o binário AI Pin original |
| Software | Compilação/link aprovados com ESP-IDF 6.0.1; imagem de aplicação 2.493.152 bytes, partição de 3.080.192 bytes |
| Alimentação | Primeira versão por USB e fonte separada para servos; LiPo fora do circuito |
| Movimento | Pan em GPIO4, tilt em GPIO6; armar somente pelo botão físico local |
| Limites | Coordenadas lógicas -10 a +10, não graus; não há confirmação de posição por sensor |
| Mecânica | Somente o OLED na cabeça móvel; câmera e XIAO no corpo fixo |
| Atualização | Firmware pela rede bloqueado para não substituir a pinagem personalizada |
| Manual | Em 28/10, v0.1.2: 43 páginas e 28 SVGs, incluindo diagramas cumulativos de 8/17 jumpers, preparação de headers/solda, Windows em cinco etapas, diagnóstico e ficha de ensaio; Markdown e PDF gerados da mesma fonte |
| Interface da nuvem | Captura real da entrada pública, sem login. Não inventar nomes de menus autenticados; pareamento/voz/visão continuam sem prova de integração |
| Reconhecimento físico | OLED redesenhado conforme anúncio fornecido, sujeito à conferência da unidade. MAX98357 representado por nomes/funções, não por uma ordem física AITRIP ainda não confirmada |
| Publicação | Repositório público, sem pedidos, endereços, credenciais ou cópia bruta da conversa |

## Próxima evidência necessária

Confirmar a placa recebida e fotografar a protoboard e os módulos desligados, com inscrições legíveis. Usar essas evidências para conferir a orientação dos conectores reais e fechar a alimentação/mecânica dos servos. O manual ilustrado já existe, mas não é comprovação de que um iniciante concluiu a montagem nem de funcionamento físico.
