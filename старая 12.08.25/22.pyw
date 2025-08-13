# 22.py
# Требуется: requests, beautifulsoup4
# Рекомендуемый запуск без консоли: pythonw.exe 22.py
# Логи: log.txt (append)

from pathlib import Path
import re
import unicodedata
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import subprocess
import os
import sys

# ----------------- ЛОГ -----------------
LOG_PATH = Path(__file__).parent / "log.txt"

def log(*args):
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    msg = " ".join(str(a) for a in args)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{ts} {msg}\n")
    except Exception:
        # на всякий случай — печать если лог не доступен
        try:
            print(ts, msg)
        except:
            pass

# ----------------- НАСТРОЙКИ -----------------
GUILD1_URL = 'https://remanga.org/guild/eternal-watchers-5fdc5a3d/about'
GUILD2_URL = 'https://remanga.org/guild/eternal-keepers-of-knowledge-06969ad9/about'
BASE_URL = 'https://remanga.org'
AVATAR_PLACEHOLDER = "avatars/placeholder.jpg"
AVATARS_DIR = Path("avatars")
AVATARS_DIR.mkdir(exist_ok=True)

# ----------------- MANUAL: гильдия 1 -----------------
guild1_manual_pairs = [
    ("CalistoTzy",114000),("МилыйКохай",109320),("Casepona",157780),("Zurichka",36000),("Яштуг",119860),
    ("Belashik",104070),("Werty-Servyt",123340),("MARKUTTs",44500),("AkiraGame",47500),("EW_NoBoN",53000),
    ("healot",16500),("_festashka_",56250),("rezord_aye",20070),("Chitandael",29380),("Okiarya",40400),
    ("Tavik",48770),("Satisfied",38170),("MeeQ_Q",39750),("Thostriel",37810),("Overcooling",35500),
    ("ADMIRAL_SENGOKU",28000),("Arbogastr",31500),("KodokunaYurei",54990),("HARLEQU1N",21790),("Andre_Falkonen",32890),
    ("Bagas",22360),("Йорм",13160),("EW_Taya_",36440),("Clf",24190),("Кайден",37610),("𝕹𝖎𝖐𝖎𝖙𝖆⁹",44630),
    ("Loly2810",14650),("Xmmxmm",10000),("гдемойстояк",10000),("Frostik4",25700),("desport",24730),
    ("Merrihew",27430),("Misikira",16300),("CreamWhite",21000),("тот_кто_смотрит....",17540),("Payk_",25000),
    ("ミュージシャン",105000),("Р03А",23260),("Dark_AngeI",10080),("Bloodborrn",13540),("vladosrat",44060),
    ("MonaLize",27900),("Abigor.",13920),("Госька",26040),("PupsTv",11200),("Gree.in",10010),
    ("Капитан-зануда",12000),("TeᴍƤeຮt",10000),("Feel_what_life_is",26710),("mangalev",11760),("Chiru-san",10050),
    ("Efiliyens",13310),("spidvrassrochku",10860),("Cкрытый_интриган",12750),("osmodeuss",10050),("Talent",7510),
    ("SalliKrash",32500),("__ASURA__",10090),("Jedı",16550),("Sunshi",7660),("FrozenJFX",22610),
    ("Я_лучший_в_мире",18080),("RayZe",11430),("К4йдэн",10220),("Harutsu",31280),("No_warries",14270),
    ("TeChal",10180),("Hellsait",9780),("ToKKeBi11",8940),("Чмошка-Мошка",10880),("NikesNt",10040),
    ("zarti",10080),("loli69228",26090),("Laytee",10030),("Старейшина-Чу",16550),("_Abyss_",12550),
    ("역사관",16480),("DarQee",1000),("Volcopik",82050),("Charisma",4000),("EW_МанкиДиГлупый",40000),
    ("WhitеFlower",31000),("Wladzer",10380)
]

