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

dry = True # dry run, no google scholar queries
scholar = './scholar.py'
titles = [
    'The Materials Project: A materials genome approach to accelerating materials innovation',
    #'A high-throughput infrastructure for density functional theory calculations',
]

for idx,title in enumerate(titles):
    print title
    parent_pub = None
    test_filepath_parent = 'test_files/parent_{}.json'.format(idx)
    test_filepath_childs = 'test_files/childs_{}.json'.format(idx)
    print 'test_filepath_parent = {}'.format(test_filepath_parent)
    if not dry:
        parent_pub = json.loads(subprocess.check_output([
            scholar, '-c', '1', '-p', title, '-t', '--json_form'
        ]))
        with open(test_filepath_parent, 'w') as outfile:
            json.dump(parent_pub, outfile)
    else:
        with open(test_filepath_parent, 'r') as infile:
            parent_pub = json.load(infile)
    print '#citations = {}'.format(parent_pub['num_citations'])
    cluster_id = parent_pub['cluster_id']
    print 'GS ClusterId = {}'.format(cluster_id)
    child_pubs = None
    if not dry:
        raw_cites = subprocess.check_output([
            scholar, '--cites', cluster_id, '--json_form'
        ])
        child_pubs = json.loads('\n'.join([
            '[', raw_cites.replace('}\n{', '},\n{'), ']'
        ]))
        with open(test_filepath_childs, 'w') as outfile:
            json.dump(child_pubs, outfile)
    else:
        with open(test_filepath_childs, 'r') as infile:
            child_pubs = json.load(infile)
    print '#child_pubs = {}'.format(len(child_pubs))
    child_pubs_pdf = [
        child_pub['url_pdf'] for child_pub in child_pubs
        if child_pub['url_pdf'] is not None and \
        'arxiv' in child_pub['url_pdf'] # TODO: non-arxiv papers
    ]
    print '#child_pubs_pdf on arXiv = {}'.format(len(child_pubs_pdf))
    for pdfurl in child_pubs_pdf:
        pdfbase = os.path.basename(pdfurl)
        pdfpath = os.path.join('papers', pdfbase + '.pdf')
        if not os.path.exists(pdfpath):
            print 'downloading {}'.format(pdfpath)
            with open(pdfpath, 'wb') as output:
                output.write(urlopen(pdfurl).read())
        print 'parsing {}'.format(pdfpath)
        images_folder = os.path.join('images', pdfbase)
        if not os.path.exists(images_folder): os.makedirs(images_folder)
        pages = get_pages(pdfpath, images_folder=images_folder)
        text = ' '.join(pages)
        print 'extracting MP paragraphs from {}'.format(pdfpath)
        for long_paragraph in text.split('\n\n'):
            for paragraph in long_paragraph.split('.\n'):
                paragraph = unicodedata.normalize(
                    "NFKC", paragraph.replace('-\n', '').decode('UTF-8')
                ).encode('ascii','ignore')
                if 'Materials Project' in paragraph:
                    print '================'
                    paragraphs = []
                    for line in paragraph.split('\n'):
                        if len(line.replace(' ', '')) > 21:
                            paragraphs.append(line.replace('\n', ''))
                    print ' '.join(paragraphs)
        break # TODO remove
