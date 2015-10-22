from fetch.download_html import download_html
from persist.cache import cache

__author__ = 'kepler'


class CVLattes():
    def __init__(self, id_lattes):
        # FIXME: check if cache is being used
        cv_path = cache.directory / id_lattes if cache.directory else None

        if cv_path and 'xml' in str(cv_path):
            arquivoX = open(cv_path)
            cvLattesXML = arquivoX.read()
            arquivoX.close()

            extended_chars = u''.join(unichr(c) for c in xrange(127, 65536, 1))  # srange(r"[\0x80-\0x7FF]")
            special_chars = ' -'''
            cvLattesXML = cvLattesXML.decode('iso-8859-1', 'replace') + extended_chars + special_chars
            parser = ParserLattesXML(self.idMembro, cvLattesXML)

            self.idLattes = parser.idLattes
            self.url = parser.url
            print "(*) Utilizando CV armazenado no cache: " + cv_path

        elif '0000000000000000' == self.idLattes:
            # se o codigo for '0000000000000000' então serao considerados dados de pessoa estrangeira - sem Lattes.
            # sera procurada a coautoria endogena com os outros membro.
            # para isso é necessario indicar o nome abreviado no arquivo .list
            return

        else:
            if cv_path.exists():
                arquivoH = cv_path.open()
                cvLattesHTML = arquivoH.read()
                if self.idMembro!='':
                    print "(*) Utilizando CV armazenado no cache: {}".format(cv_path)
            else:
                cvLattesHTML = download_html(self.idLattes)
                if cache.directory:
                    file = cv_path.open(mode='w')
                    file.write(cvLattesHTML)
                    file.close()
                    print " (*) O CV está sendo armazenado no Cache"

            # extended_chars = u''.join(unichr(c) for c in xrange(127, 65536, 1))  # srange(r"[\0x80-\0x7FF]")
            # special_chars = ' -'''
            # #cvLattesHTML  = cvLattesHTML.decode('ascii','replace')+extended_chars+special_chars                                          # Wed Jul 25 16:47:39 BRT 2012
            # cvLattesHTML = cvLattesHTML.decode('iso-8859-1', 'replace') + extended_chars + special_chars
            parser = ParserLattes(self.idMembro, cvLattesHTML)

            p = re.compile('[a-zA-Z]+')
            if p.match(self.idLattes):
                self.identificador10 = self.idLattes
                self.idLattes = parser.identificador16
                self.url = 'http://lattes.cnpq.br/{}'.format(self.idLattes)
