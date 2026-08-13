# -*- coding: utf-8 -*-
"""Builds the Elysion Tales static site from markdown sources + shared partials."""
import re
import markdown

SRC_DIR = "/home/user/workspace/elysion_tales_src"
OUT_DIR = "/home/user/workspace/elysion_tales_site"
REPO_URL = "https://github.com/fabdemnt-dev/elysion_tales"

FONT_LINKS = """  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Kaisei+Decol:wght@400;500;700&family=Zen+Maru+Gothic:wght@400;500;700&display=swap"
    rel="stylesheet"
  />"""

FAVICON = """  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cpath fill='%23dd6c8e' d='M16 4C20 4 22 8 20 12C24 10 28 12 28 16C28 20 24 22 20 20C22 24 20 28 16 28C12 28 10 24 12 20C8 22 4 20 4 16C4 12 8 10 12 12C10 8 12 4 16 4Z'/%3E%3Ccircle cx='16' cy='16' r='4.5' fill='%23fdf5f4'/%3E%3C/svg%3E" />"""

BRAND_MARK = """<svg class="brand-mark" viewBox="0 0 32 32" aria-hidden="true">
        <path d="M16 4C20 4 22 8 20 12C24 10 28 12 28 16C28 20 24 22 20 20C22 24 20 28 16 28C12 28 10 24 12 20C8 22 4 20 4 16C4 12 8 10 12 12C10 8 12 4 16 4Z" />
        <circle cx="16" cy="16" r="4.5" />
      </svg>"""

ARROW_ICON = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" /></svg>"""


def flower_icon():
    return """<svg viewBox="0 0 32 32" aria-hidden="true">
          <path d="M16 4C20 4 22 8 20 12C24 10 28 12 28 16C28 20 24 22 20 20C22 24 20 28 16 28C12 28 10 24 12 20C8 22 4 20 4 16C4 12 8 10 12 12C10 8 12 4 16 4Z" />
          <circle cx="16" cy="16" r="4.5" />
        </svg>"""


def petal(cls):
    return f"""<span class="petal {cls}" aria-hidden="true"><svg viewBox="0 0 32 32" fill="currentColor"><path d="M16 4C20 4 22 8 20 12C24 10 28 12 28 16C28 20 24 22 20 20C22 24 20 28 16 28C12 28 10 24 12 20C8 22 4 20 4 16C4 12 8 10 12 12C10 8 12 4 16 4Z"/></svg></span>"""


def head(title, description, active_root=True):
    css_path = "assets/style.css"
    js_path = "assets/script.js"
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:type" content="website" />
{FAVICON}
{FONT_LINKS}
  <link rel="stylesheet" href="{css_path}" />
