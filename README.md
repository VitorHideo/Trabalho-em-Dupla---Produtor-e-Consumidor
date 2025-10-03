# Trabalho-em-Dupla---Produtor-e-Consumidor

João Victor - RA:04241
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