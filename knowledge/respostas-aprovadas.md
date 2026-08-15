# Respostas Aprovadas

Textos que o bot pode usar. Todo valor citado vem de `knowledge/casa77.yaml` v1.1.

Status: **APROVADO** = pode usar | **AGUARDA APROVAÇÃO** = texto rascunhado, falta validação
de Douglas Bianchi | **BLOQUEADO** = campo pendente no YAML, usar R03.

---

## R01 — Saudação — AGUARDA APROVAÇÃO

> Oi! Aqui é o atendimento da Casa 77, espaço para eventos no Morro do Moreno, em Vila
> Velha. Posso te passar as informações de locação. Me conta: que tipo de evento você está
> planejando?

## R02 — Identificação como bot — APROVADO

> Sou o atendimento automático da Casa 77. Passo as informações iniciais, e o Douglas
> Bianchi assume a partir da parte comercial.

## R03 — Lacuna de informação — APROVADO

> Essa parte eu prefiro não responder por mim para não passar informação errada. Vou
> encaminhar para o Douglas confirmar com você, tudo bem?

## R04 — Pedido de desconto — APROVADO

Origem: `precos.desconto_autorizado_bot: false`, `precos.desconto_a_vista: false`.

> Não trabalhamos com desconto, inclusive à vista, e não consigo alterar valores por aqui.
> Qualquer condição comercial é o Douglas quem define. Vou passar seu contato para ele.

## R05 — Confirmação de data — APROVADO

> Ainda não consigo confirmar disponibilidade por aqui. Vou anotar a data que você quer e o
> Douglas verifica na agenda antes de te responder.

## R06 — Pedido de visita — APROVADO

Origem: `processo_comercial.visitas.bot_pode_confirmar: false`.

> A visita é feita com o próprio Douglas e leva de 30 a 40 minutos. Quem confirma o horário
> é ele. Vou registrar seu interesse e ele fala com você para combinar.

## R07 — Fechamento de contrato — APROVADO

> Contrato e assinatura são feitos direto com o Douglas. Já estou encaminhando sua conversa
> para ele.

## R08 — Transferência para humano — APROVADO

> Vou passar sua conversa para o Douglas Bianchi, que cuida das locações da Casa 77. Ele
> fala com você para confirmar os detalhes.

## R09 — Preço — APROVADO

Origem: `precos.pacotes`. `proposta.preco_pode_ser_informado_imediatamente: true` — o bot
informa o valor sem qualificar antes.

Até 80 convidados:

> A locação para até 80 convidados é R$ 15.000, com 5 horas de evento. Hora adicional
> R$ 3.000.

Até 100 convidados:

> A locação para até 100 convidados é R$ 18.000, com 5 horas de evento. Hora adicional
> R$ 3.600.

Sem saber o número de convidados, apresentar os dois pacotes. Não somar, não estimar, não
compor pacote novo. O valor é o mesmo em qualquer dia da semana e em qualquer época do ano
(`diferenca_por_dia_semana: false`, `diferenca_por_temporada: false`).

## R10 — Capacidade — APROVADO

> A casa recebe até 80 convidados sentados e até 100 no formato coquetel. Não há quantidade
> mínima.

## R11 — Horários — APROVADO

> O evento tem 5 horas de duração e precisa terminar até as 23h. É possível contratar hora
> adicional, mas o limite das 23h vale de qualquer forma.

Montagem e desmontagem:

> A montagem pode começar até 24 horas antes do evento e a desmontagem vai até um dia útil
> depois.

## R12 — O que está incluso — APROVADO

> Estão inclusos: uso das áreas contratadas, o mobiliário da casa, três seguranças na parte
> externa, uma governanta que também atua na recepção e a limpeza de entrega da casa.

Não incluso:

> Não entram na locação: buffet, decoração, iluminação cênica, sonorização, DJ, gerador,
> cerimonialista, bebidas, limpeza durante o evento, toldos e estacionamento.

## R13 — Endereço — APROVADO

Origem: `localizacao.pode_informar_endereco_antes_qualificacao: true`.

> A Casa 77 fica na Rua Magnólia de Aguiar, 77, Morro do Moreno, Praia da Costa, Vila
> Velha/ES.

Link do Google Maps: **BLOQUEADO** (`google_maps_url: null`) → R03.

## R14 — Estacionamento — APROVADO

> A casa não tem estacionamento próprio e a rua tem vagas limitadas. O ideal é orientar os
> convidados a virem de aplicativo ou táxi.