</head>"""


def header():
    return f"""  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="index.html">
        {BRAND_MARK}
        <span class="brand-name">Elysion Tales</span>
      </a>
      <nav class="site-nav">
        <a href="index.html">ものがたり一覧</a>
      </nav>
      <a class="version-switch" href="https://elysion-tales.pplx.app" target="_blank" rel="noopener">❀ 別のかわいい版を見る</a>
      <button class="theme-toggle" data-theme-toggle aria-label="Switch to dark mode"></button>
    </div>
  </header>"""


def footer():
    return """  <footer class="site-footer">
    <p>Elysion Tales &middot; <a href="simple-index.html">シンプル版で読む</a></p>
  </footer>"""


STORY_META = {
    "chatgpt": {
        "label": "CHATGPT VERSION",
        "file": "chatgpt.html",
        "title": "花咲く街エリュシオン　取材日記",
        "teaser": "銀色の花びらが舞い降りた日から、街の日々を巡る取材日記。記事にはならない小さな出来事を集めた、全十話の記録。",
        "tags": ["アイリス", "ミモザ", "アネモネ", "ダフネ"],
        "nav_label": "ChatGPT版",
        "sample_key": "chatgpt_sample",
        "rewrite_key": "chatgpt_rewrite",
    },
    "claude": {
        "label": "CLAUDE VERSION",
        "file": "claude.html",
        "title": "花の名を持たない者の記録",
        "teaser": "名前を持たない記者が、そっと書き留める街の余白。透明な視点で紡がれる、静かな一日の記録。",
        "tags": ["エリカ", "ミモザ", "アイリス", "アネモネ"],
        "nav_label": "Claude版",
        "sample_key": "claude_sample",
        "rewrite_key": "claude_rewrite",
    },
    "gemini": {
        "label": "GEMINI VERSION",
        "file": "gemini.html",
        "title": "記者日記『花守りたちの余白』",
        "teaser": "通話魔法と花びらが運ぶ、やさしい記者日記。街の余白に隠れた小さな幸せを綴った、全五話の記録。",
        "tags": ["アイリス", "ダフネ", "アネモネ", "カンパニュラ"],
        "nav_label": "Gemini版",
        "sample_key": "gemini_sample",
        "rewrite_key": "gemini_rewrite",
    },
}

ORDER = ["chatgpt", "claude", "gemini"]

SAMPLE_META = {
    "claude_sample": {
        "parent": "claude",
        "src": "claude_sample",
        "file": "claude-sample.html",
        "simple_file": "simple-claude-sample.html",
        "label": "CLAUDE VERSION \u00b7 \u6bd4\u8f03\u7528\u30b5\u30f3\u30d7\u30eb",
        "title": "\u82b1\u306e\u540d\u3092\u6301\u305f\u306a\u3044\u8005\u306e\u8a18\u9332\uff08\u5192\u982d\u30b5\u30f3\u30d7\u30eb\u7248\uff09",
        "nav_label": "\u30b5\u30f3\u30d7\u30eb\u7248",
        "teaser": "3\u3064\u306eAI\u306b\u66f8\u304d\u65b9\u306e\u9055\u3044\u3092\u6bd4\u3079\u3066\u3082\u3089\u3046\u305f\u3081\u306b\u3001\u6700\u521d\u306b\u66f8\u304b\u308c\u305f\u5192\u982d\u306e\u6bd4\u8f03\u7528\u30b5\u30f3\u30d7\u30eb\u3002\u672c\u7de8\u3067\u306f8\u65e5\u9593\u306b\u5ef6\u3073\u305f\u7269\u8a9e\u3067\u3059\u304c\u3001\u3053\u3053\u3067\u306f8\u67088\u65e5\u306e\u4e00\u65e5\u3060\u3051\u3092\u53ce\u9332\u3057\u3066\u3044\u307e\u3059\u3002",
        "tags": ["\u30a8\u30ea\u30ab", "\u30df\u30e2\u30b6", "\u30a2\u30a4\u30ea\u30b9", "\u30a2\u30cd\u30e2\u30cd"],
    },
    "chatgpt_sample": {
        "parent": "chatgpt",
        "src": "chatgpt_sample",
        "file": "chatgpt-sample.html",
        "simple_file": "simple-chatgpt-sample.html",
        "label": "CHATGPT VERSION \u00b7 比較用サンプル",
        "title": "花咲く街エリュシオン　取材日記（冒頭サンプル版）",
        "nav_label": "サンプル版",
        "teaser": "3つのAIに書き方の違いを比べてもらうために、最初に書かれた冒頭の比較用サンプル。本編では十話に渡る物語ですが、ここでは最初の一日分だけを収録しています。",
        "tags": ["アイリス", "ミモザ", "アネモネ"],
    },
    "gemini_sample": {
        "parent": "gemini",
        "src": "gemini_sample",
        "file": "gemini-sample.html",
        "simple_file": "simple-gemini-sample.html",
        "label": "GEMINI VERSION \u00b7 比較用サンプル",
        "title": "記者日記『花守りたちの余白』（冒頭サンプル版）",
        "nav_label": "サンプル版",
        "teaser": "3つのAIに書き方の違いを比べてもらうために、最初に書かれた冒頭の比較用サンプル。本編では五話に渡る物語ですが、ここでは最初の二話分だけを収録しています。",
        "tags": ["アイリス", "ダフネ", "アネモネ"],
    },
}


REWRITE_META = {
    "chatgpt_rewrite": {
        "parent": "chatgpt",
        "src": "chatgpt_rewrite",
        "file": "chatgpt-rewrite.html",
        "simple_file": "simple-chatgpt-rewrite.html",
        "label": "CHATGPT VERSION \u30fb\u66f8\u304d\u76f4\u3057\u7248",
        "title": "\u82b1\u54b2\u304f\u8857\u30a8\u30ea\u30e5\u30b7\u30aa\u30f3\u3000\u53d6\u6750\u65e5\u8a18\uff08\u66f8\u304d\u76f4\u3057\u7248\uff09",
        "nav_label": "\u66f8\u304d\u76f4\u3057\u7248",
        "teaser": "\u300c\u898b\u305f\u300d\u3068\u3044\u3046\u8a00\u8449\u3092\u4fe1\u3058\u304d\u308c\u306a\u3044\u65b0\u805e\u8a18\u8005\u304c\u3001\u9280\u8272\u306e\u82b1\u3073\u3089\u306e\u566a\u3092\u8ffd\u3044\u304b\u3051\u308b\u66f8\u304d\u76f4\u3057\u7248\u3002\u540c\u3058\u5341\u8a71\u3067\u3082\u3001\u8996\u70b9\u3082\u7b46\u81f4\u3082\u307e\u308b\u3067\u9055\u3046\u300c\u3082\u3046\u3072\u3068\u3064\u306e\u30a8\u30ea\u30e5\u30b7\u30aa\u30f3\u300d\u3002",
        "tags": ["\u30a2\u30cd\u30e2\u30cd", "\u30a2\u30a4\u30ea\u30b9", "\u30cd\u30ea\u30cd", "\u30a8\u30ea\u30ab"],
    },
    "claude_rewrite": {
        "parent": "claude",
        "src": "claude_rewrite",
        "file": "claude-rewrite.html",
        "simple_file": "simple-claude-rewrite.html",
        "label": "CLAUDE VERSION \u30fb\u66f8\u304d\u76f4\u3057\u7248",
        "title": "\u3055\u3088\u306a\u3089\u306e\u6570\u3048\u65b9",
        "nav_label": "\u66f8\u304d\u76f4\u3057\u7248",
        "teaser": "\u3055\u3088\u306a\u3089\u306e\u8a00\u8449\u3092\u6570\u3048\u7d9a\u3051\u308b\u8a18\u8005\u306e\u3001\u65ad\u7247\u7684\u306a\u89b3\u5bdf\u8a18\u3002\u8857\u306e\u5c0f\u3055\u306a\u5225\u308c\u3068\u305d\u306e\u4f59\u767d\u3092\u7db4\u3063\u305f\u3001\u66f8\u304d\u76f4\u3057\u7248\u306e\u77ed\u7de8\u3002",
        "tags": ["\u30a2\u30cd\u30e2\u30cd", "\u30c0\u30d5\u30cd", "\u30ab\u30f3\u30d1\u30cb\u30e5\u30e9"],
    },
    "gemini_rewrite": {
        "parent": "gemini",
        "src": "gemini_rewrite",
        "file": "gemini-rewrite.html",
        "simple_file": "simple-gemini-rewrite.html",
        "label": "GEMINI VERSION \u30fb\u66f8\u304d\u76f4\u3057\u7248",
        "title": "\u8a18\u8005\u624b\u5e33\u300e\u82b1\u5b88\u308a\u305f\u3061\u306e\u4f59\u767d\u300f",
        "nav_label": "\u66f8\u304d\u76f4\u3057\u7248",
        "teaser": "\u53d6\u6750\u306b\u306f\u306a\u3089\u306a\u3044\u3001\u8857\u306e\u3055\u3055\u3084\u304d\u3092\u96c6\u3081\u305f\u8a18\u8005\u624b\u5e33\u3002\u901a\u8a71\u9b54\u6cd5\u3067\u7e4b\u304c\u308b\u4f4f\u6c11\u305f\u3061\u306e\u58f0\u3092\u30b9\u30b1\u30c3\u30c1\u3057\u305f\u3001\u66f8\u304d\u76f4\u3057\u7248\u306e\u756a\u5916\u7de8\u3002",
        "tags": ["\u30a2\u30a4\u30ea\u30b9", "\u30c0\u30d5\u30cd", "\u30ab\u30f3\u30d1\u30cb\u30e5\u30e9", "\u30df\u30e2\u30b6"],
    },
}

REWRITE_ORDER = ["chatgpt_rewrite", "claude_rewrite", "gemini_rewrite"]


def build_index():
    cards = []
    for key in ORDER:
        m = STORY_META[key]
        tags = "".join(f"<span>#{t}</span>" for t in m["tags"])
        cards.append(f"""    <article class="story-card" data-story="{key}">
      <div class="card-flower">{flower_icon()}</div>
      <p class="card-kicker">{m['label']}</p>
      <h2 class="card-title">{m['title']}</h2>
      <p class="card-teaser">{m['teaser']}</p>
      <div class="card-tags">{tags}</div>
      <a class="card-link" href="{m['file']}">読む {ARROW_ICON}</a>
    </article>""")

    petals = "".join(petal(f"petal--{i}") for i in range(1, 6))

    rewrite_cards = []
    for key in REWRITE_ORDER:
        rm = REWRITE_META[key]
        tags = "".join(f"<span>#{t}</span>" for t in rm["tags"])
        rewrite_cards.append(f"""    <article class="story-card" data-story="{key}">
      <div class="card-flower">{flower_icon()}</div>
      <p class="card-kicker">{rm['label']}</p>
      <h2 class="card-title">{rm['title']}</h2>
      <p class="card-teaser">{rm['teaser']}</p>
      <div class="card-tags">{tags}</div>
      <a class="card-link" href="{rm['file']}">読む {ARROW_ICON}</a>
    </article>""")

    html = f"""{head(
        "Elysion Tales | 花咲く街エリュシオンのものがたり",
        "花咲く街エリュシオンを舞台に、ChatGPT・Claude・Geminiがそれぞれ紡いだ物語の冒頭を集めたサイトです。",
    )}
