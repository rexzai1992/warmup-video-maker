"""Google Flow helper: drives a real Chrome window (own profile in .flow-chrome/) that the owner logged into.

  python tools/flow_auto.py open                  # start Chrome on Flow; log in once by hand
  python tools/flow_auto.py look [name]           # screenshot + list of buttons/inputs (for checking the page)
  python tools/flow_auto.py run school --limit 3  # make clips in prompt order -> footage/flow/school/<id>.mp4
  python tools/flow_auto.py run school --only hop,tag --redo   # remake chosen clips
Progress (and resume point) is flow_prompts/progress.json. Waits 20-60 s between clips, 5-10 min every 10 clips.

The owner accepted the account risk of automating Flow (Google's terms). The script never solves captchas or logs in:
it stops and asks for a human whenever Flow shows anything unusual.
"""
import json, pathlib, random, re, subprocess, sys, time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parent.parent
PROFILE = ROOT / ".flow-chrome"
SHOTS = ROOT / "output" / "flow_shots"
PORT = 9333
FLOW_URL = "https://labs.google/fx/tools/flow"
CHROME = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]


def chrome_exe():
    for c in CHROME:
        if pathlib.Path(c).exists():
            return c
    sys.exit("Google Chrome not found")


def open_chrome():
    PROFILE.mkdir(exist_ok=True)
    subprocess.Popen([chrome_exe(), f"--remote-debugging-port={PORT}", f"--user-data-dir={PROFILE}",
                      "--no-first-run", "--no-default-browser-check", FLOW_URL])
    print("Chrome opened. Log in to Google Flow in that window (only needed once).")


def connect(p):
    browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    ctx = browser.contexts[0]
    pages = [pg for pg in ctx.pages if "labs.google" in pg.url] or ctx.pages
    return browser, ctx, pages[0]


ELEMENTS_JS = """() => {
  const out = [];
  const els = document.querySelectorAll('button, a, input, textarea, [role=button], [role=menuitem], [role=option], [role=combobox], [role=tab], [contenteditable=true], video');
  for (const e of els) {
    const r = e.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    out.push({tag: e.tagName.toLowerCase(), role: e.getAttribute('role') || '',
      text: (e.innerText || e.value || '').trim().slice(0, 80),
      aria: e.getAttribute('aria-label') || '', ph: e.getAttribute('placeholder') || '',
      x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2),
      src: e.tagName === 'VIDEO' ? (e.currentSrc || e.src || '').slice(0, 120) : ''});
  }
  return out;
}"""


def look(name="look"):
    from playwright.sync_api import sync_playwright
    SHOTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser, ctx, page = connect(p)
        shot = SHOTS / f"{name}.png"
        page.screenshot(path=str(shot))
        print("url:", page.url)
        print("title:", page.title())
        for e in page.evaluate(ELEMENTS_JS):
            print(json.dumps(e, ensure_ascii=False))
        print("screenshot:", shot)


def find(page, label):
    """Smallest visible clickable thing named `label` (aria-label, button text, option/menu text)."""
    for loc in (page.locator(f'[aria-label="{label}"]:visible'),
                page.get_by_role("button", name=label, exact=True),
                page.get_by_role("radio", name=label),
                page.get_by_role("option", name=label),
                page.get_by_role("menuitem", name=label),
                page.get_by_role("tab", name=label),
                page.locator(f'button:visible:has-text("{label}")'),
                page.locator(f'[role=option]:visible:has-text("{label}"), [role=menuitem]:visible:has-text("{label}")')):
        if loc.count():
            return loc.last if loc.count() > 1 and "option" in str(loc) else loc.first
    raise RuntimeError(f"nothing named '{label}' on the page")