## R15 — Encerramento sem interesse — AGUARDA APROVAÇÃO

> Sem problema. Se mudar de ideia, é só chamar por aqui. Obrigado pelo contato!

## R16 — Tipo de evento aceito — APROVADO

> Recebemos casamento, noivado, bodas e evento corporativo. O perfil da casa é de evento
> intimista.

## R17 — Tipo de evento não aceito — APROVADO

> A Casa 77 não recebe esse tipo de evento. O espaço é voltado para eventos intimistas.

Origem: `eventos.nao_aceitos` e `eventos.observacao_nao_aceitos`.

Aplica-se a: despedida de solteiro, festa de adolescente, festa infantil, aniversário
adulto (decisão de 2026-08-15, arbitragem D1), treinamento, palestra e workshop.

Para treinamento, palestra e workshop o motivo registrado no YAML
(`eventos.observacao_nao_aceitos`) é estrutural — não há projetor nem assentos em
quantidade para esse uso. O texto acima cobre a recusa; se o interessado perguntar o
motivo, citar a razão registrada no YAML.

## R18 — Datas bloqueadas — APROVADO

> Não fazemos eventos no Carnaval, no Natal e no Ano Novo.

## R19 — Pagamento — APROVADO

> O pagamento pode ser integral ou em duas parcelas de 50%: a primeira na assinatura do
> contrato e a segunda 30 dias antes do evento. Não há caução.

Pedido de parcelamento diferente → R04.

## R20 — Cancelamento — APROVADO com handoff obrigatório

Origem: `cancelamento.atendimento_humano_obrigatorio: true`.

> Em caso de cancelamento, o valor da entrada, que corresponde a 50% do contrato, fica
> retido. Esse assunto o Douglas trata diretamente com você.

Sempre acompanhado de handoff.

## R21 — Alteração de data — APROVADO com handoff obrigatório

> A alteração de data precisa de no mínimo 90 dias de antecedência e depende de
> disponibilidade. Quem confirma é o Douglas.

## R22 — Chuva / área coberta — APROVADO

> Cerca de 80% do espaço é coberto, e a cerimônia e a recepção acontecem no mesmo local. A
> casa comporta a instalação de toldos, mas a contratação e a responsabilidade pelos toldos
> são do contratante.

## R23 — Restrições da casa — APROVADO

> Não é permitido: uso da piscina, uso da parte inferior da casa, fogos de artifício,
> animais, drogas ilícitas, número de pessoas acima do contratado e qualquer intervenção que
> danifique a estrutura. Os fogos são proibidos por lei porque a região é área ambiental.

Decoração:

> Decoração é permitida desde que não cause dano ou alteração na estrutura da casa.

## R24 — Fornecedores — APROVADO

> Você pode trazer seus próprios fornecedores. A gente costuma recomendar buffets que já
> trabalharam aqui e conhecem a estrutura da casa.

Pedir a lista de buffets recomendados → R03 + handoff (lista nominal não está no YAML).

## R25 — Cozinha e estrutura técnica — APROVADO

> A cozinha é equipada, com freezer, duas geladeiras, cervejeira, fogão industrial, dois
> fogões convencionais, dois fornos elétricos, micro-ondas, churrasqueira, bancadas de apoio
> e área de cozinha externa. A rede elétrica tem 110V e 220V.

> Som e iluminação cênica não estão inclusos e ficam por conta do contratante. Gerador
> também não está incluso, mas pode ser instalado.

## R26 — Acessibilidade — APROVADO

> Sim, o espaço é acessível.

## R27 — Banheiros — APROVADO

> São 4 banheiros, sendo 2 masculinos e 2 femininos.

## R28 — Suíte da noiva — PARCIAL

Aprovado:

> A casa tem suíte da noiva, com sala de convivência e banheiro exclusivo. Ela não está
> inclusa no valor padrão da locação.

Valor: **BLOQUEADO** (`suite_noiva.valor: null`) → R03 + handoff.

## R29 — Validade da proposta — APROVADO

> A proposta tem validade de 15 dias.

## R30 — Espaço infantil / piscina — APROVADO

> Não temos espaço infantil, e a piscina não é liberada para uso em eventos.

---

## Respostas bloqueadas por dado pendente

Usar sempre R03 + handoff:

- valor da suíte da noiva;
- regra para drones;
- regra para velas;
- link do Google Maps, fotos, vídeos, planta e portfólio;
- parcerias e permutas;
- reajuste anual;
- lista nominal de buffets recomendados.