<body>
{header()}

  <section class="hero">
    <div class="hero-decor">{petals}</div>
    <div class="hero-inner">
      <p class="hero-eyebrow">✿ AIが紡ぐ、花咲く街の物語</p>
      <h1 class="hero-title">Elysion Tales</h1>
      <p class="hero-sub">
        「花咲く街エリュシオン」を舞台に、ChatGPT・Claude・Geminiがそれぞれ紡いだ物語の冒頭を集めました。<br />
        同じ世界、同じ登場人物なのに、AIごとに少しずつ違う「エリュシオン」が生まれています。
      </p>
    </div>
  </section>

  <section class="story-grid" aria-label="物語一覧">
{chr(10).join(cards)}
  </section>

  <section class="rewrite-note">
    <h2>書き直し版</h2>
    <p>同じ設定を、もう一度別の角度から紡いでもらった書き直し版です。</p>
  </section>

  <section class="story-grid" aria-label="書き直し版一覧">
{chr(10).join(rewrite_cards)}
  </section>

  <section class="about-note">
    <h2>このサイトについて</h2>
    <p>「花咲く街エリュシオン」を題材に、ChatGPT・Claude・Geminiで生まれた物語を集めたページです。それぞれのAIが描く、少しずつ違うエリュシオンの世界を楽しめます。</p>
    <p class="note-caution">※このサイトは個人で楽しむために作成しています。コンテンツの転載・再配布はご遠慮ください。</p>
  </section>

