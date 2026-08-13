window.LIKES_VER = 46;

(function () {
  const SUPABASE_URL = "https://nlvalirjjqdjzrgfqdzj.supabase.co";
  const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5sdmFsaXJqanFkanpyZ2ZxZHpqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2MjMyMjAsImV4cCI6MjA3NjE5OTIyMH0.CUunHUu1kCZVy7qjBhnbHIO49JK9akhNgdcJGBx_tsI";

  if (!window.supabase) { console.error("[likes] sdk missing"); return; }
  const sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    auth: { persistSession: true, autoRefreshToken: true, storageKey: "ew-likes" },
  });

  const STATE = { user: null, liked: new Set(), counts: Object.create(null) };
  const hydrated = new WeakSet();
  const chunk = (a, n) => { const r=[]; for (let i=0;i<a.length;i+=n) r.push(a.slice(i, i+n)); return r; };
  const setCount = (btn, n) => { (btn.querySelector(".like-count")||{}).textContent = String(n ?? 0); };
  const setLiked = (btn, v) => btn.classList.toggle("liked", !!v);

  async function ensureUser() {
    const g = await sb.auth.getSession();
    if (g.data.session?.user) { STATE.user = g.data.session.user; return STATE.user; }
    const { data, error } = await sb.auth.signInAnonymously();
    if (error) throw error;
    STATE.user = data.user; return STATE.user;
  }

  async function loadInitial(buttons) {
    const ids = [...new Set(buttons.map(b => b.dataset.cardId).filter(Boolean))];
    if (!ids.length || !STATE.user) return;

    const likedAll = [];
    for (const part of chunk(ids, 500)) {
      const { data } = await sb.from("card_likes")
        .select("card_id")
        .eq("user_id", STATE.user.id)
        .in("card_id", part);
      if (data) likedAll.push(...data);
    }
    STATE.liked = new Set(likedAll.map(r => r.card_id));

    const countsAll = [];
    for (const part of chunk(ids, 500)) {
      const { data } = await sb.from("card_like_counter")
        .select("card_id,count")
        .in("card_id", part);
      if (data) countsAll.push(...data);
    }
    for (const r of countsAll) STATE.counts[r.card_id] = Number(r.count) || 0;

    for (const btn of buttons) {
      const id = btn.dataset.cardId;
      setCount(btn, STATE.counts[id] ?? 0);
      setLiked(btn, STATE.liked.has(id));
    }
  }

  async function like(cardId) {
    const { error } = await sb.from("card_likes").insert({ card_id: cardId, user_id: STATE.user.id });
    if (error && error.code !== "23505") throw error;
  }
  async function unlike(cardId) {
    const { error } = await sb.from("card_likes")
      .delete().eq("card_id", cardId).eq("user_id", STATE.user.id);
    if (error) throw error;
  }
  async function refreshOne(cardId) {
    const [my, cnt] = await Promise.all([
      sb.from("card_likes").select("card_id").eq("card_id", cardId).eq("user_id", STATE.user.id).limit(1),
      sb.from("card_like_counter").select("count").eq("card_id", cardId).maybeSingle(),
    ]);
    const mine = !!(my.data && my.data.length);
    const count = (cnt.data?.count) || 0;
    if (mine) STATE.liked.add(cardId); else STATE.liked.delete(cardId);
    STATE.counts[cardId] = count;
    return { mine, count };
  }

  function buildButton(slot) {
    const id = slot.dataset.cardId;
    if (!id) return null;

    const btn = document.createElement("button");
    btn.className = "like-btn"; btn.type = "button";
    btn.innerHTML = `<span class="heart" aria-hidden="true">❤</span> <span class="like-count">0</span>`;
    slot.replaceChildren(btn);

    btn.addEventListener("click", async (e) => {
      e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
      btn.disabled = true;
      try {
        await ensureUser();
        if (STATE.liked.has(id)) await unlike(id); else await like(id);
        const { mine, count } = await refreshOne(id);
        setLiked(btn, mine); setCount(btn, count);
      } catch (err) {
        console.error("[likes] click", err);
      } finally {
        btn.disabled = false;
      }
    }, { capture: true });

    return btn;
  }

  async function hydrateAll(root = document) {
    const slots = Array.from(root.querySelectorAll('.like-slot[data-card-id]'))
      .filter(s => !hydrated.has(s));
    if (!slots.length) return;

    slots.forEach(s => hydrated.add(s));

    const buttons = [];
    for (const s of slots) {
      const b = buildButton(s);
      if (b) { b.dataset.cardId = s.dataset.cardId; buttons.push(b); }
    }

    try { await ensureUser(); } catch (e) { console.warn("[likes] auth", e); }
    await loadInitial(buttons);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => hydrateAll());
  } else {
    hydrateAll();
  }

  const mo = new MutationObserver(muts => {
    for (const m of muts) {
      for (const n of m.addedNodes) {
        if (!(n instanceof HTMLElement)) continue;
        if (n.matches?.('.like-slot[data-card-id]')) hydrateAll(n.parentElement || n);
        else if (n.querySelectorAll) {
          const has = n.querySelectorAll('.like-slot[data-card-id]').length;
          if (has) hydrateAll(n);
        }
      }
    }
  });
  mo.observe(document.documentElement, { childList: true, subtree: true });

  window.$$likes = {
    ver: () => window.LIKES_VER,
    user: async () => (await sb.auth.getUser()).data.user?.id,
    slots: () => document.querySelectorAll(".like-slot[data-card-id]").length,
  };
})();
