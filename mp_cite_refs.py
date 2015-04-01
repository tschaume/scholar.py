#!/usr/bin/env python
# https://github.com/dpapathanasiou/pdfminer-layout-scanner
# https://github.com/LaoLiulaoliu/pdfminer-layout-scanner
# export PYTHONPATH=../../others/pdfminer-layout-scanner:$PYTHONPATH
# pip install -U beautifulsoup4
# pip install -e git+git@github:euske/pdfminer.git@master#egg=pdfminer

# also tried slate, content-extractor, pdftotext

import subprocess, json, os, re, unicodedata
from urllib import urlopen
from layout_scanner import get_pages

scholar = './scholar.py'
titles = [
    #'A high-throughput infrastructure for density functional theory calculations',
    'The Materials Project: A materials genome approach to accelerating materials innovation',
]

for title in titles:
    print title
    #parent_pub = json.loads(subprocess.check_output([
    #    scholar, '-c', '1', '-p', title, '-t', '--json_form'
    #]))
    #print '\t#citations = {}'.format(parent_pub['num_citations'])
    #cluster_id = parent_pub['cluster_id'] #'9071217946286299275'
    #raw_cites = subprocess.check_output([
    #    scholar, '--cites', cluster_id, '--json_form'
    #])
    #child_pubs = json.loads('\n'.join([
    #    '[', raw_cites.replace('}\n{', '},\n{'), ']'
    #]))
    #print '\t#child_pubs = {}'.format(len(child_pubs))
    #child_pubs_pdf = filter(None, [
    #    child_pub['url_pdf'] for child_pub in child_pubs
    #])
    child_pubs_pdf = ['http://arxiv.org/pdf/1407.7789'] # TEST
    print '\t#child_pubs_pdf = {}'.format(len(child_pubs_pdf))
    for pdfurl in child_pubs_pdf:
        pdfpath = os.path.basename(pdfurl) + '.pdf'
        if not os.path.exists(pdfpath):
            print 'download ...'
            with open(pdfpath, 'wb') as output:
                output.write(urlopen(pdfurl).read())
        print 'parse ...'
        text = ' '.join(get_pages(pdfpath))
        print 'extract ...'
        for long_paragraph in text.split('\n\n'):
            for paragraph in long_paragraph.split('.\n'):
                paragraph = unicodedata.normalize("NFKC", unicode(paragraph.replace('-\n', '')))
                #paragraph = re.sub(r'\W+[space]', '', paragraph)
                #paragraph = re.sub('[^a-zA-Z0-9\n\.]', ' ', paragraph)
                if 'Materials Project' in paragraph:
                    print '================'
                    print repr(paragraph)
