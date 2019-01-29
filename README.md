# scriptLattes V8.12

## SINOPSE

`scriptLattes.py <nome_arquivo_de_configuracao>`


## REQUISITOS

Use a versão 2.7 do python. Por exemplo, assumindo que o executável do python 2.7 seja `python2.7` e que esteja usando o `virtualenv`:
```
$ cd <diretório-do-projeto>
$ virtualenv -p python2.7 venv
$ source venv/bin/activate
```	

Depois proceda com a instalação dos requisitos.
```
$ pip install -r requirements.txt
```	

## EXECUÇÃO

Teste o scriptLattes com os seguintes dois exemplos (linha de comandos):

### EXEMPLO 01:

```
$ cd <nome_diretorio_scriptLattes>
$ python scriptLattes.py ./exemplo/teste-01.config
```

Nesse exemplo consideram-se todas as produções cujos anos de publicações estão entre 2006 e 2014. Nenhum rótulo foi considerado para os membros. 
	
Os IDs Lattes dos 3 membros está listada em: `./exemplo/teste-01.list`

O resultado da execução estará disponível em: `./exemplo/teste-01/`

### EXEMPLO 02

```
$ cd <nome_diretorio_scriptLattes>
$ python scriptLattes.py ./exemplo/teste-02.config
```

Nesse exemplo consideram-se todas as produções cadastradas nos CVs Lattes. São considerados rótulos para os membros do grupo (professor, colaborador, aluno).

Adicionalmente também são apresentadas as informações de Qualis para os artigos publicados (congressos e journals).

Os IDs Lattes dos membros está listada em: `./exemplo/teste-02.list`

O resultado da execução estará disponível em: `./exemplo/teste-02/`


## IDEALIZADORES DO PROJETO

* Jesús P. Mena-Chalco <jesus.mena@ufabc.edu.br>
* Roberto M. Cesar-Jr <cesar@vision.ime.usp.br>

## URL DO PROJETO

http://bitbucket.org/scriptlattes
