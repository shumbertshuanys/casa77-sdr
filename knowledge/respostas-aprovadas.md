# Respostas Aprovadas

Textos que o bot pode usar. Todo valor citado vem de `knowledge/casa77.yaml` v1.1.

Status: **APROVADO** = pode usar | **AGUARDA APROVAÇÃO** = texto rascunhado, falta validação
de Douglas Bianchi | **BLOQUEADO** = campo pendente no YAML, usar R03.

---

## R01 — Saudação — AGUARDA APROVAÇÃO

<!-- fragmento: F1 -->
> Oi! Aqui é o atendimento da Casa 77, espaço para eventos no Morro do Moreno, em Vila
> Velha. Posso te passar as informações de locação. Me conta: que tipo de evento você está
> planejando?

## R02 — Identificação como bot — APROVADO

<!-- fragmento: F1 -->
> Sou o atendimento automático da Casa 77. Passo as informações iniciais, e o responsável
> comercial assume na sequência.

## R03 — Lacuna de informação — APROVADO

<!-- fragmento: F1 -->
> Essa parte eu prefiro não responder por mim para não passar informação errada. Vou
> encaminhar para o responsável comercial confirmar com você, tudo bem?

## R04 — Pedido de desconto — APROVADO

Origem: `precos.desconto_autorizado_bot: false`, `precos.desconto_a_vista: false`.

<!-- fragmento: F1 -->
> Não trabalhamos com desconto, inclusive à vista, e não consigo alterar valores por aqui.
> Condição comercial quem define é o responsável comercial — já vou encaminhar seu contato.

## R05 — Disponibilidade de data — APROVADO

Três fragmentos emitíveis. A escolha entre eles é **decisão determinística do motor**, a
partir do resultado de uma consulta autoritativa de calendário — **o LLM não decide qual
fragmento usar e nunca decide disponibilidade**. Contrato em `docs/07` §2.3, bloco
"Micro-arbitragem C-A2".

**F1 — sem confirmação segura**: ausência de fonte, falha de consulta ou resultado ambíguo.
Sempre acompanhado de handoff.

<!-- fragmento: F1 -->
> Não tenho uma confirmação segura dessa data agora. Vou registrar a data e encaminhar para
> o responsável comercial verificar com você.

**F2 — consulta autoritativa válida e data disponível.** Comunicar disponibilidade não é
reservar, segurar nem bloquear a data.

<!-- fragmento: F2 -->
> A consulta à agenda indica que essa data está disponível. Isso não é uma reserva nem
> bloqueia a data. Se quiser, encaminho para o responsável comercial dar sequência.

**F3 — consulta autoritativa válida e data indisponível.**

<!-- fragmento: F3 -->
> A consulta à agenda indica que essa data não está disponível. Se quiser, me diga outra
> data para consultar.

## R06 — Pedido de visita — APROVADO

Origem: `processo_comercial.visitas.bot_pode_confirmar: false`.

<!-- fragmento: F1 -->
> A visita é feita com o responsável comercial e leva de 30 a 40 minutos. A confirmação do
> horário também é feita pelo responsável comercial. Vou registrar seu interesse e
> encaminhar para confirmação dos detalhes.

## R07 — Fechamento de contrato — APROVADO

<!-- fragmento: F1 -->
> Contrato e assinatura são feitos direto com o responsável comercial. Já estou encaminhando
> sua conversa.

## R08 — Transferência para humano — APROVADO

<!-- fragmento: F1 -->
> Vou passar sua conversa para o responsável comercial da Casa 77, que fala com você para
> confirmar os detalhes.

## R09 — Preço — APROVADO

Origem: `precos.pacotes`. `proposta.preco_pode_ser_informado_imediatamente: true` — o bot
informa o valor sem qualificar antes.

Até 80 convidados:

<!-- fragmento: F1 -->
> A locação para até 80 convidados é R$ 15.000, com 5 horas de evento. Hora adicional
> R$ 3.000.

Até 100 convidados:

<!-- fragmento: F2 -->
> A locação para até 100 convidados é R$ 18.000, com 5 horas de evento. Hora adicional
> R$ 3.600.

Sem saber o número de convidados, apresentar os dois pacotes. Não somar, não estimar, não
compor pacote novo. O valor é o mesmo em qualquer dia da semana e em qualquer época do ano
(`diferenca_por_dia_semana: false`, `diferenca_por_temporada: false`).

## R10 — Capacidade — APROVADO

<!-- fragmento: F1 -->
> A casa recebe até 80 convidados sentados e até 100 no formato coquetel. Não há quantidade
> mínima.

## R11 — Horários — APROVADO

<!-- fragmento: F1 -->
> O evento tem 5 horas de duração e precisa terminar até as 23h. É possível contratar hora
> adicional, mas o limite das 23h vale de qualquer forma.

Montagem e desmontagem:

<!-- fragmento: F2 -->
> A montagem pode começar até 24 horas antes do evento e a desmontagem vai até um dia útil
> depois.

## R12 — O que está incluso — APROVADO

<!-- fragmento: F1 -->
> Estão inclusos: o uso das áreas contratadas, o mobiliário da casa, 3 seguranças na parte
> externa, 1 governanta, que também auxilia na recepção, e a limpeza de entrega da casa.

Não incluso:

<!-- fragmento: F2 -->
> Não entram na locação: buffet, decoração, iluminação cênica, sonorização, DJ, gerador,
> cerimonialista, bebidas, limpeza durante o evento, toldos e estacionamento.

## R13 — Endereço — APROVADO