{footer()}
  <script src="assets/script.js"></script>
</body>
</html>
"""
    with open(f"{OUT_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(html)


def convert_story_html(key):
    with open(f"{SRC_DIR}/{key}.md", encoding="utf-8") as f:
        text = f.read()
    body = markdown.markdown(text, extensions=["nl2br"])
    return body


def build_story_page(key):
    m = STORY_META[key]
    body = convert_story_html(key)
    others = [k for k in ORDER if k != key]
    more_cards = "\n".join(
        f"""      <a class="more-card" data-story="{o}" href="{STORY_META[o]['file']}">
        {STORY_META[o]['nav_label']}を読む {ARROW_ICON}
      </a>"""
        for o in others
    )
    sample_key = m.get("sample_key")
    if sample_key:
        sm = SAMPLE_META[sample_key]
        more_cards += f"""
      <a class="more-card" data-story="{sample_key}" href="{sm['file']}">
        {sm['nav_label']}(冒頭のみ)を読む {ARROW_ICON}
      </a>"""
    rewrite_key = m.get("rewrite_key")
    if rewrite_key:
        rm = REWRITE_META[rewrite_key]
        more_cards += f"""
      <a class="more-card" data-story="{rewrite_key}" href="{rm['file']}">
        {rm['nav_label']}を読む {ARROW_ICON}
      </a>"""
    tags_line = " ".join(f"#{t}" for t in m["tags"])

    html = f"""{head(
        f"{m['title']} | {m['label']} | Elysion Tales",
        m['teaser'],
    )}