def click(label, name="after_click"):
    """Exploration helper: click the first visible element whose text or aria-label is `label`."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser, ctx, page = connect(p)
        find(page, label).click(timeout=10000)
        page.wait_for_timeout(2500)
    look(name)


# ------------------------------------------------------------------ batch generation
PROGRESS = ROOT / "flow_prompts" / "progress.json"
MODEL = "Veo 3.1 - Lite"          # 10 credits per 8 s 720p clip (owner's choice: fits the credit budget)
MAX_COST = 10
LOW_CREDITS = 30
STOP_WORDS = ["captcha", "unusual activity", "unusual traffic", "verify it's you", "too many requests", "rate limit",
              "not enough credits", "insufficient credits", "out of credits", "try again later", "something went wrong"]
FAIL_WORDS = ["fail", "violat", "policy", "couldn't", "could not", "unable to", "error", "blocked", "not allowed",
              "try a different prompt", "retry"]
PEOPLE = ["children", "child", "kids", "students", "people", "teacher", "fans", "crowd", "crowds", "dancers", "teams"]


class Stop(Exception):
    """Something a human must look at. The batch stops; progress.json says where it was."""


def load_progress():
    return json.loads(PROGRESS.read_text(encoding="utf-8")) if PROGRESS.exists() else {}


def save_progress(pr):
    PROGRESS.write_text(json.dumps(pr, indent=1, ensure_ascii=False), encoding="utf-8")


def pause(a, b, why=""):
    s = random.uniform(a, b)
    print(f"    waiting {s:.0f} s {why}", flush=True)
    time.sleep(s)


def dismiss(page):
    for label in ("Get started", "Got it", "Dismiss banner"):
        loc = page.get_by_role("button", name=label, exact=True)
        if loc.count() and loc.first.is_visible():
            loc.first.click(); page.wait_for_timeout(700)
    c = page.locator('[aria-label^="Close"]:visible')
    if c.count():
        c.first.click(); page.wait_for_timeout(700)


def check_page(page):
    if "flow.google.com" not in page.url:
        raise Stop(f"left Flow (signed out?) - page is {page.url}")
    if page.locator('iframe[src*="recaptcha/api2/bframe"]:visible, iframe[title*="challenge"]:visible').count():
        raise Stop("Flow shows a captcha")
    text = page.evaluate("() => document.body.innerText").lower().replace("protected by recaptcha", "")
    for w in STOP_WORDS:
        if w in text:
            raise Stop(f"Flow says: '{w}'")


def read_credits(page):
    find(page, "Account details").click()
    page.wait_for_timeout(1500)
    m = re.search(r"([\d,]+) Google Flow credits", page.evaluate("() => document.body.innerText"))
    page.locator('[aria-label^="Close account"]:visible').first.click()
    page.wait_for_timeout(600)
    return int(m.group(1).replace(",", "")) if m else None


def open_project(page, version, pr):
    url = pr.setdefault(version, {}).get("_project")
    if url:
        if page.url != url:
            page.goto(url); page.wait_for_timeout(4000)
    else:
        page.goto("https://flow.google.com/"); page.wait_for_timeout(4000)
        dismiss(page)
        find(page, "New project").click()
        page.wait_for_url("**/project/**", timeout=30000); page.wait_for_timeout(3000)
        dismiss(page)
        title = page.get_by_role("textbox", name="Editable text")
        if not title.count():
            title = page.locator('input[aria-label="Editable text"]')
        title.first.click(); page.keyboard.press("Control+A")
        page.keyboard.type(f"Warm-up {version}", delay=60); page.keyboard.press("Enter")
        pr[version]["_project"] = page.url
        save_progress(pr)
    dismiss(page)
    check_page(page)


def setup_settings(page):
    find(page, "Settings trigger").click(); page.wait_for_timeout(900)
    for r in ("Video", "Frames", "16:9"):
        page.get_by_role("radio").filter(has_text=r).first.click(); page.wait_for_timeout(400)
    find(page, "Select model family").click(); page.wait_for_timeout(700)
    page.get_by_role("menuitem").filter(has_text=MODEL).first.click(); page.wait_for_timeout(700)
    page.get_by_role("radio").filter(has_text="x1").first.click(); page.wait_for_timeout(400)
    cost = int(re.sub(r"\D", "", page.locator('a:visible:has-text("credits")').first.inner_text()) or 0)
    page.keyboard.press("Escape"); page.wait_for_timeout(500)
    if cost > MAX_COST:
        raise Stop(f"a clip would cost {cost} credits (expected {MAX_COST}) - settings look wrong")
    return cost


def tiles(page):
    """Tiles currently in the page, newest first. Flow only keeps on-screen tiles in the page (virtual list),
    so never count them - compare the TOP tile's identity (media src or prompt text) instead."""
    return page.evaluate("""() => [...document.querySelectorAll('flow-video-tile')].map(t => {
        const v = t.querySelector('video'), im = t.querySelector('img[src]');
        const vs = v ? (v.currentSrc || v.src || '') : '', is = im ? im.src : '';
        const text = t.innerText.replace(/\s+/g, ' ').slice(0, 200);
        const title = (t.querySelector('[aria-label]:not([aria-label="Generated video"]):not([aria-label="Favorite"])' +
                       ':not([aria-label="Reuse prompt"]):not([aria-label="More options"])') || {}).ariaLabel || '';
        return {text, video: !!vs, img: !!is, key: vs || is || title || text,
                more: !!t.querySelector('[aria-label="More options"]')};
    })""")


