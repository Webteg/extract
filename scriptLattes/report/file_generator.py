
def gerarArquivosTemporarios(group):
    print "\n[CRIANDO ARQUIVOS TEMPORARIOS: CSV, RIS, TXT, GDF]"

    gerarRISdeMembros(group)
    gerarCSVdeQualisdeGrupo(group)

    if self.obterParametro('global-salvar_informacoes_em_formato_xml'):
        self.gerarXMLdeGrupo()

    # Salvamos alguns dados para análise posterior (com outras ferramentas)
    prefix = self.obterParametro('global-prefixo') + '-' if not self.obterParametro('global-prefixo') == '' else ''

    # (1) matrizes
    salvarMatrizTXT(group.matrizDeAdjacencia, prefix + "matrizDeAdjacencia.txt")
    salvarMatrizTXT(group.matrizDeFrequencia, prefix + "matrizDeFrequencia.txt")
    salvarMatrizTXT(group.matrizDeFrequenciaNormalizada, prefix + "matrizDeFrequenciaNormalizada.txt")
    # self.salvarMatrizXML(self.matrizDeAdjacencia, prefix+"matrizDeAdjacencia.xml")

    # (2) listas de nomes, rótulos, ids
    salvarListaTXT(group.nomes, prefix + "listaDeNomes.txt")
    salvarListaTXT(group.rotulos, prefix + "labels_set.txt")
    salvarListaTXT(group.ids, prefix + "listaDeIDs.txt")

    # (3) medidas de authorRanks
    salvarListaTXT(group.vectorRank, prefix + "authorRank.txt")

    # (4) lista unica de colaboradores (orientadores, ou qualquer outro tipo de parceiros...)
    rawColaboradores = list([])
    for membro in grupo.members_list.values():
        for idColaborador in membro.listaIDLattesColaboradoresUnica:
            rawColaboradores.append(idColaborador)
    rawColaboradores = list(set(rawColaboradores))
    salvarListaTXT(rawColaboradores, prefix + "colaboradores.txt")

    # (5) Geolocalizacoes
    self.geolocalizacoes = list([])
    for membro in grupo.members_list.values():
        self.geolocalizacoes.append(str(membro.enderecoProfissionalLat) + "," + str(membro.enderecoProfissionalLon))
    salvarListaTXT(self.geolocalizacoes, prefix + "listaDeGeolocalizacoes.txt")

    # (6) arquivo GDF
    gerarArquivoGDF(prefix + "rede.gdf")


def gerarRISdeMembros(group):
    prefix = self.obterParametro('global-prefixo') + '-' if not self.obterParametro('global-prefixo') == '' else ''
    s = ""
    for membro in grupo.members_list.values():
        s += membro.ris().encode('utf8') + "\n"
    self.salvarArquivoGenerico(s, prefix + 'membros.ris')


def gerarCSVdeQualisdeGrupo(grupo):
    prefix = self.obterParametro('global-prefixo') + '-' if not self.obterParametro('global-prefixo') == '' else ''

    # Salvamos a lista individual
    s = ""
    for membro in grupo.members_list.values():
        s += self.imprimeCSVListaIndividual(membro.nomeCompleto, membro.listaArtigoEmPeriodico)
        s += self.imprimeCSVListaIndividual(membro.nomeCompleto, membro.listaTrabalhoCompletoEmCongresso)
        s += self.imprimeCSVListaIndividual(membro.nomeCompleto, membro.listaResumoExpandidoEmCongresso)
    self.salvarArquivoGenerico(s, prefix + 'publicacoesPorMembro.csv')

    # Salvamos a lista total (publicações do grupo)
    s = ""
    s += self.imprimeCSVListaGrupal(self.compilador.listaCompletaArtigoEmPeriodico)
    s += self.imprimeCSVListaGrupal(self.compilador.listaCompletaTrabalhoCompletoEmCongresso)
    s += self.imprimeCSVListaGrupal(self.compilador.listaCompletaResumoExpandidoEmCongresso)
    self.salvarArquivoGenerico(s, prefix + 'publicacoesDoGrupo.csv')


    def gerarArquivoGDF(self, nomeArquivo):
        # Vêrtices
        N = len(grupo.members_list.values())
        string = "nodedef> name VARCHAR, id_lattes VARCHAR, label VARCHAR, rotulo VARCHAR, lat DOUBLE, lon DOUBLE, collaborationRank DOUBLE, producaoBibliografica DOUBLE, artigoEmPeriodico DOUBLE, livro DOUBLE, capituloDeLivro DOUBLE, trabalhoEmCongresso DOUBLE, resumoExpandido DOUBLE, resumo DOUBLE, color VARCHAR"
        i = 0
        for membro in self.members_list.values():
            nomeCompleto = unicodedata.normalize('NFKD', membro.nomeCompleto).encode('ASCII', 'ignore')
            string += "\n" + str(
                i) + "," + membro.idLattes + "," + nomeCompleto + "," + membro.rotulo + "," + membro.enderecoProfissionalLat + "," + membro.enderecoProfissionalLon + ","
            string += str(self.vectorRank[i]) + ","
            string += str(len(membro.listaArtigoEmPeriodico) + len(membro.listaLivroPublicado) + len(
                membro.listaCapituloDeLivroPublicado) + len(membro.listaTrabalhoCompletoEmCongresso) + len(
                membro.listaResumoExpandidoEmCongresso) + len(membro.listaResumoEmCongresso)) + ","
            string += str(len(membro.listaArtigoEmPeriodico)) + ","
            string += str(len(membro.listaLivroPublicado)) + ","
            string += str(len(membro.listaCapituloDeLivroPublicado)) + ","
            string += str(len(membro.listaTrabalhoCompletoEmCongresso)) + ","
            string += str(len(membro.listaResumoExpandidoEmCongresso)) + ","
            string += str(len(membro.listaResumoEmCongresso)) + ","
            string += "'" + self.HTMLColorToRGB(membro.rotuloCorBG) + "'"
            i += 1

        # Arestas
        matriz = self.matrizDeAdjacencia

        string += "\nedgedef> node1 VARCHAR, node2 VARCHAR, weight DOUBLE"
        for i in range(0, N):
            for j in range(i + 1, N):
                if (i != j) and (matriz[i, j] > 0):
                    string += '\n' + str(i) + ',' + str(j) + ',' + str(matriz[i, j])


        # gerando o arquivo GDF
        dir = self.obterParametro('global-diretorio_de_saida')
        arquivo = open(dir + "/" + nomeArquivo, 'w')
        arquivo.write(string)  # .encode("utf8","ignore"))
        arquivo.close()


