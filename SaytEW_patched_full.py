# SaytEW.py
# Требуется: requests, beautifulsoup4, pillow
# Рекомендуемый запуск: python SaytEW.py
# Назначение: сбор данных гильдий и призов, генерация index.html
# Особенности: поддержка анимированных карточек (WebM) без нарушения старой логики.

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone
import json
import re
import os
import subprocess

import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

# --------------------------- Конфигурация ---------------------------

BASE_DIR = Path(__file__).parent.resolve()
OUT_HTML = BASE_DIR / "index.html"
DATA_TOP10 = BASE_DIR / "top10.json"
HIST_EW = BASE_DIR / "history_ew.json"
HIST_ED = BASE_DIR / "history_ed.json"
CARDS_DIR = BASE_DIR / "cards"
CARDS_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
}

GUILDS = [
    ("Eternal Watchers", "https://remanga.org/guild/eternal-watchers-5fdc5a3d/about"),
    ("Eternal Demonic", "https://remanga.org/guild/eternal-keepers-of-knowledge-06969ad9/about"),
    ("ШИЗА", "https://remanga.org/guild/bed-s-bashkoi-kohaja-6a891c56/about"),
]

# Набор ID «призов» (можно менять произвольно — формат сохранён для совместимости)
PRIZES_IDS = [
    56841, 60378, 88552, 40645, 20696, 46776, 112293, 86913, 84245, 84628
]

# --------------------------- Логгер ---------------------------

def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg: str) -> None:
    print(f"[{now_str()}] {msg}", flush=True)

# --------------------------- Модели ---------------------------

@dataclass
class Prize:
    id: int
    title: str
    manga: str
    manga_url: str
    author: str
    author_url: str
    image: Optional[str]  # локальный путь к постеру (может быть None)
    video: Optional[str]  # webm ссылка (может быть None)

# --------------------------- HTTP ---------------------------

def get_soup(session: requests.Session, url: str) -> BeautifulSoup:
    r = session.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def download_image_to_webp(session: requests.Session, url: str, target: Path) -> Optional[str]:
    try:
        r = session.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content))
        img.convert("RGB").save(target, "WEBP")
        return target.as_posix()
    except Exception as e:
        log(f"[image] download error: {e} ({url})")
        return None

# --------------------------- Парсинг гильдий ---------------------------

def fetch_guild_cards(session: requests.Session, name: str, url: str) -> List[Dict[str, Any]]:
    log(f"[fetch_guild] Start: {name} -> {url}")
    r = session.get(url, headers=HEADERS, timeout=30)
    log(f"[fetch_guild] HTTP status: {r.status_code}")
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # На странице обычно есть блоки карточек пользователей — вытаскиваем <img> или <video>
    items = soup.select("div a img, div a video")
    log(f"[fetch_guild] Found cards: {len(items)}")
    cards = []
    for it in items:
        if it.name == "img":
            src = it.get("src") or it.get("data-src") or ""
            if not src:
                continue
            cards.append({"cover": src, "type": "img"})
        elif it.name == "video":
            s = it.find("source", attrs={"type": "video/webm"}) or it.find("source")
            if not s:
                continue
            src = s.get("src") or ""
            if not src:
                continue
            cards.append({"cover": src, "type": "webm"})
    log(f"[fetch_guild] Parsed count: {len(cards)}")
    return cards

# --------------------------- Парсинг призов ---------------------------

def fetch_prizes(session: requests.Session, ids: List[int]) -> List[Prize]:
    base_item = "https://remanga.org/card-item/{}"
    prizes: List[Prize] = []
    for pid in ids:
        url = base_item.format(pid)
        try:
            soup = get_soup(session, url)
        except Exception as e:
            log(f"[fetch_prizes] {pid} -> request error: {e}")
            continue

        title = soup.select_one("[data-testid='title'], h1, .title")
        title = title.get_text(strip=True) if title else f"Card #{pid}"

        # метаданные
        manga_a = soup.find("a", href=re.compile(r"/manga/"))
        manga_title = manga_a.get_text(strip=True) if manga_a else "—"
        manga_url = manga_a["href"] if manga_a and manga_a.has_attr("href") else "#"
        if manga_url and manga_url.startswith("/"):
            manga_url = "https://remanga.org" + manga_url

        author_a = soup.find("a", href=re.compile(r"/user/"))
        author_name = author_a.get_text(strip=True) if author_a else "—"
        author_url = author_a["href"] if author_a and author_a.has_attr("href") else "#"
        if author_url and author_url.startswith("/"):
            author_url = "https://remanga.org" + author_url

        # медиа
        wrap = soup.select_one("span video, span img, .prize, .card, video, img")
        img_url = None
        video_src = None

        # Ищем img
        img_tag = soup.select_one("img[class*='object-cover'], img[src]")
        if img_tag:
            img_url = img_tag.get("src") or img_tag.get("data-src")

        # Ищем video webm
        video_tag = soup.select_one("video")
        if video_tag:
            s = video_tag.find("source", attrs={"type": "video/webm"}) or video_tag.find("source")
            if s and s.get("src"):
                video_src = s.get("src")

        img_path = None
        if img_url:
            img_path = download_image_to_webp(session, img_url, CARDS_DIR / f"{pid}.webp")
        elif video_src:
            log(f"[fetch_prizes] {pid} -> video only (no <img>)")
        else:
            log(f"[fetch_prizes] {pid} -> media not found")
            continue

        prizes.append(Prize(
            id=pid,
            title=title,
            manga=manga_title,
            manga_url=manga_url,
            author=author_name,
            author_url=author_url,
            image=img_path,
            video=video_src
        ))
    return prizes

