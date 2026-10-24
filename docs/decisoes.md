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
| Manual | Precisa ser refeito para iniciantes, com peças reais e uma ligação por imagem |
| Publicação | Repositório público, sem pedidos, endereços, credenciais ou cópia bruta da conversa |

## Próxima evidência necessária

Receber a nova placa e fotografar a protoboard e os módulos desligados, com inscrições legíveis. Depois, definir o layout físico e escrever o manual ilustrado. A montagem só será declarada funcional após os testes reais.