<body>
{header()}

  <div class="story-page" data-story="{key}">
    <a class="back-link" href="index.html">&larr; ものがたり一覧に戻る</a>

    <header class="story-hero">
      <p class="story-kicker">{m['label']} <span class="dot">&middot;</span> 花咲く街エリュシオン</p>
      <h1>{m['title']}</h1>
      <p class="story-meta">{tags_line}</p>
    </header>

    <article class="story-body">
{body}
    </article>

    <nav class="story-more">
      <h2>他のバージョンも読む</h2>
      <div class="more-grid">
{more_cards}
      </div>
    </nav>
  </div>

{footer()}
  <script src="assets/script.js"></script>
</body>
</html>
"""
    with open(f"{OUT_DIR}/{m['file']}", "w", encoding="utf-8") as f:
        f.write(html)


def simple_head(title, description):
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <link rel="stylesheet" href="assets/simple.css" />
</head>"""


def simple_topline(back_href, back_label):
    return f"""    <div class="simple-topline">
      <a class="simple-brand" href="{back_href}">{back_label}</a>
      <div class="simple-topline-links">
        <a href="index.html">❀ かわいい版で見る</a>
        <a href="https://elysion-tales.pplx.app" target="_blank" rel="noopener">❀ 別のかわいい版</a>
      </div>
    </div>"""


def build_simple_index():
    items = []
    for key in ORDER:
        m = STORY_META[key]
        items.append(f"""      <li>
        <p class="simple-tag">{m['nav_label']}</p>
        <a href="simple-{key}.html">{m['title']}</a>
        <p>{m['teaser']}</p>
      </li>""")

    rewrite_items = []
    for key in REWRITE_ORDER:
        rm = REWRITE_META[key]
        rewrite_items.append(f"""      <li>
        <p class="simple-tag">{rm['label']}</p>
        <a href="{rm['simple_file']}">{rm['title']}</a>
        <p>{rm['teaser']}</p>
      </li>""")

    html = f"""{simple_head(
        "Elysion Tales (シンプル版)",
        "花咲く街エリュシオンを舞台に、ChatGPT・Claude・Geminiの物語をシンプルなレイアウトで読むページ。",
    )}
<body class="simple-page">
  <div class="simple-wrap">
{simple_topline('simple-index.html', 'Elysion Tales')}

    <h1>Elysion Tales</h1>
    <p class="simple-meta">ChatGPT・Claude・Geminiがそれぞれ紡いだ、花咲く街エリュシオンの物語の冒頭。</p>

    <ul class="simple-list">
{chr(10).join(items)}
    </ul>

    <h2>書き直し版</h2>
    <ul class="simple-list">
{chr(10).join(rewrite_items)}
    </ul>

    <p class="simple-footer">このサイトは個人で楽しむことを目的に作成しています。コンテンツの転載・再配布はご遠慮ください。</p>
  </div>
</body>
</html>
"""
    with open(f"{OUT_DIR}/simple-index.html", "w", encoding="utf-8") as f:
        f.write(html)


