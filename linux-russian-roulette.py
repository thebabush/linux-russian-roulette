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
import shutil
import socket
import ssl
import sys
import tempfile
import time
import urllib.error
import urllib.request

SYZBOT_URL = r'https://syzkaller.appspot.com/upstream'
SYZBOT_BASE_URL = r'https://syzkaller.appspot.com/'

# SyzKaller's website gets mad otherwise
SLEEP = 0.8
TIMEOUT = 5
MAX_RETRIES = 3
RETRY_DELAY = 2


HELPER = """
#define __NR_rmdir           4
#define __NR_open            5
#define __NR_creat           8
#define __NR_link			 9
#define __NR_unlink			10
#define __NR_mknod			14
#define __NR_rename			38
#define __NR_mkdir          39
#define __NR_symlink		83
#define __NR_getdents   	141
"""


def robust_download(url, filename=None):
    """Download with timeout and retry logic"""
    # Create SSL context that ignores certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    for attempt in range(MAX_RETRIES):
        try:
            if filename:
                request = urllib.request.Request(url)
                with urllib.request.urlopen(request, timeout=TIMEOUT, context=ctx) as f:
                    with open(filename, 'wb') as out_file:
                        out_file.write(f.read())
                return None
            else:
                with urllib.request.urlopen(url, timeout=TIMEOUT, context=ctx) as f:
                    return f.read().decode('latin1')
        except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout, socket.error) as e:
            print('Download attempt {} failed: {}'.format(attempt + 1, e))
            if attempt < MAX_RETRIES - 1:
                print('Retrying in {} seconds...'.format(RETRY_DELAY))
                time.sleep(RETRY_DELAY)
            else:
                print('Max retries reached for {}'.format(url))
                raise
        except Exception as e:
            print('Unexpected error downloading {}: {}'.format(url, e))
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                raise
    return None


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
        if not text.startswith('/text') or 'ReproC' not in text:
            return

        self.links.append(text)


def roulette_compile(bug):
    print('compiling {}'.format(bug))
    # os.system('gcc -include {}/helper.h -pthread -o {}.exe {} -static'.format(temp_dir, bug, bug))
    result = os.system('gcc -pthread -o {}.exe {} -static'.format(bug, bug))
    return result == 0


def roulette_run(bug):
    print('running {}.exe'.format(bug))
    exe_name = os.path.basename(bug) + '.exe'
    
    if not os.path.exists(exe_name):
        print('Executable {} not found, skipping run'.format(exe_name))
        return
    
    run_dir = tempfile.mkdtemp(prefix='roulette_run_')
    original_dir = os.getcwd()
    
    try:
        # Copy executable to run directory
        shutil.copy2(exe_name, os.path.join(run_dir, exe_name))
        os.chdir(run_dir)
        os.system('timeout {} ./{}'.format(TIMEOUT, exe_name))
    finally:
        os.chdir(original_dir)
        shutil.rmtree(run_dir, ignore_errors=True)


def main(exe=False):
    temp_dir = tempfile.mkdtemp(prefix='roulette_')
    original_dir = os.getcwd()

    try:
        os.chdir(temp_dir)
        bug_count = 0

        with open(os.path.join(temp_dir, 'helper.h'), 'w') as helper:
            helper.write(HELPER)

        print(SYZBOT_URL)
        data = robust_download(SYZBOT_URL)
        p = TableParser()
        p.feed(data)

        random.shuffle(p.rows)
        for row in p.rows:
            bug = row[0]
            assert bug.startswith('/bug')
            url = SYZBOT_BASE_URL + bug
            print(url)
            time.sleep(SLEEP)
            data = robust_download(url)
            p = LinkParser()
            p.feed(data)

            if p.links:
                url = SYZBOT_BASE_URL + p.links[0]
                print(url)
                bug_path = os.path.join(temp_dir, '{}.c'.format(bug_count))
                bug_count += 1
                robust_download(url, bug_path)
                time.sleep(SLEEP)
                if roulette_compile(bug_path):
                    if exe:
                        roulette_run(bug_path)
                else:
                    print('Compilation failed for {}'.format(bug_path))

    finally:
        os.chdir(original_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    main(*sys.argv[1:])
