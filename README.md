# CC_TP

Para executar o projecto nós disponibilizamos um virtual enviroment bastando executar o seguinte comando para dar source do mesmo, lembrando que deverá possuir a versão 3.10.8 do python:
  
  source .venv/bin/activate

Após isto para executar o servidor deverá ser executado o seguinte comando
  sudo python servermain.py [porta de atendimento] [TTL] [Ficheiro de Configuracao] [Debug(Opcional)]

caso queira que o servidor corra em modo debug no campo Debug(Opcional) basta colocar um D, caso contrario não será necessario colocar nada

Para colocar o cliente a executar deverá ser executado o seguinte comando
  sudo python clientmain.py [ip servidor:[porta de atendimento(5353 por default)]] [query_info(ex. "example.com.")] [tipo dos dados da query(ex. "MX")]