def build_simple_story(key):
    m = STORY_META[key]
    body = convert_story_html(key)
    others = [k for k in ORDER if k != key]
    other_links = "\n".join(
        f'      <a href="simple-{o}.html">{STORY_META[o]["nav_label"]}を読む</a>'
        for o in others
    )
    sample_key = m.get("sample_key")
    if sample_key:
        sm = SAMPLE_META[sample_key]
        other_links += f'\n      <a href="{sm["simple_file"]}">{sm["nav_label"]}(冒頭のみ)を読む</a>'
    rewrite_key = m.get("rewrite_key")
    if rewrite_key:
        rm = REWRITE_META[rewrite_key]
        other_links += f'\n      <a href="{rm["simple_file"]}">{rm["nav_label"]}を読む</a>'
    tags_line = " ".join(f"#{t}" for t in m["tags"])

    html = f"""{simple_head(
        f"{m['title']} (シンプル版) | Elysion Tales",
        m['teaser'],
    )}
<body class="simple-page">
  <div class="simple-wrap">
{simple_topline('simple-index.html', '← 一覧に戻る')}

    <h1>{m['title']}</h1>
    <p class="simple-meta"><strong>{m['nav_label']}</strong> &middot; {tags_line}</p>

    <div class="simple-body">
{body}
    </div>

    <div class="simple-nav-links">
{other_links}
      <a href="{m['file']}">❀ この物語をかわいい版で見る</a>
    </div>

    <p class="simple-footer">Elysion Tales &middot; <a href="simple-index.html">シンプル版一覧</a></p>
  </div>
</body>
</html>
"""
    with open(f"{OUT_DIR}/simple-{key}.html", "w", encoding="utf-8") as f:
        f.write(html)


def build_sample_page(key):
    sm = SAMPLE_META[key]
    parent = STORY_META[sm["parent"]]
    body = convert_story_html(sm["src"])
    tags_line = " ".join(f"#{t}" for t in sm["tags"])

    html = f"""{head(
        f"{sm['title']} | {sm['label']} | Elysion Tales",
        sm['teaser'],
    )}
<body>
{header()}

  <div class="story-page" data-story="{key}">
    <a class="back-link" href="index.html">&larr; ものがたり一覧に戻る</a>

    <header class="story-hero">
      <p class="story-kicker">{sm['label']} <span class="dot">&middot;</span> 花咲く街エリュシオン</p>
      <h1>{sm['title']}</h1>
      <p class="story-meta">{tags_line}</p>
      <p class="story-note">{sm['teaser']}</p>
    </header>

    <article class="story-body">
{body}
    </article>

    <nav class="story-more">
      <h2>本編を読む</h2>
      <div class="more-grid">
        <a class="more-card" data-story="{sm['parent']}" href="{parent['file']}">
          {parent['nav_label']}（全文）を読む {ARROW_ICON}
        </a>
      </div>
    </nav>
  </div>

{footer()}
  <script src="assets/script.js"></script>
</body>
</html>
"""
    with open(f"{OUT_DIR}/{sm['file']}", "w", encoding="utf-8") as f:
        f.write(html)