Origem: `localizacao.pode_informar_endereco_antes_qualificacao: true`.

<!-- fragmento: F1 -->
> A Casa 77 fica na Rua Magnólia de Aguiar, 77, Morro do Moreno, Praia da Costa, Vila
> Velha/ES.

Link do Google Maps: **BLOQUEADO** (`google_maps_url: null`) → R03.

## R14 — Estacionamento — APROVADO

<!-- fragmento: F1 -->
> A casa não tem estacionamento próprio e a rua tem vagas limitadas. O ideal é orientar os
> convidados a virem de aplicativo ou táxi.

## R15 — Encerramento sem interesse — AGUARDA APROVAÇÃO

<!-- fragmento: F1 -->
> Sem problema. Se mudar de ideia, é só chamar por aqui. Obrigado pelo contato!

## R16 — Tipo de evento aceito — APROVADO

<!-- fragmento: F1 -->
> Recebemos casamento, noivado, bodas e evento corporativo. O perfil da casa é de evento
> intimista.

## R17 — Tipo de evento não aceito — APROVADO

<!-- fragmento: F1 -->
> A Casa 77 não recebe esse tipo de evento. O espaço é voltado para eventos intimistas.

Origem: `eventos.nao_aceitos` e `eventos.perfil_intimista`.

Aplica-se a: despedida de solteiro, festa de adolescente, festa infantil, aniversário
adulto (decisão de 2026-08-15, arbitragem D1), treinamento, palestra e workshop.

**Instrução interna — não emitível (FE-11a).** O **motivo específico** pelo qual um tipo de
evento não é aceito **não possui representação estrutural na base**. Enquanto essa
representação não existir e não for aprovada, **pedido específico do motivo → R03 +
handoff** — o bot não explica, não parafraseia, não resume e não infere motivo. O texto
emitível acima cobre a recusa e não depende de motivo.

## R18 — Datas bloqueadas — APROVADO

<!-- fragmento: F1 -->
> Não fazemos eventos nestas datas: Carnaval, Natal e Ano Novo.

## R19 — Pagamento — APROVADO

<!-- fragmento: F1 -->
> O pagamento pode ser integral ou em 2 parcelas: 50% na assinatura do contrato e 50% com
> vencimento 30 dias antes do evento. Não há caução.

Pedido de parcelamento diferente → R04.

## R20 — Cancelamento — APROVADO com handoff obrigatório

Origem: `cancelamento.atendimento_humano_obrigatorio: true`.

<!-- fragmento: F1 -->
> Em caso de cancelamento, o valor pago como entrada fica retido integralmente. Esse assunto
> o responsável comercial trata diretamente com você.

Sempre acompanhado de handoff.

## R21 — Alteração de data — APROVADO com handoff obrigatório

<!-- fragmento: F1 -->
> A alteração de data precisa de no mínimo 90 dias de antecedência e depende de
> disponibilidade. Quem confirma é o responsável comercial.

## R22 — Chuva / área coberta — APROVADO

<!-- fragmento: F1 -->
> Cerca de 80% do espaço é coberto, e a cerimônia e a recepção acontecem no mesmo local. A
> casa comporta a instalação de toldos, mas a contratação e a responsabilidade pelos toldos
> são do contratante.

## R23 — Restrições da casa — APROVADO

<!-- fragmento: F1 -->
> Não é permitido: drogas ilícitas, uso da piscina, uso da parte inferior da casa,
> quantidade de pessoas superior ao contratado, fogos de artifício, animais e danos ou
> intervenções na estrutura da casa. Fogos de artifício são proibidos por lei por se tratar
> de área ambiental.

Decoração:

<!-- fragmento: F2 -->
> Decoração é permitida desde que não cause dano ou alteração na estrutura da casa.

## R24 — Fornecedores — APROVADO

<!-- fragmento: F1 -->
> Você pode trazer seus próprios fornecedores. A gente costuma recomendar buffets que já
> trabalharam aqui e conhecem a estrutura da casa.

Pedir a lista de buffets recomendados → R03 + handoff (lista nominal não está no YAML).

## R25 — Cozinha e estrutura técnica — APROVADO

<!-- fragmento: F1 -->
> A cozinha é equipada com os seguintes itens, com a quantidade entre parênteses: freezer
> horizontal (1), geladeira duplex (2), cervejeira (1), fogão industrial (1), fogão
> convencional (2), forno elétrico (2), micro-ondas (1), churrasqueira (1), bancada de apoio
> (2) e área de cozinha externa (1). A rede elétrica tem 110 V e 220 V.

<!-- fragmento: F2 -->
> Som e iluminação cênica não estão inclusos e ficam por conta do contratante. Gerador
> também não está incluso, mas pode ser instalado.

## R26 — Acessibilidade — APROVADO

<!-- fragmento: F1 -->
> Sim, o espaço é acessível.

## R27 — Banheiros — APROVADO

<!-- fragmento: F1 -->
> São 4 banheiros, sendo 2 masculinos e 2 femininos.

## R28 — Suíte da noiva — PARCIAL

Aprovado:

<!-- fragmento: F1 -->
> A casa tem suíte da noiva, com sala de convivência e banheiro exclusivo. Ela não está
> inclusa no valor padrão da locação.

Valor: **BLOQUEADO** (`suite_noiva.valor: null`) → R03 + handoff.

## R29 — Validade da proposta — APROVADO

<!-- fragmento: F1 -->
> A proposta tem validade de 15 dias.

## R30 — Espaço infantil / piscina — APROVADO

<!-- fragmento: F1 -->
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