# ----------------- MANUAL: гильдия 2 -----------------
guild2_manual_pairs = [
    ("URUS",8000),("Pepegaronni",10638),("allentina",19500),("@𝑻𝑶𝑿𝑰𝑪",11880),
    ("Ronin74",36010),("Ham021",22000),("mmarti",8000),("FlammeNoire",21640),("Kaizaki",11394),
    ("Dergauss",10000),("Trololo_Mio",8410),("Beast_",37930),("DestructionGod𒉭",40000),("Zatex",10004),
    ("Trillo",7210),("RiverFreedom",9000),(".谢怜.",9000),("Akashi550",8000),("Kim_5+",7000),
    ("Cracker_7",8500),("-AGGRESSIV-",7750),("mei_mei",9103),("SilentHill",23100),("HaiSan",15700),
    ("WebRU",14290),("DmitryFlow",22000),("AllD-995",14000),("Hatin",9720),("Рил_сучк@.",9280),
    ("Издатель",11030),("GidiK",9700),("Woods_s",23100),("RWBYLOVE",10000),("kintownskiy",10000),
    ("Sw1ty",8000),("Ley-Ley",7100),("OblakaT_T",9000),("BanShei",7000),("Читатель+друг",8000),
    ("Jdhdbx",11110),("Vaenkh",8500),("moonsh1ne",8050),("Sas47",11010),("Takahikoo",8000),("Aki_Ram",6000),
    ("Mefisto51",26000),("S.a.m.u.r.a.i.",8000),("So1oMooN",7000),("etoRomantic",8000),("Амен",8000),
    ("Vallynor",9000),("Saytoriya",9000),("KOST9N",8000),("feazxch",8000),("Velial_Salivan",8000),
    ("Dr.Rи",8000),("tenofmoses",6000),("BigMen07",6000),("Hazenberg",6000),("--Lucifiel--",10500),
    ("Akihiko",7900),("TiltExist",10910),("stas211242",9130),("CKCKCK",8000),("ДолинаРекиСетунь",20570),
    ("over-time",9190),("Alafex",7000),("Luneheim",6000),("Fox94",10000),("SamuraFs",6000),("Sanctuary_",10000),
    ("Sunburst",9000),("Sckat_Man",4000),("LLIKoJIoma",6000),("Acediaqq",6000),("necromant",6020),
    ("Henati",6000),("oportew",5000),("Aleksan_09",6000),("alan-hui",7260)
]

# ----------------- ВСПОМОГАТЕЛЬНЫЕ -----------------
def super_normalize(name):
    if name is None:
        return ""
    s = unicodedata.normalize('NFKC', str(name)).strip().lower()
    s = re.sub(r'\s+', '', s)
    s = re.sub(r'[_\-.]', '', s)
    replacements = {
        'ᴍ': 'm', 'ᴛ': 't', 'ᴇ': 'e', 'ᴘ': 'p', 'ᴅ': 'd', 'ᴄ': 'c', 'ᴋ': 'k',
        'Ƥ': 'p', 'Ƭ': 't', 'Ρ': 'p', 'Ѕ': 's', 'ຮ': 's', 'ı': 'i',
        'а': 'a', 'А': 'a', 'в': 'b', 'В': 'b', 'с': 'c', 'С': 'c',
        'е': 'e', 'Е': 'e', 'н': 'h', 'Н': 'h', 'к': 'k', 'К': 'k',
        'м': 'm', 'М': 'm', 'о': 'o', 'О': 'o', 'р': 'p', 'Р': 'p',
        'т': 't', 'Т': 't', 'х': 'x', 'Х': 'x', 'у': 'y', 'У': 'y',
        'і': 'i', 'І': 'i', 'ӏ': 'i', '₽': 'p',
    }
    return ''.join(replacements.get(c, c) for c in s)

def ensure_placeholder():
    ph = Path(AVATAR_PLACEHOLDER)
    if not ph.exists():
        try:
            ph.parent.mkdir(parents=True, exist_ok=True)
            ph.write_bytes(requests.get("https://via.placeholder.com/96").content)
            log("-> placeholder avatar created")
        except Exception as e:
            log("-> placeholder download failed:", e)

def parse_lightning_text(raw_text):
    if not raw_text:
        return 0
    raw = raw_text.strip().replace(",", ".").upper()
    try:
        if "K" in raw:
            return int(float(raw.replace("K","")) * 1000)
        if "M" in raw:
            return int(float(raw.replace("M","")) * 1_000_000)
        return int(float(raw))
    except Exception:
        digits = re.sub(r"[^\d]", "", raw)
        return int(digits) if digits else 0