def top_key(page):
    page.evaluate("() => { const m = document.querySelector('main') || document.scrollingElement; window.scrollTo(0, 0);"
                  " document.querySelectorAll('*').forEach(e => { if (e.scrollTop > 0) e.scrollTop = 0; }); }")
    page.wait_for_timeout(800)
    ts = tiles(page)
    return ts[0]["key"] if ts else None


def type_prompt(page, prompt):
    box = page.get_by_role("textbox", name="What do you want to create?")
    box.click(); page.keyboard.press("Control+A"); page.keyboard.press("Delete")
    page.keyboard.type(prompt, delay=random.randint(15, 35))
    page.wait_for_timeout(800)
    got = box.inner_text().strip()
    if got != prompt.strip():
        raise Stop(f"prompt box has {len(got)} chars, expected {len(prompt)} - not submitting")


def generate(page, prompt, timeout=900):
    """Submit one prompt and wait for its tile (the new top tile). Returns ('done', 0) or ('failed', text)."""
    before = top_key(page)
    type_prompt(page, prompt)
    find(page, "Start generation").click()
    t0, last, mine = time.time(), None, None
    while time.time() - t0 < timeout:
        page.wait_for_timeout(5000)
        check_page(page)
        page.evaluate("() => { window.scrollTo(0, 0); document.querySelectorAll('*').forEach(e => { if (e.scrollTop > 0) e.scrollTop = 0; }); }")
        ts = tiles(page)
        if not ts:
            continue
        t = ts[0]
        if mine is None:
            if t["key"] == before:                 # our tile hasn't appeared yet
                continue
            mine = True
        if t["text"] != last:
            print(f"    {time.time() - t0:4.0f}s tile: {t['text'][:90]}", flush=True)
            last = t["text"]
        if any(w in t["text"].lower() for w in FAIL_WORDS):
            return "failed", t["text"]
        if t["more"] and (t["video"] or t["img"]) and "%" not in t["text"]:
            page.wait_for_timeout(2000)
            return "done", 0
    raise Stop(f"clip not finished after {timeout // 60} min")