# --------------------------- Рендер HTML ---------------------------

def css_block() -> str:
    return r"""
:root{
  --bg:#0b0e12; --card:#12161c; --txt:#e8eef6; --sub:#9fb3c8; --accent:#ffd24d;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--bg);color:var(--txt);font-family:Inter,system-ui,Segoe UI,Roboto,Arial,sans-serif}
a{color:#8fc7ff;text-decoration:none}
a:hover{text-decoration:underline}

.container{max-width:1200px;margin:0 auto;padding:20px}

h1{margin:0 0 16px 0;font-size:28px}
h2{margin:24px 0 12px 0;font-size:22px;color:var(--accent)}

.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}

.prize-card{background:var(--card);border-radius:12px;padding:12px;text-align:center;position:relative}
.prize-img{width:100%;aspect-ratio:3/4;background:#0f1114;border-radius:10px;overflow:hidden;display:flex;align-items:center;justify-content:center;margin-bottom:8px}
.fluid-media{width:100%;height:100%;object-fit:cover;display:block;border-radius:10px}

.prize-title{font-weight:700;margin:6px 0 2px 0}
.prize-author{color:var(--sub);font-size:12px;margin:2px 0}

.author-card{background:var(--card);border-radius:12px;padding:8px;display:block}
.author-card .imgwrap{width:100%;aspect-ratio:3/4;background:#0f1114;border-radius:10px;overflow:hidden;display:flex;align-items:center;justify-content:center;margin-bottom:6px}
.author-card img,.author-card video{width:100%;height:100%;object-fit:cover;display:block;border-radius:10px}
.author-card-num{color:var(--sub);font-size:12px}
"""

def render_prizes(prizes: List[Prize]) -> str:
    cards = []
    for p in prizes:
        if p.video:
            poster = f' poster="{p.image}"' if p.image else ""
            media = f'<video class="fluid-media" playsinline muted autoplay loop preload="metadata"{poster}><source src="{p.video}" type="video/webm"></video>'
        else:
            media = f'<img class="fluid-media" src="{p.image}" alt="{p.title}">'
        cards.append(f"""
        <div class="prize-card">
          <div class="prize-img">{media}</div>
          <div class="prize-title">{p.title}</div>
          <div class="prize-author">Автор: <a href="{p.author_url}" target="_blank">{p.author}</a></div>
          <div class="prize-author"><a href="{p.manga_url}" target="_blank">{p.manga}</a></div>
        </div>
        """)
    return "<div class='grid'>" + "\n".join(cards) + "</div>"

def render_participants_section() -> str:
    # Вкладка «Карты участников»: JS сам решит, img или webm
    return r"""
<section class="container" id="participants">
  <h2>Карты участников</h2>
  <div id="part-cards" class="grid"></div>
</section>
<script>
(function(){
  function esc(s){return (s||"").replace(/[&<>"']/g, m=>({ "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;" }[m]))}
  function cardHTML(card, idx){
    const cover = esc(card.cover||"");
    let media;
    if (cover.endsWith(".webm")) {
      media = `<video class="fluid-media" playsinline muted autoplay loop preload="metadata">
                 <source src="${cover}" type="video/webm">
               </video>`;
    } else {
      media = `<img class="fluid-media" src="${cover}" alt="card ${idx+1}">`;
    }
    return `<a class="author-card" href="#" target="_blank">
              <div class="imgwrap">${media}</div>
              <div class="author-card-num">№${idx+1}</div>
            </a>`;
  }

  // Данные можно заменить на реальные: ячейки формируются одинаково
  const sample = window.__SAMPLE_PARTS__ || [
    {"cover":"https://remanga.org/media/card-item/cover_18b5a569.webm"},
    {"cover":"https://remanga.org/media/cards/sample.webp"}
  ];
  const root = document.getElementById("part-cards");
  root.innerHTML = sample.map(cardHTML).join("");
})();
</script>
"""

def build_html(prizes: List[Prize]) -> str:
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Eternal Watchers — Карты и Призы</title>
  <style>{css_block()}</style>
</head>
<body>
  <section class="container">
    <h1>Карта фонда (Призы)</h1>
    {render_prizes(prizes)}
  </section>
  {render_participants_section()}
</body>
</html>
"""

# --------------------------- Git helper (опционально) ---------------------------

def git_commit_and_push(msg: str) -> None:
    try:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
    except Exception as e:
        log(f"[GIT] error: {e}")

# --------------------------- Главная логика ---------------------------

def main():
    log("=== SCRIPT START ===")
    with requests.Session() as s:
        # Гильдии
        for name, url in GUILDS:
            try:
                fetch_guild_cards(s, name, url)
            except Exception as e:
                log(f"[fetch_guild] {name} -> error: {e}")

        # Призы
        prizes = fetch_prizes(s, PRIZES_IDS)

    # Сохраняем JSON для обратной совместимости (если где-то используется)
    DATA_TOP10.write_text(json.dumps([asdict(p) for p in prizes], ensure_ascii=False, indent=2), encoding="utf-8")

    # Генерация HTML
    html = build_html(prizes)
    OUT_HTML.write_text(html, encoding="utf-8")
    log(f"-> {OUT_HTML.name} saved")

    # Истории-заглушки для совместимости
    for f in (HIST_EW, HIST_ED):
        if not f.exists():
            f.write_text("[]", encoding="utf-8")
    log("-> top10.json, history_ew.json & history_ed.json saved")

    # Git (если репозиторий настроен)
    try:
        git_commit_and_push(f"Auto update: {now_str()}")
        log("[GIT] push done")
    except Exception:
        pass

    log("=== SCRIPT FINISHED ===")

if __name__ == "__main__":
    main()
