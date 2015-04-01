#!/usr/bin/env python
# https://github.com/dpapathanasiou/pdfminer-layout-scanner
# https://github.com/LaoLiulaoliu/pdfminer-layout-scanner
# pip install -U beautifulsoup4
# pip install -e git+git@github:euske/pdfminer.git@master#egg=pdfminer

# also tried slate, content-extractor, pdftotext

import subprocess, json, os, re, unicodedata
from datetime import datetime
from urllib import urlopen
from layout_scanner import get_pages
from markdownwriter import *

output_file = open('mp_cite_refs.md', 'w+')
dry = True # dry run, no google scholar queries
scholar = './scholar.py'
titles = [
    'The Materials Project: A materials genome approach to accelerating materials innovation',
    #'A high-throughput infrastructure for density functional theory calculations',
]

md = MarkdownWriter()
timestamp = datetime.now()
md.addText('{}'.format(timestamp))
md.addDoubleLineBreak()

for idx,title in enumerate(titles):
    parent_pub = None
    test_filepath_parent = 'test_files/parent_{}.json'.format(idx)
    test_filepath_childs = 'test_files/childs_{}.json'.format(idx)
    if not dry:
        parent_pub = json.loads(subprocess.check_output([
            scholar, '-c', '1', '-p', title, '-t', '--json_form'
        ]))
        with open(test_filepath_parent, 'w') as outfile:
            json.dump(parent_pub, outfile)
    else:
        with open(test_filepath_parent, 'r') as infile:
            parent_pub = json.load(infile)
    md.addHeader(parent_pub['title'], 2)
    md.addLink(parent_pub['url'], 'URL', 'URL')
    md.addText(', {}, {} citations'.format(
        parent_pub['year'], parent_pub['num_citations']
    ))
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
    nr_child_pubs_pdfs = 0
    for child_pub in child_pubs:
        pdfurl = child_pub['url_pdf']
        if pdfurl is None or 'arxiv' not in pdfurl:
            continue # TODO: non-arxiv papers
        pdfbase = os.path.basename(pdfurl)
        images_folder = os.path.join('images', pdfbase)
        pdfpath = os.path.join('papers', pdfbase + '.pdf')
        if not os.path.exists(pdfpath):
            continue # TODO remove
            print 'downloading {}'.format(pdfpath)
            with open(pdfpath, 'wb') as output:
                output.write(urlopen(pdfurl).read())
        md.addDoubleLineBreak()
        md.addHeader(child_pub['title'], 3)
        md.addLink(child_pub['url'], 'URL', 'URL')
        md.addText(', ')
        md.addLink(child_pub['url_pdf'], 'PDF', 'PDF URL')
        md.addText(', ')
        md.addLink(images_folder, 'Images', 'Images')
        md.addText(', {}, {} citations'.format(
            child_pub['year'], child_pub['num_citations']
        ))
        md.addDoubleLineBreak()
        md.addHeader('excerpt', 4)
        md.addParagraph(unicodedata.normalize(
            "NFKC", child_pub['excerpt']
        ).encode('ascii','ignore'), 0)
        print 'parsing {}'.format(pdfpath)
        if not os.path.exists(images_folder): os.makedirs(images_folder)
        pages = get_pages(pdfpath, images_folder=images_folder)
        text = ' '.join(pages)
        print 'extracting MP paragraphs from {}'.format(pdfpath)
        md.addHeader('paragraphs', 4)
        for long_paragraph in text.split('\n\n'):
            for paragraph in long_paragraph.split('.\n'):
                paragraph = unicodedata.normalize(
                    "NFKC", paragraph.replace('-\n', '').decode('UTF-8')
                ).encode('ascii','ignore')
                if 'Materials Project' in paragraph:
                    paragraphs = []
                    for line in paragraph.split('\n'):
                        if len(line.replace(' ', '')) > 21:
                            paragraphs.append(line.replace('\n', ''))
                    md.addParagraph(' '.join(paragraphs), 1)
        nr_child_pubs_pdfs += 1
    print '#child PDFs parsed = {}'.format(nr_child_pubs_pdfs)
    output_file.write(unicodedata.normalize(
        "NFKC", md.getStream()
    ).encode('ascii','ignore'))
    output_file.close()