def fetch_guild(guild_url, allowed_norms, guild_label):
    log(f"[fetch_guild] Start: {guild_label} -> {guild_url}")
    parsed = {}
    avatars = {}
    profiles = {}
    try:
        resp = requests.get(guild_url, timeout=20)
        log(f"[fetch_guild] HTTP status: {resp.status_code}")
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        cards = soup.find_all("a", href=re.compile(r"^/user/\d+/about"))
        log(f"[fetch_guild] Found cards on page: {len(cards)}")
        for card in cards:
            nick_tag = card.find("span", class_=re.compile(r"font-semibold"))
            if not nick_tag:
                continue
            site_nick = nick_tag.text.strip()
            norm = super_normalize(site_nick)
            if norm not in allowed_norms:
                # пропускаем участников не из manual-списка
                continue
            href = card.get("href") or ""
            profiles[norm] = BASE_URL + href if href else BASE_URL
            img = card.find("img")
            avatar_url = None
            if img:
                avatar_url = img.get("src") or img.get("data-src") or img.get("data-original")
            avatar_path = AVATARS_DIR / f"{norm}.jpg"
            if avatar_url:
                if not avatar_path.exists():
                    try:
                        r = requests.get(avatar_url, timeout=20)
                        avatar_path.write_bytes(r.content)
                        log(f"[fetch_guild] Avatar saved for {site_nick}")
                    except Exception as e:
                        log(f"[fetch_guild] Avatar download error for {site_nick}:", e)
                        avatar_path = Path(AVATAR_PLACEHOLDER)
            else:
                avatar_path = Path(AVATAR_PLACEHOLDER)
            avatars[norm] = avatar_path.as_posix()
            lightning_div = card.find("div", attrs={"data-slot": "badge"})
            lightning = parse_lightning_text(lightning_div.text) if lightning_div else 0
            parsed[norm] = {"site_nick": site_nick, "lightning": lightning}
        log(f"[fetch_guild] Parsed (filtered by manual) count: {len(parsed)}")
    except Exception as e:
        log("[fetch_guild] ERROR:", e)
    return parsed, avatars, profiles

# ----------------- MAIN -----------------
log("=== SCRIPT START ===")
ensure_placeholder()

# карты initial/display
initial_g1 = {super_normalize(d): int(v) for d, v in guild1_manual_pairs}
display_g1 = {super_normalize(d): d for d, v in guild1_manual_pairs}
initial_g2 = {super_normalize(d): int(v) for d, v in guild2_manual_pairs}
display_g2 = {super_normalize(d): d for d, v in guild2_manual_pairs}

allowed_g1 = set(initial_g1.keys())
allowed_g2 = set(initial_g2.keys())

log("[1/6] Parsing guild1 (Eternal Watchers)...")
g1_parsed, g1_avatars_map, g1_profiles_map = fetch_guild(GUILD1_URL, allowed_g1, "Eternal Watchers")

log("[2/6] Parsing guild2 (Eternal Demonic)...")
g2_parsed, g2_avatars_map, g2_profiles_map = fetch_guild(GUILD2_URL, allowed_g2, "Eternal Demonic")

def build_participants(manual_pairs, initial_map, parsed_map, avatars_map, profiles_map, guild_label):
    out = []
    for display, init_val in manual_pairs:
        norm = super_normalize(display)
        init_v = int(init_val or 0)
        if norm in parsed_map:
            info = parsed_map[norm]
            current_v = int(info.get("lightning", 0))
            display_label = info.get("site_nick") or display
        else:
            current_v = init_v
            display_label = display
        diff = current_v - init_v
        if diff < 0:
            diff = 0
        avatar = avatars_map.get(norm, Path(AVATAR_PLACEHOLDER).as_posix())
        profile = profiles_map.get(norm, BASE_URL)
        out.append({
            "norm": norm,
            "display": display_label,
            "initial": init_v,
            "current": current_v,
            "diff": diff,
            "avatar": avatar,
            "profile": profile,
            "guild": guild_label
        })
    out.sort(key=lambda x: x["diff"], reverse=True)
    return out

log("[3/6] Building participants lists (only manual entries)...")
participants_g1 = build_participants(guild1_manual_pairs, initial_g1, g1_parsed, g1_avatars_map, g1_profiles_map, "Eternal Watchers")
participants_g2 = build_participants(guild2_manual_pairs, initial_g2, g2_parsed, g2_avatars_map, g2_profiles_map, "Eternal Demonic")

