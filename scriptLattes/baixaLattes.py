#!/usr/bin/python
# encoding: utf-8

import time
import random
import re

from robobrowser.browser import RoboBrowser


# try:
# 	import mechanize
# except:
# 	print "Erro, voce precisa do Mechanize instalado no sistema, instale no Ubuntu com 'sudo apt-get install python-mechanize"
# import cookielib

VERSION = '2015-10-19T17'

REMOTE_SCRIPT = 'https://api.bitbucket.org/2.0/snippets/scriptlattes/g5Bx'

HEADERS = [('Accept-Language', 'en-us,en;q=0.5'),
           ('Accept-Encoding', 'deflate'),
           ('Keep-Alive', '115'),
           ('Connection', 'keep-alive'),
           ('Cache-Control', 'max-age=0'),
           ('Host', 'buscatextual.cnpq.br'),
           ('Origin', 'http,//buscatextual.cnpq.br'),
           ('User-Agent',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'),
           ]


def __self_update():
    raise "METHOD BEING UPGRADED"
    # import inspect
    # try:
    # 	import simplejson
    # except:
    # 	print "Erro, voce precisa do Simplejson instalado no sistema, instale no Ubuntu com 'sudo apt-get install python-simplejson'"
    # 	sys.exit(1)
    # br = mechanize.Browser()
    # r = br.open(REMOTE_SCRIPT)
    # d = simplejson.loads(r.read())
    # if d['updated_on'][:13] != VERSION:
    # 	print "BaixaLattes desatualizado, atualizando..."
    # 	r = br.open(d['files']['baixaLattes.py']['links']['self']['href'])
    # 	content = r.read()
    # 	fpath = os.path.abspath(inspect.getfile(inspect.currentframe()))
    # 	try:
    # 		handler = file(fpath, 'w')
    # 	except:
    # 		print "Erro na escrita do novo arquivo, verifique se o arquivo '%s' tem permissao de escrita" % fpath
    # 		sys.exit(1)
    # 	handler.write(content)
    # 	handler.close()
    # 	print "BaixaLattes atualizado, reinicie o programa para utilizar a nova versão, encerrando o ScriptLattes"
    # 	sys.exit(0)


def __get_data(id_lattes):
    p = re.compile('[a-zA-Z]+')
    url = 'http://lattes.cnpq.br/' + id_lattes
    if p.match(id_lattes):
        url = 'http://buscatextual.cnpq.br/buscatextual/visualizacv.do?id=' + id_lattes
    # br = mechanize.Browser()
    # br.set_cookiejar(cookielib.LWPCookieJar())
    # br.set_handle_equiv(True)
    # br.set_handle_gzip(True)
    # br.set_handle_redirect(True)
    # br.set_handle_referer(True)
    # br.set_handle_robots(False)
    # br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    # br.addheaders = HEADERS
    # r = br.open(url)
    # response = r.read()
    # if 'infpessoa' in response:
    # 	return response
    # br.select_form(nr=0)
    # br.form.set_all_readonly(False)
    # br.form['metodo'] = 'visualizarCV'
    # r = br.submit()
    # return r.read()

    br = RoboBrowser()
    br.open(url)
    form = br.get_forms()[0]
    form['metodo'] = 'visualizarCV'
    br.submit_form(form)

    return br.parsed


def baixaCVLattes(id_lattes, debug=True):
    tries = 5
    while tries > 0:
        try:
            data = __get_data(id_lattes)
            time.sleep(
                random.random() + 0.5)  # 0.5 a 1.5 segs de espera, nao altere esse tempo para não ser barrado do servidor do lattes
            if 'infpessoa' not in data:
                tries -= 1
            else:
                return data
        except Exception, e:
            if debug:
                print e
            tries -= 1
    # depois de 5 tentativas, verifiquemos se existe uma nova versao do baixaLattes
    __self_update()
    if debug:
        print '[AVISO] Nao é possível obter o CV Lattes: ', id_lattes
        print '[AVISO] Certifique-se que o CV existe.'

    raise Exception("Nao foi possivel baixar o CV Lattes em 5 tentativas")
