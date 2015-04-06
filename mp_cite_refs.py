#!/usr/bin/env python
# https://github.com/dpapathanasiou/pdfminer-layout-scanner
# https://github.com/LaoLiulaoliu/pdfminer-layout-scanner
# pip install -U beautifulsoup4
# pip install -e git+git@github:euske/pdfminer.git@master#egg=pdfminer

# also tried slate, content-extractor, pdftotext

import subprocess, json, os, re, unicodedata, sys
from datetime import datetime
from urllib import urlopen
from layout_scanner import get_pages
from markdownwriter import *
from time import sleep
from random import randint
from pybtex.database.input import bibtex as inbib
from pybtex.database.output import bibtex as outbib
from pybtex.database import BibliographyData
from pybtex import errors
from StringIO import StringIO

bibtex_test = """
@inproceedings{yushin2014phosphorus,
                 title={Phosphorus: An Alternative for High Capacity Li-Ion
                        Battery Anodes},
                 author={Yushin, Gleb},
                 booktitle={225th ECS Meeting (May 11-15, 2014)},
                 year={2014},
                 organization={Ecs}
              }


@article{liu2015spinel,
           title={Spinel compounds as multivalent battery cathodes: a systematic
                  evaluation based on ab initio calculations},
           author={Liu, Miao and Rong, Ziqin and Malik, Rahul and Canepa,
                   Pieremanuele and Jain, Anubhav and Ceder, Gerbrand and
                   Persson, Kristin A},
           journal={Energy \& Environmental Science},
           year={2015},
           publisher={Royal Society of Chemistry}
        }


@article{li2015achieving,
           title={Achieving High Specific Capacity through a Two-Electron
                  Reaction in Hypothetical Li2VFSiO4: A First-Principles
                  Investigation},
           author={Li, Yunsong and Huang, Baoling and Cheng, Xuan and Zhang,
                   Ying},
           journal={Journal of The Electrochemical Society},
           volume={162},
           number={6},
           pages={A787--A792},
           year={2015},
           publisher={The Electrochemical Society}
        }


@article{ramakrishnan2015big,
           title={Big Data meets Quantum Chemistry Approximations: The
                  $$\backslash$ Delta $-Machine Learning Approach},
           author={Ramakrishnan, Raghunathan and Dral, Pavlo O and Rupp,
                   Matthias and von Lilienfeld, O Anatole},
           journal={arXiv preprint arXiv:1503.04987},
           year={2015}
        }


@article{legrain2015aluminum,
           title={Aluminum doping improves the energetics of lithium, sodium,
                  and magnesium storage in silicon: A first-principles study},
           author={Legrain, Fleur and Manzhos, Sergei},
           journal={Journal of Power Sources},
           volume={274},
           pages={65--70},
           year={2015},
           publisher={Elsevier}
        }


@article{maceachern2015li,
           title={Li-ion battery negative electrodes based on the Fe x Zn 1- x
                  alloy system},
           author={MacEachern, L and Dunlap, RA and Obrovac, MN},
           journal={Journal of Non-Crystalline Solids},
           volume={409},
           pages={183--190},
           year={2015},
           publisher={Elsevier}
        }


@article{young2014charge,
           title={Charge Storage in Cation Incorporated $\alpha$-MnO2},
           author={Young, Matthias J and Holder, Aaron M and George, Steven M
                   and Musgrave, Charles B},
           journal={Chemistry of Materials},
           year={2014},
           publisher={ACS Publications}
        }


@article{bathia2014high,
           title={High-Mobility Bismuth-based Transparent P-Type Oxide from
                  High-throughput Material Screening},
           author={Bathia, Amit and Hautier, Geoffroy and Nilgianskul, Tan and
                   Miglio, Anna and Rignanese, Gian-Marco and Gonze, Xavier and
                   Suntivich, Jin},
           journal={arXiv preprint arXiv:1412.4429},
           year={2014}
        }


@article{varignon2014novel,
           title={Novel magneto-electric multiferroics from first-principles},
           author={Varignon, Julien and Bristowe, Nicholas C and Bousquet, Eric
                   and Ghosez, Philippe},
           journal={arXiv preprint arXiv:1410.4047},
           year={2014}
        }
"""

output_file = open('mp_cite_refs.md', 'w+')
scholar = './scholar.py'
titles = [
    'The Materials Project: A materials genome approach to accelerating materials innovation',
    'A high-throughput infrastructure for density functional theory calculations',
]
mpcenter_authors = [
    'Kristin Persson', 'Gerbrand Ceder', 'Shyue Ping Ong', 'Mark Asta',
    'Stefano Curtarolo', 'Jeffrey Snyder', 'Anthony Gamst', 'Dan Gunter', 'Jeff Neaton'
]

parser = inbib.Parser()
writer = outbib.Writer()
errors.set_strict_mode(False)
md = MarkdownWriter()
timestamp = datetime.now()
md.addText('{}'.format(timestamp))
md.addDoubleLineBreak()

for idx,title in enumerate(titles):
    parent_pub = None
    test_filepath_parent = 'test_files/parent_{}.json'.format(idx)
    test_filepath_childs = 'test_files/childs_{}.json'.format(idx)
    if not os.path.exists(test_filepath_parent):
        parent_pub = json.loads(subprocess.check_output([
            scholar, '-c', '1', '-p', title, '-t', '--json_form',
            '--cookie-file=cookie.txt'
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
    for f,form in enumerate(['--json_form', '--citation=bt']):
        if (f == 0 and not os.path.exists(test_filepath_childs)) or f == 1:
            sleep(randint(2,5))
            cmd = [ scholar, '--cites', cluster_id, form, '--cookie-file=cookie.txt' ]
            print cmd
            raw_cites = subprocess.check_output(cmd)
            print 'got raw_cites for', form
            if f == 0:
                child_pubs = json.loads('\n'.join([
                    '[', raw_cites.replace('}\n{', '},\n{'), ']'
                ]))
            else:
                bib_data = parser.parse_stream(StringIO(raw_cites))
                mpcenter = 0
                for key,entry in bib_data.entries.iteritems():
                    for person in entry.persons['author']:
                        try:
                            author = ' '.join([person.first()[0], person.last()[0]])
                        except:
                            continue
                        if author in mpcenter_authors:
                            mpcenter += 1
                            break
                    #entry_bibtex = StringIO()
                    #bd = BibliographyData(entries={key:entry})
                    #writer.write_stream(bd, entry_bibtex)
                    #entry_found = False
                    #for child_pub in child_pubs:
                    #    if child_pub['title'] == entry.fields['title']:
                    #        child_pub['bibtex'] = entry_bibtex.getvalue()
                    #        entry_found = True
                    #        break
                    #if not entry_found:
                    #    print 'not found:', entry.fields['title']
                print 'mpcenter = ', mpcenter    
        else:
            with open(test_filepath_childs, 'r') as infile:
                child_pubs = json.load(infile)
    with open(test_filepath_childs, 'w') as outfile:
        json.dump(child_pubs, outfile)
    print '#child_pubs = {}'.format(len(child_pubs))
    continue
    nr_child_pubs_pdfs = 0
    for child_pub in child_pubs:
        pdfurl = child_pub['url_pdf']
        if pdfurl is None or 'arxiv' not in pdfurl:
            continue # TODO: non-arxiv papers
        pdfbase = os.path.basename(pdfurl)
        images_folder = os.path.join('images', pdfbase)
        pdfpath = os.path.join('papers', pdfbase + '.pdf')
        if not os.path.exists(pdfpath):
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