log("-> G1 manual count:", len(participants_g1), " G2 manual count:", len(participants_g2))

log("[4/6] Building combined TOP-10...")
all_participants = participants_g1 + participants_g2
all_sorted = sorted(all_participants, key=lambda x: x["diff"], reverse=True)
top10 = all_sorted[:10]

# Formatting helper
def fmt(n):
    try:
        return f"{n:,}".replace(",", " ")
    except:
        return str(n)

def render_cards(parts):
    html = ""
    place = 1
    for p in parts:
        html += (
            "<div class='card'>"
            f"<div class='place'>#{place}</div>"
            f"<div class='avatar' style=\"background-image: url('{p['avatar']}');\"></div>"
            "<div class='info'>"
            f"<div class='nickname'><a href='{p['profile']}' target='_blank' rel='noopener noreferrer'>{p['display']}</a></div>"
            "<div class='row'>"
            f"<div class='stat'><span class='label'>Начальный вклад</span><span class='val'>{fmt(p['initial'])}</span></div>"
            f"<div class='stat'><span class='label'>Текущий вклад</span><span class='val'>{fmt(p['current'])}</span></div>"
            f"<div class='stat big'><span class='label'>Сумма залитых молний</span><span class='val bigval'>{fmt(p['diff'])}</span></div>"
            "</div>"
            "</div></div>\n"
        )
        place += 1
    return html

cards_g1 = render_cards(participants_g1)
cards_g2 = render_cards(participants_g2)
cards_top10 = render_cards(top10)

# ----------------- HTML TEMPLATE -----------------
log("[5/6] Generating HTML (index.html)...")
now_msk = datetime.now(timezone(timedelta(hours=3))).strftime("%d.%m.%Y %H:%M (МСК)")

