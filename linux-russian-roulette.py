#!/usr/bin/env python3

"""
Linux Russian roulette.

by Paolo "babush" Montesel

Originally made in ~2017/2018.

WARNING1: use this only if you are losing CTFs... /s?
WARNING2: this software may break your computer, handle with care.
WARNING3: if you really really want to use this, at least wear a VM.
WARNING4: using this in a VM is still not very safe. lol.

Usage:
    ./linux-russian-roulette.py         # compile the PoCs
    ./linux-russian-roulette.py asd     # compile and **RUN** the PoCs
"""

import html.parser
import os
import random
import sys
import urllib.request

SYZBOT_URL = r'https://syzkaller.appspot.com/upstream'
SYZBOT_BASE_URL = r'https://syzkaller.appspot.com/'


class TableParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.current_row = None
        self.keep_current = None

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.current_row = []
            self.keep_current = False
            return

        attrs = dict(attrs)
        if self.current_row is not None and 'href' in attrs:
            self.current_row.append(attrs['href'])

    def handle_endtag(self, tag):
        if tag == 'tr' and self.keep_current:
            self.rows.append(self.current_row)
            self.current_row = None

    def handle_data(self, data):
        if data.strip() == 'C':
            self.keep_current = True
            return


class LinkParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return

        attrs = dict(attrs)
        if 'href' not in attrs:
            return

        text = attrs['href']
        if not text.startswith('/text') or not 'ReproC' in text:
            return

        self.links.append(text)


def roulette_compile(bug):
    print(f'compiling {bug}')
    os.system(f'gcc -pthread -o {bug}.exe {bug} -static')


def roulette_run(bug):
    print(f'running {bug}.exe')
    os.system(bug + '.exe')


def main(exe=False):

    os.makedirs('/tmp/roulette', exist_ok=True)
    bug_count = 0

    print(SYZBOT_URL)
    with urllib.request.urlopen(SYZBOT_URL) as f:
        data = f.read().decode('latin1')
        p = TableParser()
        p.feed(data)

        random.shuffle(p.rows)
        for row in p.rows:
            bug = row[0]
            assert bug.startswith('/bug')
            url = SYZBOT_BASE_URL + bug
            print(url)
            with urllib.request.urlopen(url) as f:
                data = f.read().decode('latin1')
                p = LinkParser()
                p.feed(data)

                if p.links:
                    url = SYZBOT_BASE_URL + p.links[0]
                    print(url)
                    bug_path = f'/tmp/roulette/{bug_count}.c'
                    bug_count += 1
                    urllib.request.urlretrieve(url, bug_path)
                    roulette_compile(bug_path)
                    if exe:
                        roulette_run(bug_path)


if __name__ == '__main__':
    main(*sys.argv[1:])
