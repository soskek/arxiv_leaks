from __future__ import print_function

import argparse
import json
import os
import re
import sys
import tarfile

import lxml.html
import requests

com_pt = re.compile(r'(?<!\\)%+(.+)')
multi_com_pt = re.compile(r'\\begin{comment}(.+?)\\end{comment}')

arxiv_id_pt = re.compile(r'(?<!\d)(\d{4}\.\d{5})(?!\d)')
url_base = 'https://arxiv.org/e-print/'
url_bib_base = 'http://adsabs.harvard.edu/cgi-bin/bib_query?arXiv:'

def get_all_arxiv_ids(text):
    ids = []
    for arxiv_id in arxiv_id_pt.findall(text):
        ids.append(arxiv_id)
    return ids

def download(url, dir_path='./'):
    idx = os.path.split(url)[-1]
    file_name = idx + '.tar.gz'
    file_path = os.path.join(dir_path, file_name)
    if os.path.exists(file_path):
        return file_path

    r = requests.get(url)
    sys.stderr.write('\tdownload {}'.format(url) + '\n')
    if r.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(r.content)
        return file_path
    else:
        return 0

def read_papers(arxiv_ids, dir_path='./'):
    results = {}
    for arxiv_id in arxiv_ids:
        sys.stderr.write('[{}]'.format(arxiv_id) + '\n')
        result = read_paper(arxiv_id, dir_path)
        if result:
            if 'title' in result:
                sys.stderr.write('\t({})'.format(result['title']) + '\n')
                sys.stderr.write('\t {}'.format(' / '.join(result['authors'])) + '\n')
            results[arxiv_id] = result
    return results

def read_paper(arxiv_id, dir_path='./'):
    url = url_base + arxiv_id
    targz_path = download(url, dir_path)
    url = url_bib_base + arxiv_id
    bib_path = download(url, dir_path)

    if not targz_path:
        return []
    else:
        return read_tex_files(targz_path, bib_path)

def read_tex_files(file_path, bib_path=None):
    results = {}
    with tarfile.open(file_path, 'r') as tf:
        for ti in tf:
            if ti.name.endswith('.tex'):
                with tf.extractfile(ti) as f:
                    comments = extract_comment(f)
                    if comments:
                        results[ti.name] = comments
    if results and bib_path:
        with open(bib_path) as f:
            bib_data = extract_bibinfo(f)
        results['authors'] = bib_data['authors']
        results['title'] = bib_data['title']

    return results

def extract_bibinfo(f):
    info = {'title': '', 'authors': []}
    dom = lxml.html.fromstring(f.read())
    for c in dom.xpath('//meta'):
        name = c.attrib.get('name', '')
        if name == 'dc.title':
            info['title'] = c.attrib['content']
        elif name == 'dc.creator':
            info['authors'].append(c.attrib['content'])
    return info

def extract_comment(f):
    results = []
    for line_idx, line in enumerate(f.readlines()):
        for comment in com_pt.findall(line.decode('utf-8')):
            results.append(comment)

    for comment in multi_com_pt.findall(f.read().decode('utf-8')):
        results.append(comment)

    return results

def main():
    parser = argparse.ArgumentParser(description='Arxiv')
    parser.add_argument('--text', '-t', help='text which contains arxiv ids')
    parser.add_argument('--id', '-i', nargs='+', default=[])
    parser.add_argument('--save-dir', '-s', default='./')
    parser.add_argument('--output', '-o', default='./comments.json')

    args = parser.parse_args()
    sys.stderr.write(json.dumps(args.__dict__, indent=2) + '\n')

    ids = args.id
    if args.text:
        sys.stderr.write('load text: {}'.format(args.text) + '\n')
        ids.extend(get_all_arxiv_ids(open(args.text).read()))
    ids = list(set(ids))

    if not os.path.isdir(args.save_dir):
        os.mkdir(args.save_dir)

    sys.stderr.write('TARGET:\n' + '\n'.join('{} {}'.format(i, idx) for i, idx in enumerate(ids)) + '\n\n')
    all_results = read_papers(ids, args.save_dir)

    print(json.dumps(all_results, indent=2))
    json.dump(all_results, open(args.output, 'w'), indent=2)

if __name__ == '__main__':
    main()
