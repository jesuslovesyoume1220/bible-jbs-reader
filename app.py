#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聖書協会共同訳リーダー
JBS Bible App の内容を表示し、参照箇所を右パネルで開く
"""

from flask import Flask, render_template, jsonify, request
import requests
import re
import json
import os

app = Flask(__name__)

CACHE = {}
_state = {'jbs_logged_in': False, 'jbs_email': ''}

JBS_SESSION = requests.Session()
JBS_SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://si.jbsbibleapp.com',
    'Referer': 'https://si.jbsbibleapp.com/',
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json',
})

BOOKS = [
    {'id': 'GEN', 'name': '創世記',           'chapters': 50},
    {'id': 'EXO', 'name': '出エジプト記',      'chapters': 40},
    {'id': 'LEV', 'name': 'レビ記',            'chapters': 27},
    {'id': 'NUM', 'name': '民数記',            'chapters': 36},
    {'id': 'DEU', 'name': '申命記',            'chapters': 34},
    {'id': 'JOS', 'name': 'ヨシュア記',        'chapters': 24},
    {'id': 'JDG', 'name': '士師記',            'chapters': 21},
    {'id': 'RUT', 'name': 'ルツ記',            'chapters': 4},
    {'id': '1SA', 'name': 'サムエル記上',      'chapters': 31},
    {'id': '2SA', 'name': 'サムエル記下',      'chapters': 24},
    {'id': '1KI', 'name': '列王記上',          'chapters': 22},
    {'id': '2KI', 'name': '列王記下',          'chapters': 25},
    {'id': '1CH', 'name': '歴代志上',          'chapters': 29},
    {'id': '2CH', 'name': '歴代志下',          'chapters': 36},
    {'id': 'EZR', 'name': 'エズラ記',          'chapters': 10},
    {'id': 'NEH', 'name': 'ネヘミヤ記',        'chapters': 13},
    {'id': 'EST', 'name': 'エステル記',        'chapters': 10},
    {'id': 'JOB', 'name': 'ヨブ記',            'chapters': 42},
    {'id': 'PSA', 'name': '詩編',              'chapters': 150},
    {'id': 'PRO', 'name': '箴言',              'chapters': 31},
    {'id': 'ECC', 'name': 'コヘレトの言葉',    'chapters': 12},
    {'id': 'SNG', 'name': '雅歌',              'chapters': 8},
    {'id': 'ISA', 'name': 'イザヤ書',          'chapters': 66},
    {'id': 'JER', 'name': 'エレミヤ書',        'chapters': 52},
    {'id': 'LAM', 'name': '哀歌',              'chapters': 5},
    {'id': 'EZK', 'name': 'エゼキエル書',      'chapters': 48},
    {'id': 'DAN', 'name': 'ダニエル書',        'chapters': 12},
    {'id': 'HOS', 'name': 'ホセア書',          'chapters': 14},
    {'id': 'JOL', 'name': 'ヨエル書',          'chapters': 3},
    {'id': 'AMO', 'name': 'アモス書',          'chapters': 9},
    {'id': 'OBA', 'name': 'オバデヤ書',        'chapters': 1},
    {'id': 'JON', 'name': 'ヨナ書',            'chapters': 4},
    {'id': 'MIC', 'name': 'ミカ書',            'chapters': 7},
    {'id': 'NAM', 'name': 'ナホム書',          'chapters': 3},
    {'id': 'HAB', 'name': 'ハバクク書',        'chapters': 3},
    {'id': 'ZEP', 'name': 'ゼファニヤ書',      'chapters': 3},
    {'id': 'HAG', 'name': 'ハガイ書',          'chapters': 2},
    {'id': 'ZEC', 'name': 'ゼカリヤ書',        'chapters': 14},
    {'id': 'MAL', 'name': 'マラキ書',          'chapters': 4},
    {'id': 'MAT', 'name': 'マタイによる福音書',         'chapters': 28},
    {'id': 'MRK', 'name': 'マルコによる福音書',         'chapters': 16},
    {'id': 'LUK', 'name': 'ルカによる福音書',           'chapters': 24},
    {'id': 'JHN', 'name': 'ヨハネによる福音書',         'chapters': 21},
    {'id': 'ACT', 'name': '使徒言行録',                 'chapters': 28},
    {'id': 'ROM', 'name': 'ローマの信徒への手紙',       'chapters': 16},
    {'id': '1CO', 'name': 'コリントの信徒への手紙一',   'chapters': 16},
    {'id': '2CO', 'name': 'コリントの信徒への手紙二',   'chapters': 13},
    {'id': 'GAL', 'name': 'ガラテヤの信徒への手紙',     'chapters': 6},
    {'id': 'EPH', 'name': 'エフェソの信徒への手紙',     'chapters': 6},
    {'id': 'PHP', 'name': 'フィリピの信徒への手紙',     'chapters': 4},
    {'id': 'COL', 'name': 'コロサイの信徒への手紙',     'chapters': 4},
    {'id': '1TH', 'name': 'テサロニケの信徒への手紙一', 'chapters': 5},
    {'id': '2TH', 'name': 'テサロニケの信徒への手紙二', 'chapters': 3},
    {'id': '1TI', 'name': 'テモテへの手紙一',           'chapters': 6},
    {'id': '2TI', 'name': 'テモテへの手紙二',           'chapters': 4},
    {'id': 'TIT', 'name': 'テトスへの手紙',             'chapters': 3},
    {'id': 'PHM', 'name': 'フィレモンへの手紙',         'chapters': 1},
    {'id': 'HEB', 'name': 'ヘブライ人への手紙',         'chapters': 13},
    {'id': 'JAS', 'name': 'ヤコブの手紙',               'chapters': 5},
    {'id': '1PE', 'name': 'ペトロの手紙一',             'chapters': 5},
    {'id': '2PE', 'name': 'ペトロの手紙二',             'chapters': 3},
    {'id': '1JN', 'name': 'ヨハネの手紙一',             'chapters': 5},
    {'id': '2JN', 'name': 'ヨハネの手紙二',             'chapters': 1},
    {'id': '3JN', 'name': 'ヨハネの手紙三',             'chapters': 1},
    {'id': 'JUD', 'name': 'ユダの手紙',                 'chapters': 1},
    {'id': 'REV', 'name': 'ヨハネの黙示録',             'chapters': 22},
]

BOOK_MAP = {b['id']: b for b in BOOKS}


def strip_html(text):
    return re.sub(r'<[^>]+>', '', text).strip()


# ── 日本語聖書参照パーサー ────────────────────────────────────
_JA_BOOK_MAP = {
    'マタイ': 'MAT', 'マタ': 'MAT',
    'マルコ': 'MRK', 'マコ': 'MRK',
    'ルカ': 'LUK',
    'ヨハネ': 'JHN', 'ヨハ': 'JHN',
    '使徒': 'ACT', '使': 'ACT',
    'ローマ': 'ROM', 'ロマ': 'ROM',
    'コリント一': '1CO', 'コリ一': '1CO', '一コリント': '1CO',
    'コリント二': '2CO', 'コリ二': '2CO', '二コリント': '2CO',
    'ガラテヤ': 'GAL', 'ガラ': 'GAL',
    'エフェソ': 'EPH', 'エフェ': 'EPH',
    'フィリピ': 'PHP', 'フィリ': 'PHP',
    'コロサイ': 'COL', 'コロ': 'COL',
    'テサロニケ一': '1TH', 'テサ一': '1TH',
    'テサロニケ二': '2TH', 'テサ二': '2TH',
    'テモテ一': '1TI', 'テモ一': '1TI',
    'テモテ二': '2TI', 'テモ二': '2TI',
    'テトス': 'TIT', 'テト': 'TIT',
    'フィレモン': 'PHM',
    'ヘブライ': 'HEB', 'ヘブ': 'HEB',
    'ヤコブ': 'JAS', 'ヤコ': 'JAS',
    'ペトロ一': '1PE', 'ペト一': '1PE',
    'ペトロ二': '2PE', 'ペト二': '2PE',
    'ヨハネ一': '1JN', 'ヨハ一': '1JN',
    'ヨハネ二': '2JN', 'ヨハ二': '2JN',
    'ヨハネ三': '3JN', 'ヨハ三': '3JN',
    'ユダ': 'JUD',
    '黙示録': 'REV', '黙示': 'REV',
    '創世記': 'GEN', '創': 'GEN',
    '出エジプト': 'EXO', '出': 'EXO',
    'レビ': 'LEV',
    '民数': 'NUM', '民': 'NUM',
    '申命': 'DEU', '申': 'DEU',
    'ヨシュア': 'JOS', 'ヨシュ': 'JOS',
    '士師': 'JDG', '士': 'JDG',
    'ルツ': 'RUT',
    'サムエル上': '1SA', 'サム上': '1SA',
    'サムエル下': '2SA', 'サム下': '2SA',
    '列王上': '1KI', '王上': '1KI',
    '列王下': '2KI', '王下': '2KI',
    '歴代上': '1CH', '代上': '1CH',
    '歴代下': '2CH', '代下': '2CH',
    'エズラ': 'EZR',
    'ネヘミヤ': 'NEH', 'ネヘ': 'NEH',
    'エステル': 'EST', 'エス': 'EST',
    'ヨブ': 'JOB',
    '詩編': 'PSA', '詩': 'PSA',
    '箴言': 'PRO', '箴': 'PRO',
    'コヘレト': 'ECC', 'コヘ': 'ECC',
    '雅歌': 'SNG', '雅': 'SNG',
    'イザヤ': 'ISA', 'イザ': 'ISA',
    'エレミヤ': 'JER', 'エレ': 'JER',
    '哀歌': 'LAM', '哀': 'LAM',
    'エゼキエル': 'EZK', 'エゼ': 'EZK',
    'ダニエル': 'DAN', 'ダニ': 'DAN',
    'ホセア': 'HOS', 'ホセ': 'HOS',
    'ヨエル': 'JOL',
    'アモス': 'AMO', 'アモ': 'AMO',
    'オバデヤ': 'OBA', 'オバ': 'OBA',
    'ヨナ': 'JON',
    'ミカ': 'MIC',
    'ナホム': 'NAM', 'ナホ': 'NAM',
    'ハバクク': 'HAB', 'ハバ': 'HAB',
    'ゼファニヤ': 'ZEP', 'ゼファ': 'ZEP',
    'ハガイ': 'HAG',
    'ゼカリヤ': 'ZEC', 'ゼカ': 'ZEC',
    'マラキ': 'MAL',
}


def _kanji_to_num(s):
    """漢数字を数値に変換: 三→3, 十二→12, 二十三→23"""
    nums = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9}
    result, cur = 0, 0
    for c in s:
        if c in nums:
            cur = nums[c]
        elif c == '十':
            result += (cur if cur else 1) * 10
            cur = 0
        elif c == '百':
            result += (cur if cur else 1) * 100
            cur = 0
    return result + cur


def parse_ja_ref(text):
    """
    'ルカ三23-38' → {'book':'LUK','chapter':3,'verse':23,'label':'ルカ三23-38'}
    None if not parseable
    """
    text = text.strip('（）() 　')
    for ja in sorted(_JA_BOOK_MAP, key=len, reverse=True):
        if text.startswith(ja):
            book = _JA_BOOK_MAP[ja]
            rest = text[len(ja):]
            km = re.match(r'^([一二三四五六七八九十百]+)', rest)
            dm = re.match(r'^(\d+)', rest)
            if km:
                chapter = _kanji_to_num(km.group(1))
                rest = rest[km.end():]
            elif dm:
                chapter = int(dm.group(1))
                rest = rest[dm.end():]
            else:
                return None
            vm = re.match(r'^[.:・]?(\d+)', rest)
            verse = int(vm.group(1)) if vm else 1
            return {'book': book, 'chapter': chapter, 'verse': verse, 'label': text}
    return None


# ── JBSログイン ───────────────────────────────────────────────
def jbs_login(email, password):
    global JBS_SESSION
    JBS_SESSION = requests.Session()
    JBS_SESSION.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://si.jbsbibleapp.com',
        'Referer': 'https://si.jbsbibleapp.com/',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
    })
    resp = JBS_SESSION.post(
        'https://api.si.jbsbibleapp.com/api/v1/auth/signin',
        json={'email': email, 'password': password},
        timeout=15
    )
    if resp.status_code == 200:
        for k in list(CACHE.keys()):
            if k.startswith('jbs_'):
                del CACHE[k]
        return True, {}
    try:
        msg = resp.json().get('message', resp.text[:200])
    except Exception:
        msg = resp.text[:200]
    return False, msg


# ── JBS章取得 ─────────────────────────────────────────────────
def jbs_fetch_chapter(book, chapter):
    key = f'jbs_{book}_{chapter}'
    if key in CACHE:
        return CACHE[key]

    # 認証切れ・接続エラー時は再ログインして1回リトライ
    url = f'https://api.si.jbsbibleapp.com/api/v1/bible/SI/{book}/{chapter - 1}'
    for attempt in range(2):
        try:
            resp = JBS_SESSION.get(url, timeout=15)
        except Exception as e:
            if attempt == 0:
                _auto_login_from_env()
                continue
            return {'error': f'接続エラー: {e}', 'items': [], 'count': 0}
        if resp.status_code in (401, 403):
            if attempt == 0:
                _auto_login_from_env()
                continue
            return {'error': 'not_logged_in', 'items': [], 'count': 0}
        if resp.status_code != 200:
            return {'error': f'HTTP {resp.status_code}', 'items': [], 'count': 0}
        break

    try:
        data = resp.json()
    except Exception:
        return {'error': 'parse_error', 'items': [], 'count': 0}

    items = []
    book_info = BOOK_MAP.get(book, {'name': book})

    if isinstance(data, dict) and 'html' in data:
        html = data['html']

        def jbs_strip(inner, keep_ruby=False):
            s = inner
            s = re.sub(r'<span[^>]*class="[^"]*\b(?:x|f)\b[^"]*"[^>]*>.*?</span>', '', s, flags=re.DOTALL)
            s = re.sub(r'<span[^>]*class="[^"]*v-number[^"]*"[^>]*>.*?</span>', '', s, flags=re.DOTALL)
            s = re.sub(r'<svg\b[^>]*>.*?</svg>', '', s, flags=re.DOTALL)
            if keep_ruby:
                # ふりがな（<ruby><rt><rp>）を残し、それ以外のタグだけ除去（元サイトと同じルビ表示）
                s = re.sub(r'<(?!/?(?:ruby|rt|rp)\b)[^>]*>', '', s)
                return re.sub(r'[ \t]+', ' ', s).strip()
            s = re.sub(r'<rt>[^<]*</rt>', '', s)
            s = re.sub(r'</?ruby[^>]*>', '', s)
            s = strip_html(s)
            return re.sub(r'\s+', ' ', s).strip()

        def clean_note_value(val):
            """引照・注の value 属性からHTML断片やエンティティを除去"""
            val = val.replace('&quote;', '"')
            val = re.sub(r'<[^>]+>', '', val)
            val = (val.replace('&amp;', '&').replace('&lt;', '<')
                      .replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'"))
            return re.sub(r'\s+', ' ', val).strip()

        HEADING_CLASSES = {'s', 's1', 's2', 's3'}

        # 引照(x)・注(f)を節番号（target属性）ごとに、HTML全体から収集
        # 例: <span class="x" target="1" value="創一1　コロ一17">1</span>
        #     <span class="f" target="3-4" value="別訳「…」">a</span>
        notes_by_target = {}
        for nm in re.finditer(
            r'<span[^>]*class="[^"]*\b(x|f)\b[^"]*"[^>]*target="([^"]*)"[^>]*value="([^"]*)"[^>]*>(.*?)</span>',
            html, re.DOTALL
        ):
            kind, tgt = nm.group(1), nm.group(2).strip()
            val = clean_note_value(nm.group(3))
            marker = strip_html(nm.group(4)).strip()
            if val:
                notes_by_target.setdefault(tgt, []).append(
                    {'kind': kind, 'no': marker, 'text': val})

        # ── 文書順に全要素（見出し・参照行・段落の開閉・節）を収集 ──
        # ※ 節アンカー <a class="v"> は <p> の外に「はみ出す」ことがあるため、
        #    <p> 単位ではなく HTML 全体から拾う（従来は <p> 外の節を取りこぼしていた）
        events = []  # (pos, order, kind, *data)

        # 見出し・参照行・段落の開閉（<p>ブロック）
        for pm in re.finditer(r'<p\b([^>]*)>(.*?)</p>', html, re.DOTALL):
            cls_m = re.search(r'class="([^"]*)"', pm.group(1))
            cls = cls_m.group(1) if cls_m else ''
            inner = pm.group(2)
            if cls in HEADING_CLASSES:
                text = jbs_strip(inner, keep_ruby=True)
                if text:
                    events.append((pm.start(), 0, 'heading', text))
            elif cls == 'r':
                raw = jbs_strip(inner).strip('（）() 　')
                events.append((pm.start(), 0, 'xref', raw))
            else:
                # 通常段落: 開き=段落境界、閉じ=段落終端（節は下の全体スキャンで拾う）
                events.append((pm.start(), 0, 'popen', None))
                events.append((pm.end(), 2, 'pclose', None))

        # 節アンカー（<p>の内外を問わずHTML全体から）
        for vm in re.finditer(
            r'<a[^>]*class="[^"]*\bv\b[^"]*"[^>]*index="([^"]+)"[^>]*>(.*?)</a>',
            html, re.DOTALL
        ):
            idx_raw = vm.group(1)
            nums = re.findall(r'\d+', idx_raw)
            if not nums:
                continue
            vnum = int(nums[0])
            label = idx_raw.strip() if len(nums) > 1 else str(vnum)
            text = jbs_strip(vm.group(2), keep_ruby=True)  # ふりがな付き
            if text:
                events.append((vm.start(), 1, 'verse', vnum, label, text,
                               notes_by_target.get(idx_raw.strip(), [])))

        events.sort(key=lambda e: (e[0], e[1]))

        # ── items を構築（段落境界で行を区切る） ──
        cur_parts = []
        cur_first = [None]

        def flush():
            if cur_parts:
                items.append({'type': 'para', 'lines': [
                    {'num': cur_first[0], 'parts': list(cur_parts)}]})
                cur_parts.clear()
                cur_first[0] = None

        for ev in events:
            kind = ev[2]
            if kind == 'heading':
                flush()
                items.append({'type': 'heading', 'text': ev[3]})
            elif kind == 'xref':
                flush()
                for ref_text in re.split(r'[、,；;]', ev[3]):
                    ref_text = ref_text.strip().strip('（）() ')
                    if not ref_text:
                        continue
                    items.append({'type': 'xref', 'text': ref_text,
                                  'ref': parse_ja_ref(ref_text)})
            elif kind in ('popen', 'pclose'):
                flush()
            elif kind == 'verse':
                vnum, label, text, notes = ev[3], ev[4], ev[5], ev[6]
                if cur_first[0] is None:
                    cur_first[0] = vnum
                cur_parts.append([label, text, notes])

        flush()

    total = sum(len(i.get('lines', [])) for i in items if i['type'] == 'para')
    result = {
        'title': f'{book_info["name"]} {chapter}章',
        'book': book,
        'chapter': chapter,
        'items': items,
        'count': total,
    }
    CACHE[key] = result
    return result


# ── Flask ルート ──────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html', books=BOOKS)


@app.route('/api/chapter')
def api_chapter():
    book = request.args.get('book', 'MAT')
    try:
        chapter = int(request.args.get('chapter', '1'))
    except ValueError:
        chapter = 1
    # 未ログインなら環境変数から自動ログインを試みる
    if not _state.get('jbs_logged_in'):
        _auto_login_from_env()
    if not _state.get('jbs_logged_in'):
        return jsonify({'error': 'not_logged_in', 'items': [], 'count': 0})
    try:
        result = jbs_fetch_chapter(book, chapter)
    except Exception as e:
        result = {'error': str(e), 'items': [], 'count': 0}
    return jsonify(result)


@app.route('/api/parse_ref')
def api_parse_ref():
    """「創一1」のような日本語聖句表記を解析して書ID・章・節を返す"""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'ok': False})
    ref = parse_ja_ref(q)
    if ref:
        return jsonify({'ok': True, **ref})
    return jsonify({'ok': False})


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    if not email or not password:
        return jsonify({'ok': False, 'message': 'メールアドレスとパスワードを入力してください'})
    ok, result = jbs_login(email, password)
    if ok:
        _state['jbs_logged_in'] = True
        _state['jbs_email'] = email
        return jsonify({'ok': True})
    else:
        _state['jbs_logged_in'] = False
        return jsonify({'ok': False, 'message': str(result)})


@app.route('/api/logout', methods=['POST'])
def api_logout():
    global JBS_SESSION
    JBS_SESSION = requests.Session()
    _state['jbs_logged_in'] = False
    for k in list(CACHE.keys()):
        if k.startswith('jbs_'):
            del CACHE[k]
    return jsonify({'ok': True})


@app.route('/api/status')
def api_status():
    return jsonify({
        'logged_in': _state.get('jbs_logged_in', False),
        'email': _state.get('jbs_email', ''),
    })


def _auto_login_from_env():
    email = os.environ.get('JBS_EMAIL', '').strip()
    password = os.environ.get('JBS_PASSWORD', '').strip()
    if email and password:
        try:
            ok, _ = jbs_login(email, password)
            if ok:
                _state['jbs_logged_in'] = True
                _state['jbs_email'] = email
                print(f'[auto-login] JBS ログイン成功: {email}')
        except Exception as e:
            print(f'[auto-login] エラー: {e}')


# 起動時ログインは別スレッドで実行（JBS APIが遅くてもサーバー起動をブロックしない）。
# 未ログイン時は各リクエストで遅延ログインするため、これが失敗・遅延しても支障はない。
import threading
threading.Thread(target=_auto_login_from_env, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5051))
    print(f'聖書協会共同訳リーダーを起動します: http://localhost:{port}')
    app.run(host='0.0.0.0', debug=False, port=port)