def wait_newest(page, timeout=900):
    """Resume after a crash: the newest tile (first) belongs to the job that was submitted last."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        check_page(page)
        ts = tiles(page)
        if not ts:
            return None
        t = ts[0]
        if any(w in t["text"].lower() for w in FAIL_WORDS):
            return None
        if t["more"] and (t["video"] or t["img"]) and "%" not in t["text"]:
            return 0
        page.wait_for_timeout(5000)
    raise Stop("the clip submitted before the crash never finished")


def download(page, idx, out):
    tile = page.locator("flow-video-tile").nth(idx)
    tile.scroll_into_view_if_needed(); tile.hover(); page.wait_for_timeout(900)
    tile.locator('[aria-label="More options"]').first.click(); page.wait_for_timeout(900)
    page.get_by_role("menuitem").filter(has_text="Download").first.click(); page.wait_for_timeout(900)
    with page.expect_download(timeout=180000) as d:
        page.get_by_role("menuitem").filter(has_text="Original size").first.click()
    tmp = out.with_suffix(".part")
    d.value.save_as(str(tmp))
    page.keyboard.press("Escape")
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(tmp)],
                       capture_output=True, text=True)
    dur = float(r.stdout.strip() or 0)
    if dur < 3:
        tmp.unlink(missing_ok=True)
        raise Stop(f"downloaded file for {out.name} looks broken ({dur:.1f} s)")
    tmp.replace(out)
    return dur


def rewrite(prompt):
    """Safer retry for a blocked prompt: same place, no people."""
    parts = [p.strip() for p in re.split(r"(?<=\.)\s+", prompt)]
    scene = parts[1]
    keep = [c for c in scene.rstrip(".").split(",") if not any(re.search(rf"\b{w}\b", c, re.I) for w in PEOPLE)]
    parts[1] = ",".join(keep).strip() + ". Empty scene with no people."
    return " ".join(parts).replace(", people far away at the sides", "")


def run(version, limit=None, only=None, redo=False):
    from playwright.sync_api import sync_playwright
    items = json.loads((ROOT / "flow_prompts" / f"{version}.json").read_text(encoding="utf-8"))
    if only:
        items = [e for e in items if e["id"] in only]
    dest = ROOT / "footage" / "flow" / version
    dest.mkdir(parents=True, exist_ok=True)
    pr = load_progress()
    made = 0
    with sync_playwright() as p:
        browser, ctx, page = connect(p)
        page.bring_to_front()
        open_project(page, version, pr)
        cost = setup_settings(page)
        credits = read_credits(page)
        print(f"[{version}] model {MODEL}, {cost} credits per clip, {credits} credits left", flush=True)
        for e in items:
            rec = pr[version].setdefault(e["id"], {"n": e["n"]})
            out = dest / e["save_as"]
            if rec.get("status") == "done" and out.exists() and not (redo and only):
                continue
            if out.exists() and not (redo and only):
                rec.update(status="done", file=str(out.relative_to(ROOT)), note="file was already there")
                save_progress(pr); continue
            if rec.get("status") == "submitted":          # crashed after submitting: fetch it, don't pay twice
                idx = wait_newest(page)
                if idx is None:
                    raise Stop(f"{e['id']} was submitted before a crash but its clip isn't in the project. "
                               f"Check Flow; delete its entry in progress.json to remake it")
                dur = download(page, idx, out)
                rec.update(status="done", file=str(out.relative_to(ROOT)), seconds=round(dur, 2), note="recovered")
                save_progress(pr)
                print(f"  #{e['n']} {e['id']}: recovered clip from before the crash ({dur:.1f} s)", flush=True)
                continue
            if limit is not None and made >= limit:
                break
            if credits is not None and credits < max(LOW_CREDITS, cost):
                raise Stop(f"low credits: {credits} left")
            if made and made % 10 == 0:
                pause(300, 600, "(break after 10 clips)")
            elif made:
                pause(20, 60, "(between clips)")
            prompt = e["prompt"]
            for attempt in (1, 2):
                print(f"  #{e['n']} {e['id']} (try {attempt})", flush=True)
                rec.update(status="submitted", prompt_used=prompt, tries=rec.get("tries", 0) + 1,
                           time=time.strftime("%Y-%m-%d %H:%M:%S"))
                save_progress(pr)
                state, info = generate(page, prompt)
                made += 1
                if state == "done":
                    break
                rec.update(status="failed", error=info)
                save_progress(pr)
                print(f"    blocked/failed: {info}", flush=True)
                if attempt == 2:
                    raise Stop(f"{e['id']} failed twice: {info}")
                prompt = rewrite(prompt)
                rec["rewritten"] = prompt
                print(f"    retrying with: {prompt[:120]}...", flush=True)
                pause(20, 40, "(before retry)")
            dur = download(page, info, out)
            before = credits
            credits = read_credits(page)
            rec.update(status="done", file=str(out.relative_to(ROOT)), seconds=round(dur, 2),
                       credits_used=(before - credits) if before is not None and credits is not None else None,
                       credits_left=credits)
            rec.pop("error", None)
            save_progress(pr)
            print(f"    saved {out.relative_to(ROOT)} ({dur:.1f} s), credits left: {credits}", flush=True)
    done = sum(1 for k, v in pr[version].items() if not k.startswith("_") and v.get("status") == "done")
    print(f"[{version}] {done}/{len(json.loads((ROOT / 'flow_prompts' / f'{version}.json').read_text(encoding='utf-8')))} clips done")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "open"
    if cmd == "run":
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument("cmd"); ap.add_argument("version")
        ap.add_argument("--limit", type=int, help="make at most N new clips this time")
        ap.add_argument("--only", help="comma-separated part ids (e.g. to remake bad clips)")
        ap.add_argument("--redo", action="store_true", help="with --only: remake even if the clip exists")
        a = ap.parse_args()
        try:
            run(a.version, a.limit, a.only.split(",") if a.only else None, a.redo)
        except Stop as s:
            print(f"\n!! STOPPED: {s}\n   Fix it, then run the same command again - it continues where it stopped.")
            sys.exit(2)
        sys.exit(0)
    if cmd == "open":
        open_chrome()
    elif cmd == "look":
        look(*(sys.argv[2:3] or ["look"]))
    elif cmd == "click":
        click(sys.argv[2], *(sys.argv[3:4] or ["after_click"]))