html_template = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Eternal guilds — статистика</title>
<style>
:root{--bg:#0f1114;--card:#141618;--muted:#9aa4ad;--accent:#4aa3ff;--accent2:#82b5f7;--gold:#ffd24d;--text:#e6eef6}
html,body{height:100%;margin:0;background:var(--bg);color:var(--text);font-family:Inter,Segoe UI,Roboto,Arial,sans-serif}
header{background:linear-gradient(180deg,#0b0d0f,#101214);padding:18px 12px;border-bottom:1px solid rgba(255,255,255,0.03);text-align:center}
header h1{margin:0;font-size:20px;font-weight:600}
header .updated{margin-top:6px;color:var(--muted);font-size:13px}
.container{max-width:1200px;margin:18px auto;padding:0 12px}
.tabs{display:flex;gap:8px;justify-content:center;margin-bottom:18px;flex-wrap:wrap}
.tab-btn{background:transparent;border:1px solid rgba(255,255,255,0.04);color:var(--text);padding:10px 14px;border-radius:10px;cursor:pointer;font-weight:600}
.tab-btn.active{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.00));box-shadow:0 6px 16px rgba(0,0,0,0.6)}
.panel{display:none}
.panel.active{display:block}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}
.card{background:var(--card);border-radius:10px;padding:14px;display:flex;gap:14px;align-items:flex-start;box-shadow:0 6px 22px rgba(0,0,0,0.6);transition:transform .12s}
.card:hover{transform:translateY(-6px)}
.avatar{width:96px;height:96px;border-radius:50%;background:#222;background-size:cover;background-position:center;border:2px solid rgba(255,255,255,0.03);flex-shrink:0}
.place{font-weight:800;color:var(--gold);width:64px;text-align:center;font-size:18px}
.info{flex:1;min-width:0}
.nickname a{color:var(--accent);text-decoration:none;font-weight:700;font-size:1.05em}
.nickname a:hover{color:var(--accent2);text-decoration:underline}
.row{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-top:8px}
.stat{background:rgba(255,255,255,0.01);padding:8px 10px;border-radius:8px;display:flex;flex-direction:column;min-width:120px;box-sizing:border-box}
.stat .label{color:var(--muted);font-size:0.85em;margin-bottom:6px;white-space:nowrap}
.stat .val{font-weight:700;font-size:1.02em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.stat.big{flex:1;min-width:140px}
.bigval{font-size:1.1em;color:var(--gold)}
.footer{text-align:center;color:var(--muted);padding:14px 8px;border-top:1px solid rgba(255,255,255,0.02);margin-top:18px}
@media (max-width:900px){.grid{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}}
@media (max-width:700px){
  .grid{grid-template-columns:1fr}
  .card{flex-direction:column;align-items:center;text-align:center;padding:16px}
  .avatar{width:120px;height:120px}
  .place{width:auto}
  .row{flex-direction:column;align-items:center}
  .stat{min-width:unset;width:100%;box-sizing:border-box}
  .stat .label{white-space:normal}
  .stat .val{font-size:1.08em}
}
</style>
</head>
<body>
<header>
  <h1>Eternal guilds — статистика</h1>
  <div class="updated">Последнее обновление: __NOW__</div>
</header>
<div class="container">
  <div class="tabs" role="tablist">
    <button class="tab-btn active" data-target="tab1">Eternal Watchers</button>
    <button class="tab-btn" data-target="tab2">Eternal Keepers</button>
    <button class="tab-btn" data-target="tab3">Общий TOP-10</button>
  </div>

  <section id="tab1" class="panel active"><div class="grid">
  __CARDS_G1__
  </div></section>

  <section id="tab2" class="panel"><div class="grid">
  __CARDS_G2__
  </div></section>

  <section id="tab3" class="panel"><div class="grid">
  __CARDS_T10__
  </div></section>

  <div class="footer">Сортировка во всех вкладках — по <strong>Сумма залитых молний</strong> (current − initial). Только пользователи из manual-списков отображаются на сайте.</div>
</div>

<script>
document.querySelectorAll('.tab-btn').forEach(function(btn){
  btn.addEventListener('click', function(){
    document.querySelectorAll('.tab-btn').forEach(function(b){ b.classList.remove('active'); });
    document.querySelectorAll('.panel').forEach(function(p){ p.classList.remove('active'); });
    btn.classList.add('active');
    document.getElementById(btn.dataset.target).classList.add('active');
    window.scrollTo({top:0,behavior:'smooth'});
  });
});
</script>
</body>
</html>
"""

html = html_template.replace("__NOW__", now_msk).replace("__CARDS_G1__", cards_g1).replace("__CARDS_G2__", cards_g2).replace("__CARDS_T10__", cards_top10)

OUT = Path("index.html")
OUT.write_text(html, encoding="utf-8")
log("-> index.html saved:", OUT.resolve())

# ----------------- GIT PUSH (без всплывающих окон) -----------------
def try_git_push():
    """
    Выполняем git add/commit/push, при этом:
    - capture_output=True чтобы ничего не печаталось в консоль
    - на Windows используем creationflags=subprocess.CREATE_NO_WINDOW (если доступно),
      чтобы не открывалось отдельное окно процесса
    - устанавливаем GIT_TERMINAL_PROMPT=0 в окружении, чтобы git не ждал ввода пароля
      (если push требует аутентификации — push завершится с ошибкой, которую мы залогируем)
    """
    log("[6/6] Attempting git add/commit/push (silent)...")
    # подготовка параметров subprocess
    creationflags = 0
    if os.name == "nt":
        # защита: возможно атрибут отсутствует в старых версиях
        try:
            creationflags = subprocess.CREATE_NO_WINDOW
        except Exception:
            creationflags = 0
    # окружение: отключаем интерактивные git prompt'ы
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"

    def run_cmd(cmd):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False, creationflags=creationflags)
            return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
        except Exception as e:
            return 999, "", str(e)

    # add
    rc, out, err = run_cmd(["git", "add", "index.html", "avatars"])
    log("git add rc:", rc, "stdout:", out, "stderr:", err)
    # commit
    commit_msg = f"Auto update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    rc2, out2, err2 = run_cmd(["git", "commit", "-m", commit_msg])
    log("git commit rc:", rc2, "stdout:", out2, "stderr:", err2)
    # push
    rc3, out3, err3 = run_cmd(["git", "push", "origin", "main"])
    log("git push rc:", rc3, "stdout:", out3, "stderr:", err3)
    if rc3 == 0:
        log("-> Git push successful.")
    else:
        log("-> Git push finished with non-zero exit code. If authentication is needed, configure a token/SSH key or push manually.")

# Запускаем попытку пуша
try_git_push()

log("=== SCRIPT FINISHED ===")