def build_rewrite_page(key):
    rm = REWRITE_META[key]
    parent = STORY_META[rm["parent"]]
    body = convert_story_html(rm["src"])
    tags_line = " ".join(f"#{t}" for t in rm["tags"])
    others = [k for k in REWRITE_ORDER if k != key]
    more_cards = "\n".join(
        f"""      <a class="more-card" data-story="{o}" href="{REWRITE_META[o]['file']}">
        {REWRITE_META[o]['label']}を読む {ARROW_ICON}
      </a>"""
        for o in others
    )

    html = f"""{head(
        f"{rm['title']} | {rm['label']} | Elysion Tales",
        rm['teaser'],
    )}
<body>
{header()}

  <div class="story-page" data-story="{key}">
    <a class="back-link" href="index.html">&larr; ものがたり一覧に戻る</a>

    <header class="story-hero">
      <p class="story-kicker">{rm['label']} <span class="dot">&middot;</span> 花咲く街エリュシオン</p>
      <h1>{rm['title']}</h1>
      <p class="story-meta">{tags_line}</p>
      <p class="story-note">{rm['teaser']}</p>
    </header>

    <article class="story-body">
{body}
    </article>

    <nav class="story-more">
      <h2>他のバージョンも読む</h2>
      <div class="more-grid">
{more_cards}
      <a class="more-card" data-story="{rm['parent']}" href="{parent['file']}">
        {parent['nav_label']}（本編）を読む {ARROW_ICON}
      </a>
      </div>
    </nav>
  </div>

{footer()}
  <script src="assets/script.js"></script>
</body>
</html>
"""
    with open(f"{OUT_DIR}/{rm['file']}", "w", encoding="utf-8") as f:
        f.write(html)


def build_simple_rewrite_page(key):
    rm = REWRITE_META[key]
    parent = STORY_META[rm["parent"]]
    body = convert_story_html(rm["src"])
    tags_line = " ".join(f"#{t}" for t in rm["tags"])
    others = [k for k in REWRITE_ORDER if k != key]
    other_links = "\n".join(
        f'      <a href="{REWRITE_META[o]["simple_file"]}">{REWRITE_META[o]["label"]}を読む</a>'
        for o in others
    )

    html = f"""{simple_head(
        f"{rm['title']} (シンプル版) | Elysion Tales",
        rm['teaser'],
    )}
<body class="simple-page">
  <div class="simple-wrap">
{simple_topline('simple-index.html', '← 一覧に戻る')}

    <h1>{rm['title']}</h1>
    <p class="simple-meta"><strong>{rm['label']}</strong> &middot; {tags_line}</p>
    <p class="simple-meta">{rm['teaser']}</p>

    <div class="simple-body">
{body}
    </div>

    <div class="simple-nav-links">
{other_links}
      <a href="simple-{rm['parent']}.html">{parent['nav_label']}（本編）を読む</a>
      <a href="{rm['file']}">❀ この書き直し版をかわいい版で見る</a>
    </div>

    <p class="simple-footer">Elysion Tales &middot; <a href="simple-index.html">シンプル版一覧</a></p>
  </div>
</body>
</html>
"""
    with open(f"{OUT_DIR}/{rm['simple_file']}", "w", encoding="utf-8") as f:
        f.write(html)


def build_simple_sample_page(key):
    sm = SAMPLE_META[key]
    parent = STORY_META[sm["parent"]]
    body = convert_story_html(sm["src"])
    tags_line = " ".join(f"#{t}" for t in sm["tags"])

    html = f"""{simple_head(
        f"{sm['title']} (シンプル版) | Elysion Tales",
        sm['teaser'],
    )}
<body class="simple-page">
  <div class="simple-wrap">
{simple_topline('simple-index.html', '← 一覧に戻る')}

    <h1>{sm['title']}</h1>
    <p class="simple-meta"><strong>{sm['nav_label']}</strong> &middot; {tags_line}</p>
    <p class="simple-meta">{sm['teaser']}</p>

    <div class="simple-body">
{body}
    </div>

    <div class="simple-nav-links">
      <a href="simple-{sm['parent']}.html">{parent['nav_label']}（全文）を読む</a>
      <a href="{sm['file']}">❀ このサンプルをかわいい版で見る</a>
    </div>

    <p class="simple-footer">Elysion Tales &middot; <a href="simple-index.html">シンプル版一覧</a></p>
  </div>
</body>
</html>
"""
    with open(f"{OUT_DIR}/{sm['simple_file']}", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    build_index()
    build_simple_index()
    for key in ORDER:
        build_story_page(key)
        build_simple_story(key)
    for key in SAMPLE_META:
        build_sample_page(key)
        build_simple_sample_page(key)
    for key in REWRITE_ORDER:
        build_rewrite_page(key)
        build_simple_rewrite_page(key)
    print("build complete")
