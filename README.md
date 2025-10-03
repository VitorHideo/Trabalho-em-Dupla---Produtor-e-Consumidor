# Trabalho-em-Dupla---Produtor-e-Consumidor

João Victor - RA:04241009
Vitor Hideo - RA:04241059

Para Subir ambiente Docker do Produtor:
1- Rodar o projeto
2- Caso não subir, executar o comando docker compose up -d
no diretorio raiz do projeto, que tem o arquvio compose.yaml

Para Testar o endpoint do Produtor:

1- Acessar o insominia, postman ou swagger
2- Utilizar a seguinte url POST: http://localhost:8080/herois
Content-Type: application/json
3- Exemplo de json para teste:
{
  "nome": "Genji",
  "idade": 35,
  "funcao": "Dano",
  "fraseUlt": "Ryūjin no ken o kurae"
}

# Instruções do Jogo (Consumer - heroi_game.py)

O consumidor recebe heróis via RabbitMQ e, ao acumular 6 heróis, inicia automaticamente uma partida 3x3. Veja como funciona:

## Regras e Funcionamento

- **Partida automática:** Assim que 6 heróis diferentes são recebidos, o jogo embaralha e divide em dois times de 3.
- **Atributos:** Cada herói tem nome, função (Tank, Dano, Suporte etc.), vida, dano, cura, idade e uma frase de ultimate.
- **Turnos:** Os times se alternam em turnos. Em cada turno, todos os heróis vivos de um time agem:
  - **Suporte/Healer:** Cura o aliado mais fraco do seu time.
  - **Outros:** Atacam o inimigo com menos vida.
  - **Ultimate:** Cada ação tem chance de ativar o ultimate, aumentando dano ou cura e exibindo a frase especial.
- **Fim de partida:** O jogo termina quando todos os heróis de um time são eliminados ou após 200 turnos (empate).
- **MVP:** O herói com maior média de impacto (dano + cura por ação) é destacado como MVP.
- **Estatísticas:** Ao final, são exibidas estatísticas detalhadas dos times e do MVP.

## Como rodar o consumidor

1. Certifique-se de que o RabbitMQ está rodando e configurado conforme as variáveis de ambiente (veja no início do `heroi_game.py`).
2. Execute o script `heroi_game.py`:
   ```powershell
   python heroi_game.py
   ```
3. Envie heróis pelo produtor (endpoint ou fila). Quando houver 6, a partida será iniciada automaticamente.

## Exemplo de saída

```
Time A: Genji, Ana, Winston
Time B: Tracer, Mercy, Reinhardt
--------------------------------

-- TURNO 1 --
Genji ataca Reinhardt 18 (x1.0)
Ana (SUPPORT) cura Winston +15 (x1.0) HP=135
Winston ataca Tracer 20 (x1.5)
...
===== FIM =====
VENCEDOR: Time A
Turnos: 12  Duracao: 0.12s

===== ESTATISTICAS =====
Time A (Vencedor):
  Genji         Role=Dano     HP=  0 Dano= 90 Cura=  0 Kills=2 Acoes=6 Ults=1 Media=15.00
  Ana           Role=Support  HP= 80 Dano=  0 Cura= 60 Kills=0 Acoes=6 Ults=2 Media=10.00
  Winston       Role=Tank     HP=  0 Dano= 60 Cura=  0 Kills=1 Acoes=6 Ults=0 Media=10.00
...
===== MVP DETALHES =====
{
  "nome": "Genji",
  "funcao": "Dano",
  "idade": 35,
  "fraseUlt": "Ryūjin no ken o kurae",
  "time": "A",
  "dano_total": 90,
  "cura_total": 0,
  "kills": 2,
  "acoes": 6,
  "ultimates": 1,
  "media_impacto": 15.0
}
<< Genji FOI O MVP >>
```