def salvarArquivoGenerico(conteudo, nomeArquivo):
    dir = self.obterParametro('global-diretorio_de_saida')
    arquivo = open(dir + "/" + nomeArquivo, 'w')
    arquivo.write(conteudo)
    arquivo.close()

def salvarListaTXT(self, lista, nomeArquivo):
    dir = self.obterParametro('global-diretorio_de_saida')
    arquivo = open(dir + "/" + nomeArquivo, 'w')

    for i in range(0, len(lista)):
        elemento = lista[i]
        if type(elemento) == type(unicode()):
            elemento = elemento.encode("utf8")
        else:
            elemento = str(elemento)
        arquivo.write(elemento + '\n')
    arquivo.close()

def salvarMatrizTXT(self, matriz, nomeArquivo):
    dir = self.obterParametro('global-diretorio_de_saida')
    arquivo = open(dir + "/" + nomeArquivo, 'w')
    N = matriz.shape[0]

    for i in range(0, N):
        for j in range(0, N):
            arquivo.write(str(matriz[i, j]) + ' ')
        arquivo.write('\n')
    arquivo.close()

def salvarMatrizXML(self, matriz, nomeArquivo):
    dir = self.obterParametro('global-diretorio_de_saida')
    arquivo = open(dir + "/" + nomeArquivo, 'w')

    s = '<?xml version="1.0" encoding="UTF-8"?> \
            \n<!--  An excerpt of an egocentric social network  --> \
            \n<graphml xmlns="http://graphml.graphdrawing.org/xmlns"> \
            \n<graph edgedefault="undirected"> \
            \n<!-- data schema --> \
            \n<key id="name" for="node" attr.name="name" attr.type="string"/> \
            \n<key id="nickname" for="node" attr.name="nickname" attr.type="string"/> \
            \n<key id="gender" for="node" attr.name="gender" attr.type="string"/> \
            \n<key id="image" for="node" attr.name="image" attr.type="string"/> \
            \n<key id="link" for="node" attr.name="link" attr.type="string"/> \
            \n<key id="amount" for="edge" attr.name="amount" attr.type="int"/> \
            \n<key id="pubs" for="node" attr.name="pubs" attr.type="int"/>'

    for i in range(0, self.numeroDeMembros()):
        membro = self.members_list.values()[i]
        s += '\n<!-- nodes --> \
                \n<node id="' + str(membro.idMembro) + '"> \
                \n<data key="name">' + membro.nomeCompleto + '</data> \
                \n<data key="nickname">' + membro.nomeEmCitacoesBibliograficas + '</data> \
                \n<data key="gender">' + membro.sexo[0].upper() + '</data> \
                \n<data key="image">' + membro.foto + '</data> \
                \n<data key="link">' + membro.url + '</data> \
                \n<data key="pubs">' + str(int(self.vetorDeCoAutoria[i])) + '</data> \
                \n</node>'

    N = matriz.shape[0]
    for i in range(0, N):
        for j in range(0, N):
            if matriz[i, j] > 0:
                s += '\n<!-- edges --> \
                        \n<edge source="' + str(i) + '" target="' + str(j) + '"> \
                        \n<data key="amount">' + str(matriz[i, j]) + '</data> \
                        \n</edge>'

    s += '\n</graph>\
            \n</graphml>'

    arquivo.write(s.encode('utf8'))
    arquivo.close()
