/* custom.js - Static Client-side Top 30 Dashboard script */
(function() {
  // --- STATE VARIABLES ---
  let allGuilds = [];
  let dbCachedData = null;
  let currentGuildDetail = null;
  const selectedCompareDirs = new Set();
  const charts = {};

  // --- HTML FALLBACKS & UTILITIES ---
  const formatNum = (num) => {
    if (num === undefined || num === null) return '0';
    return Number(num).toLocaleString('ru-RU');
  };

  const stripHtml = (html) => {
    if (!html) return '';
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    return tempDiv.textContent || tempDiv.innerText || '';
  };

  const formatShortNum = (num) => {
    if (num === undefined || num === null) return '0';
    const n = Number(num);
    if (Math.abs(n) >= 1_000_000) {
      return (n / 1_000_000).toFixed(1).replace('.0', '') + 'M';
    }
    if (Math.abs(n) >= 1_000) {
      return (n / 1_000).toFixed(1).replace('.0', '') + 'K';
    }
    return n.toString();
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Неизвестно';
    try {
      const d = new Date(dateStr);
      return d.toLocaleString('ru-RU', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'Europe/Moscow'
      }) + ' (МСК)';
    } catch {
      return dateStr;
    }
  };

  const getAvatarUrl = (avatarObj) => {
    const defaultAvatar = 'https://remanga.org/images/default-avatar.webp';
    if (!avatarObj) return defaultAvatar;

    let p = '';
    if (typeof avatarObj === 'string') {
      p = avatarObj;
    } else {
      p = avatarObj.mid || avatarObj.high || avatarObj.low || '';
    }
    if (!p) return defaultAvatar;

    // Already a full URL
    if (p.startsWith('http')) return p;
    // Absolute path starting with /media/
    if (p.startsWith('/media/')) return 'https://api.remanga.org' + p;
    // Relative path starting with media/
    if (p.startsWith('media/')) return 'https://api.remanga.org/' + p;
    // Other absolute paths (e.g. /something)
    if (p.startsWith('/')) return 'https://api.remanga.org/media' + p;
    // Bare relative paths (e.g. clubs/avatar_xxx.webp)
    return 'https://api.remanga.org/media/' + p;
  };

  const getAvatarHtml = (avatarObj, extraClass = '', extraStyle = '') => {
    const url = getAvatarUrl(avatarObj);
    if (url.endsWith('.webm') || url.endsWith('.mp4')) {
      return `<video src="${url}" class="${extraClass}" style="${extraStyle}" autoplay loop muted playsinline></video>`;
    }
    return `<img src="${url}" class="${extraClass}" style="${extraStyle}" onerror="this.src='https://remanga.org/images/default-avatar.webp'">`;
  };

  const getSection = () => document.getElementById('tab8') || document;

  // --- MAIN ENTRYPOINT ---
  function initDashboard() {
    const tab8Section = getSection();

    // Sub-tab Navigation inside Top 30
    tab8Section.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const targetTab = item.getAttribute('data-tab');
        showTab(targetTab);
      });
    });

    // Back to List
    const btnBack = tab8Section.querySelector('#btn-back-to-list');
    if (btnBack) {
      btnBack.addEventListener('click', () => showTab('dashboard'));
    }

    // Compare Selected Button
    const btnCompare = tab8Section.querySelector('#btn-compare-selected');
    if (btnCompare) {
      btnCompare.addEventListener('click', () => {
        if (selectedCompareDirs.size < 2) {
          alert('Выберите как минимум 2 гильдии для сравнения!');
          return;
        }
        showTab('compare');
      });
    }

    // Clear Compare Button
    const btnClearCompare = tab8Section.querySelector('#btn-clear-compare');
    if (btnClearCompare) {
      btnClearCompare.addEventListener('click', () => {
        selectedCompareDirs.clear();
        tab8Section.querySelectorAll('.compare-checkbox').forEach(cb => cb.checked = false);
        updateCompareBadge();
        renderCompareView();
      });
    }

    // Global Search
    const globalSearch = tab8Section.querySelector('#global-search');
    if (globalSearch) {
      globalSearch.addEventListener('input', (e) => {
        filterGuildsGrid(e.target.value.toLowerCase().trim());
      });
    }

    // Member Search
    const memberSearch = tab8Section.querySelector('#member-search');
    if (memberSearch) {
      memberSearch.addEventListener('input', (e) => {
        filterMembersTable(e.target.value.toLowerCase().trim());
      });
    }

    // Sorting selector
    const sortGuilds = tab8Section.querySelector('#sort-guilds');
    if (sortGuilds) {
      sortGuilds.addEventListener('change', () => {
        renderGuildsGrid();
      });
    }

    // Initial Fetch & Start Polling (every 5 minutes)
    fetchGuilds();
    setInterval(fetchGuilds, 300000);
  }

  // --- CORE LOGIC ---
  async function fetchGuilds() {
    const tab8Section = getSection();

    try {
      const res = await fetch('db.json');
      dbCachedData = await res.json();

      allGuilds = Object.values(dbCachedData.guilds).map(g => {
        const changes = calculateGrowth(g.history);
        changes.day = {
          diff: g.today_growth || 0,
          pct: g.total_coins_spent > 0 ? parseFloat((((g.today_growth || 0) / Math.max(1, g.total_coins_spent - (g.today_growth || 0))) * 100).toFixed(2)) : 0
        };
        return {
          id: g.id,
          name: g.name,
          dir: g.dir,
          avatar: g.avatar,
          cur_level: g.cur_level,
          exp: g.exp,
          members_count: g.members_count,
          rank: g.rank,
          total_coins_spent: g.total_coins_spent,
          changes
        };
      });

      // Update sync time
      const syncTimeEl = tab8Section.querySelector('#last-sync-time');
      if (syncTimeEl) {
        syncTimeEl.textContent = formatDate(dbCachedData.last_parse);
      }

      // Update overview header stats
      updateOverviewStats();

      // Render cards
      renderGuildsGrid();

      // If details view is open, refresh it in real-time
      if (currentGuildDetail) {
        showGuildDetail(currentGuildDetail.dir);
      }
    } catch (err) {
      console.error('Error fetching static db.json:', err);
      const cardsGrid = tab8Section.querySelector('#guilds-cards-container');
      if (cardsGrid) {
        const isLocalFile = window.location.protocol === 'file:';
        const errorMsg = isLocalFile 
          ? `Ошибка загрузки базы данных db.json.<br>
             <span style="font-size: 13px; color: var(--color-text-dim); margin-top: 8px; display: block; line-height: 1.5;">
               Браузер заблокировал запрос из-за политики безопасности CORS для локальных файлов (схема <b>file://</b>).<br>
               Для запуска выполните команду <code>npm run dev</code> в папке <b>Guildss</b> и откройте <b>http://localhost:3000</b> в браузере.
             </span>`
          : `Ошибка загрузки базы данных db.json. Убедитесь, что SaytEW.py уже сгенерировал и загрузил его в репозиторий.`;

        cardsGrid.innerHTML = `
          <div class="loading-state-container" style="grid-column: 1 / -1; color: var(--danger-color); text-align: center; padding: 24px;">
            <i class="fa-solid fa-triangle-exclamation" style="font-size: 32px; margin-bottom: 12px;"></i>
            <p style="margin: 0;">${errorMsg}</p>
          </div>
        `;
      }
    }
  }

  function calculateGrowth(history, field = 'total_coins_spent') {
    const result = {
      day: { diff: 0, pct: 0 },
      week: { diff: 0, pct: 0 },
      month: { diff: 0, pct: 0 }
    };

    if (!history || history.length === 0) return result;

    const latest = history[history.length - 1];
    const latestVal = latest[field] || 0;
    const now = new Date(latest.timestamp);

    const findValDaysAgo = (days) => {
      const targetDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
      let bestMatch = null;
      let minDiff = Infinity;

      for (const entry of history) {
        const entryDate = new Date(entry.timestamp);
        const diff = Math.abs(entryDate.getTime() - targetDate.getTime());
        if (diff < minDiff) {
          minDiff = diff;
          bestMatch = entry;
        }
      }

      const hoursDiff = minDiff / (1000 * 60 * 60);
      const maxAllowedHours = days === 1 ? 24 : days * 24 * 0.5;
      if (hoursDiff <= maxAllowedHours && bestMatch) {
        return bestMatch[field] || 0;
      }
      return null;
    };

    const val1d = findValDaysAgo(1);
    if (val1d !== null) {
      result.day.diff = latestVal - val1d;
      result.day.pct = val1d > 0 ? parseFloat(((result.day.diff / val1d) * 100).toFixed(2)) : 0;
    } else if (history.length > 1) {
      const prev = history[history.length - 2];
      const prevVal = prev[field] || 0;
      result.day.diff = latestVal - prevVal;
      result.day.pct = prevVal > 0 ? parseFloat(((result.day.diff / prevVal) * 100).toFixed(2)) : 0;
    }

    const getMondayOfDate = (d) => {
      const day = d.getDay();
      const diff = d.getDate() - day + (day === 0 ? -6 : 1);
      const monday = new Date(d.getTime());
      monday.setDate(diff);
      monday.setHours(0, 0, 0, 0);
      return monday;
    };

    const latestDate = new Date(latest.timestamp);
    const mondayDate = getMondayOfDate(latestDate);

    let mondayVal = null;
    let minDiff = Infinity;
    for (const entry of history) {
      const entryDate = new Date(entry.timestamp);
      const diff = Math.abs(entryDate.getTime() - mondayDate.getTime());
      if (diff < minDiff) {
        minDiff = diff;
        mondayVal = entry[field] || 0;
      }
    }

    if (mondayVal === null && history.length > 0) {
      mondayVal = history[0][field] || 0;
    }

    result.week.diff = latestVal - (mondayVal || 0);
    result.week.pct = mondayVal > 0 ? parseFloat(((result.week.diff / mondayVal) * 100).toFixed(2)) : 0;

    const val30d = findValDaysAgo(30);
    if (val30d !== null) {
      result.month.diff = latestVal - val30d;
      result.month.pct = val30d > 0 ? parseFloat(((result.month.diff / val30d) * 100).toFixed(2)) : 0;
    } else if (history.length > 0) {
      const oldestVal = history[0][field] || 0;
      const daysStored = (now - new Date(history[0].timestamp)) / (1000 * 60 * 60 * 24);
      if (daysStored >= 15) {
        result.month.diff = latestVal - oldestVal;
        result.month.pct = oldestVal > 0 ? parseFloat(((result.month.diff / oldestVal) * 100).toFixed(2)) : 0;
      }
    }

    return result;
  }

  function updateOverviewStats() {
    const tab8Section = getSection();
    if (allGuilds.length === 0) return;

    // Top Guild
    const topGuild = [...allGuilds].sort((a, b) => a.rank - b.rank)[0];
    const topGuildNameEl = tab8Section.querySelector('#top-guild-name');
    if (topGuildNameEl) {
      topGuildNameEl.textContent = topGuild ? topGuild.name : '-';
    }

    // Total coins spent
    const totalCoins = allGuilds.reduce((sum, g) => sum + (g.total_coins_spent || 0), 0);
    const totalCoinsEl = tab8Section.querySelector('#total-coins-all');
    if (totalCoinsEl) {
      totalCoinsEl.textContent = formatShortNum(totalCoins);
    }

    // Total members
    const totalMembers = allGuilds.reduce((sum, g) => sum + (g.members_count || 0), 0);
    const totalMembersEl = tab8Section.querySelector('#total-members-all');
    if (totalMembersEl) {
      totalMembersEl.textContent = `${totalMembers} чел.`;
    }

    // Daily growth
    const dailyGrowth = allGuilds.reduce((sum, g) => sum + (g.changes?.day?.diff || 0), 0);
    const dailyGrowthEl = tab8Section.querySelector('#daily-growth-all');
    if (dailyGrowthEl) {
      dailyGrowthEl.textContent = `+${formatShortNum(dailyGrowth)}`;
    }
  }

  function renderGuildsGrid() {
    const tab8Section = getSection();

    const container = tab8Section.querySelector('#guilds-cards-container');
    if (!container) return;

    container.innerHTML = '';

    const sortBy = tab8Section.querySelector('#sort-guilds')?.value || 'rank';
    const sorted = [...allGuilds];

    if (sortBy === 'rank') {
      sorted.sort((a, b) => a.rank - b.rank);
    } else if (sortBy === 'coins') {
      sorted.sort((a, b) => b.total_coins_spent - a.total_coins_spent);

    } else if (sortBy === 'members') {
      sorted.sort((a, b) => b.members_count - a.members_count);
    } else if (sortBy === 'growth') {
      sorted.sort((a, b) => b.changes.day.diff - a.changes.day.diff);
    }

    if (sorted.length === 0) {
      container.innerHTML = '<div class="loading-state-container" style="grid-column:1/-1;"><p>Список гильдий пуст</p></div>';
      return;
    }

    sorted.forEach(guild => {
      const growthDiff = guild.changes?.day?.diff || 0;
      const growthPct = guild.changes?.day?.pct || 0;

      let growthBadgeHtml = `<span class="growth-badge neutral">0</span>`;
      if (growthDiff > 0) {
        growthBadgeHtml = `<span class="growth-badge positive">+${formatShortNum(growthDiff)} (+${growthPct}%)</span>`;
      } else if (growthDiff < 0) {
        growthBadgeHtml = `<span class="growth-badge negative">${formatShortNum(growthDiff)} (${growthPct}%)</span>`;
      }

      const card = document.createElement('div');
      card.className = 'guild-card glass-panel';
      card.innerHTML = `
        <div class="guild-card-header">
          ${getAvatarHtml(guild.avatar, 'guild-card-avatar')}
          <div class="guild-card-title-block">
            <h2 class="guild-card-name" title="${guild.name}">${guild.name}</h2>
            <div class="guild-card-rank-lvl">
              <span>Ранг #${guild.rank}</span>
              <span class="guild-card-lvl-badge">Ур. ${guild.cur_level}</span>
            </div>
          </div>
          <label class="compare-checkbox-container" title="Добавить к сравнению">
            <input type="checkbox" class="compare-checkbox" data-dir="${guild.dir}" ${selectedCompareDirs.has(guild.dir) ? 'checked' : ''}>
            <i class="fa-solid fa-code-compare"></i>
          </label>
        </div>

        <div class="guild-card-stats">
          <div class="card-stat-item">
            <span class="card-stat-label">Всего вкладов</span>
            <span class="card-stat-val text-glow-orange">${formatNum(guild.total_coins_spent)}</span>
          </div>
          <div class="card-stat-item">
            <span class="card-stat-label">Участники</span>
            <span class="card-stat-val">${guild.members_count} / 200</span>
          </div>
        </div>

        <div class="guild-card-growth">
          <span style="color: var(--color-text-dim);">Рост за 24ч:</span>
          ${growthBadgeHtml}
        </div>
      `;

      card.addEventListener('click', (e) => {
        if (e.target.closest('.compare-checkbox-container')) return;
        showGuildDetail(guild.dir);
      });

      const checkbox = card.querySelector('.compare-checkbox');
      checkbox.addEventListener('change', (e) => {
        const dir = e.target.getAttribute('data-dir');
        if (e.target.checked) {
          selectedCompareDirs.add(dir);
        } else {
          selectedCompareDirs.delete(dir);
        }
        updateCompareBadge();
      });

      container.appendChild(card);
    });

    // Update search filtering on redraw
    const searchVal = tab8Section.querySelector('#global-search')?.value.toLowerCase().trim() || '';
    if (searchVal) filterGuildsGrid(searchVal);
  }

  function filterGuildsGrid(query) {
    const tab8Section = getSection();

    tab8Section.querySelectorAll('.guild-card').forEach(card => {
      const name = card.querySelector('.guild-card-name').textContent.toLowerCase();
      card.style.display = name.includes(query) ? 'flex' : 'none';
    });
  }

  function updateCompareBadge() {
    const tab8Section = getSection();

    const badge = tab8Section.querySelector('#compare-count');
    if (badge) {
      badge.textContent = selectedCompareDirs.size;
      badge.style.display = selectedCompareDirs.size > 0 ? 'inline-block' : 'none';
    }
  }

  // --- DETAIL VIEW ---
  function showGuildDetail(dir) {
    const tab8Section = getSection();
    if (!dbCachedData) return;

    const guild = dbCachedData.guilds[dir];
    if (!guild) return;

    currentGuildDetail = guild;
    showTab('guild-detail');

    // Fill textual properties
    tab8Section.querySelector('#guild-detail-name').textContent = guild.name;
    tab8Section.querySelector('#guild-detail-rank').textContent = `Ранг #${guild.rank}`;
    const descElement = tab8Section.querySelector('#guild-detail-desc');
    if (descElement) {
      const cleanDesc = stripHtml(guild.description || 'Описание отсутствует.').trim();
      const maxLen = 120;
      if (cleanDesc.length > maxLen) {
        const shortDesc = cleanDesc.substring(0, maxLen) + '...';
        descElement.innerHTML = `
          <span class="desc-text">${shortDesc}</span>
          <button class="btn-more" style="background: none; border: none; color: var(--accent-color); font-weight: 700; cursor: pointer; padding: 0 4px; font-size: 11px; text-decoration: underline; display: inline-block;">Далее</button>
        `;
        const btnMore = descElement.querySelector('.btn-more');
        btnMore.addEventListener('click', (e) => {
          e.stopPropagation();
          const textSpan = descElement.querySelector('.desc-text');
          if (btnMore.textContent === 'Далее') {
            textSpan.textContent = cleanDesc;
            btnMore.textContent = 'Скрыть';
          } else {
            textSpan.textContent = shortDesc;
            btnMore.textContent = 'Далее';
          }
        });
      } else {
        descElement.textContent = cleanDesc;
      }
    }
    tab8Section.querySelector('#gd-level').textContent = guild.cur_level;
    tab8Section.querySelector('#gd-members').textContent = `${guild.members_count} / 200`;
    tab8Section.querySelector('#gd-coins').textContent = formatNum(guild.total_coins_spent);
    tab8Section.querySelector('#gd-upgrade-points').textContent = guild.upgrade_points || 0;
    tab8Section.querySelector('#gd-regression').textContent = guild.regression ? `Уровень ${guild.regression.level || 1}` : 'Нет';

    const levelExpMax = 1000000;
    const expPercent = Math.min((guild.exp / levelExpMax) * 100, 100);
    tab8Section.querySelector('#gd-level-progress').style.width = `${expPercent}%`;

    // Avatar and Wallpaper hero background
    const avatarContainer = tab8Section.querySelector('#guild-detail-avatar-container');
    if (avatarContainer) {
      avatarContainer.innerHTML = getAvatarHtml(guild.avatar, 'guild-hero-avatar', '');
    }
    const heroBg = tab8Section.querySelector('#guild-hero-bg');
    if (heroBg) {
      if (guild.wallpaper && (guild.wallpaper.high || guild.wallpaper.mid)) {
        heroBg.style.backgroundImage = `url("${getAvatarUrl(guild.wallpaper)}")`;
      } else {
        heroBg.style.backgroundImage = 'linear-gradient(135deg, #1e1b4b 0%, #311042 100%)';
      }
    }

    // Detail growth deltas
    const changes = calculateGrowth(guild.history);
    changes.day = {
      diff: guild.today_growth || 0,
      pct: guild.total_coins_spent > 0 ? parseFloat((((guild.today_growth || 0) / Math.max(1, guild.total_coins_spent - (guild.today_growth || 0))) * 100).toFixed(2)) : 0
    };

    const renderItem = (elemId, change) => {
      const el = tab8Section.querySelector(elemId);
      if (!el) return;
      const diff = change?.diff || 0;
      const pct = change?.pct || 0;
      if (diff > 0) {
        el.className = 'g-det-val positive';
        el.innerHTML = `+${formatShortNum(diff)} <span class="pct">(+${pct}%)</span>`;
      } else if (diff < 0) {
        el.className = 'g-det-val negative';
        el.innerHTML = `${formatShortNum(diff)} <span class="pct">(${pct}%)</span>`;
      } else {
        el.className = 'g-det-val';
        el.innerHTML = `0 <span class="pct">(0%)</span>`;
      }
    };
    renderItem('#gd-growth-day', changes.day);
    renderItem('#gd-growth-week', changes.week);
    renderItem('#gd-growth-month', changes.month);

    // Predictive analytics: calculate dynamically based on history
    let avgDailyGrowth = 0;
    if (guild.history && guild.history.length > 1) {
      const latestEntry = guild.history[guild.history.length - 1];
      const oldestEntry = guild.history[0];
      const latestVal = latestEntry.total_coins_spent || 0;
      const oldestVal = oldestEntry.total_coins_spent || 0;
      const daysDiff = (new Date(latestEntry.timestamp) - new Date(oldestEntry.timestamp)) / (1000 * 60 * 60 * 24);
      if (daysDiff > 0.5) {
        avgDailyGrowth = (latestVal - oldestVal) / daysDiff;
      }
    } else {
      avgDailyGrowth = guild.today_growth || 0;
    }

    if (avgDailyGrowth < 0) avgDailyGrowth = 0;

    // Calculate elapsed time in the current week to project Sunday forecast
    let weekForecast = 0;
    if (guild.history && guild.history.length > 1) {
      const latestEntry = guild.history[guild.history.length - 1];
      const latestDate = new Date(latestEntry.timestamp);
      const getMondayOfDate = (d) => {
        const day = d.getDay();
        const diff = d.getDate() - day + (day === 0 ? -6 : 1);
        const monday = new Date(d.getTime());
        monday.setDate(diff);
        monday.setHours(0, 0, 0, 0);
        return monday;
      };
      const mondayDate = getMondayOfDate(latestDate);
      const timeElapsed = latestDate.getTime() - mondayDate.getTime();
      const daysElapsed = Math.max(0.1, timeElapsed / (1000 * 60 * 60 * 24));
      
      const weekGrowth = changes.week.diff;
      if (daysElapsed >= 0.5 && weekGrowth > 0) {
        weekForecast = Math.round((weekGrowth / daysElapsed) * 7);
      } else {
        weekForecast = Math.round(avgDailyGrowth * 7);
      }
    } else {
      weekForecast = Math.round(avgDailyGrowth * 7);
    }

    const monthForecast = Math.round(avgDailyGrowth * 30);

    const weekEl = tab8Section.querySelector('#gd-forecast-week');
    if (weekEl) {
      weekEl.textContent = weekForecast > 0 ? `+${formatNum(weekForecast)}` : '0';
      weekEl.className = weekForecast > 0 ? 'forecast-val positive' : 'forecast-val';
    }

    const monthEl = tab8Section.querySelector('#gd-forecast-month');
    if (monthEl) {
      monthEl.textContent = monthForecast > 0 ? `+${formatNum(monthForecast)}` : '0';
      monthEl.className = monthForecast > 0 ? 'forecast-val positive' : 'forecast-val';
    }

    // Render activity
    renderActivityTimeline(guild.activity_log || []);

    // Render members
    const membersList = Object.values(guild.members || {}).map(m => {
      const memChanges = calculateGrowth(m.history, 'coins_spent');
      memChanges.day = {
        diff: m.today_contribution || 0,
        pct: 0
      };
      return {
        ...m,
        changes: memChanges
      };
    });
    membersList.sort((a, b) => b.coins_spent - a.coins_spent);
    renderMembersTable(membersList);

    // Draw growth line chart
    drawGuildGrowthChart(guild.history || []);
  }

  function renderActivityTimeline(log) {
    const tab8Section = getSection();

    const container = tab8Section.querySelector('#gd-activity-log');
    if (!container) return;

    container.innerHTML = '';

    if (!log || log.length === 0) {
      container.innerHTML = '<p class="empty-state">Нет записанной активности</p>';
      return;
    }

    const sortedLog = [...log].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)).slice(0, 100);

    sortedLog.forEach(item => {
      let badge = '';
      let desc = '';
      if (item.type === 'join') {
        badge = '<div class="timeline-badge join"><i class="fa-solid fa-user-plus"></i></div>';
        desc = `Вступил в гильдию с вкладом <span class="hl">${formatNum(item.coins_spent)} молний</span>`;
      } else if (item.type === 'leave') {
        badge = '<div class="timeline-badge leave"><i class="fa-solid fa-user-minus"></i></div>';
        desc = `Покинул гильдию (последний вклад <span class="hl">${formatNum(item.last_coins_spent)} молний</span>)`;
      } else if (item.type === 'contribution') {
        badge = '<div class="timeline-badge contribution"><i class="fa-solid fa-bolt"></i></div>';
        desc = `Внес вклад <span class="hl text-glow-orange">+${formatNum(item.coins_added)} молний</span> (всего: ${formatNum(item.total_coins)})`;
      }

      const div = document.createElement('div');
      div.className = 'timeline-item';
      div.innerHTML = `
        ${badge}
        <div class="timeline-content">
          <div class="timeline-user-row">
            ${getAvatarHtml(item.avatar, 'member-avatar', 'width:20px;height:20px;border-radius:50%;')}
            <span>${item.username}</span>
          </div>
          <div class="timeline-details">${desc}</div>
          <div class="timeline-time">${formatDate(item.timestamp)}</div>
        </div>
      `;
      container.appendChild(div);
    });
  }

  function renderMembersTable(members) {
    const tab8Section = getSection();

    tab8Section.querySelector('#gd-members-count').textContent = members.length;
    const tbody = tab8Section.querySelector('#gd-members-tbody');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (!members || members.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" class="align-center">Нет участников в гильдии</td></tr>';
      return;
    }

    members.forEach(m => {
      const roleName = m.role === 'creator' ? 'Основатель' : 'Участник';
      const roleClass = m.role === 'creator' ? 'creator' : 'member';

      const growthDiff = m.changes?.day?.diff || 0;
      let growthHtml = `<span class="color-text-dim">-</span>`;
      if (growthDiff > 0) {
        growthHtml = `<span class="growth-badge positive">+${formatShortNum(growthDiff)}</span>`;
      }

      const tr = document.createElement('tr');
      tr.className = 'member-row';
      tr.innerHTML = `
        <td>
          <div class="member-cell">
            ${getAvatarHtml(m.avatar, 'member-avatar')}
            <div class="member-info">
              <span class="member-name">${m.username}</span>
              <span class="member-tagline" title="${m.tagline || ''}">${m.tagline || ''}</span>
            </div>
          </div>
        </td>
        <td>
          <span class="role-badge ${roleClass}">${roleName}</span>
          ${m.rank ? `<span class="rank-text">${m.rank.rank_name}</span>` : ''}
        </td>
        <td class="align-right coins-val">${formatNum(m.coins_spent)}</td>
        <td class="align-right">${growthHtml}</td>
      `;
      tbody.appendChild(tr);
    });

    const searchVal = tab8Section.querySelector('#member-search')?.value.toLowerCase().trim() || '';
    if (searchVal) filterMembersTable(searchVal);
  }

  function filterMembersTable(query) {
    const tab8Section = getSection();

    tab8Section.querySelectorAll('.member-row').forEach(row => {
      const name = row.querySelector('.member-name').textContent.toLowerCase();
      const role = row.querySelector('.role-badge').textContent.toLowerCase();
      const rank = row.querySelector('.rank-text')?.textContent.toLowerCase() || '';
      row.style.display = (name.includes(query) || role.includes(query) || rank.includes(query)) ? '' : 'none';
    });
  }

  function drawGuildGrowthChart(history) {
    if (charts['guildGrowth']) {
      charts['guildGrowth'].destroy();
    }

    const ctx = document.getElementById('guild-growth-chart').getContext('2d');

    if (!history || history.length === 0) {
      ctx.font = '13px Inter';
      ctx.fillStyle = '#718096';
      ctx.textAlign = 'center';
      ctx.fillText('Недостаточно данных для графика', ctx.canvas.width / 2, ctx.canvas.height / 2);
      return;
    }

    const sortedHist = [...history].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    const labels = sortedHist.map(h => {
      const d = new Date(h.timestamp);
      return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', timeZone: 'Europe/Moscow' });
    });
    const data = sortedHist.map(h => h.total_coins_spent);

    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
    gradient.addColorStop(0, 'rgba(0, 111, 238, 0.35)');
    gradient.addColorStop(1, 'rgba(0, 111, 238, 0.0)');

    charts['guildGrowth'] = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Молний всего',
          data,
          borderColor: '#006fee',
          borderWidth: 2,
          pointBackgroundColor: '#006fee',
          pointRadius: 4,
          fill: true,
          backgroundColor: gradient,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: {
              color: '#a1a1aa',
              font: { family: 'Inter', size: 10 },
              callback: (val) => formatShortNum(val)
            }
          },
          x: {
            grid: { display: false },
            ticks: {
              color: '#a1a1aa',
              font: { family: 'Inter', size: 10 }
            }
          }
        }
      }
    });
  }

  // --- COMPARE VIEW ---
  function renderCompareView() {
    const tab8Section = getSection();
    if (!dbCachedData) return;

    const container = tab8Section.querySelector('#compare-content-area');
    if (!container) return;

    if (selectedCompareDirs.size === 0) {
      container.innerHTML = `
        <div class="empty-state-large" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 64px 0; color: var(--text-muted); gap: 12px;">
          <i class="fa-solid fa-code-compare empty-icon" style="font-size: 32px; color: var(--primary-color);"></i>
          <h3 style="font-size: 18px; font-weight: 700; margin: 0; color: var(--text-light);">Не выбраны гильдии для сравнения</h3>
          <p style="margin: 0; font-size: 13px;">Вернитесь на вкладку Топ 30 и выберите хотя бы 2 гильдии для проведения сравнительного анализа.</p>
          <button class="btn btn-primary" onclick="window.showTab8SubView('dashboard')" style="padding: 8px 16px; border-radius: 6px; font-weight: 600; border: none; background: var(--primary-color); color: #fff; cursor: pointer; margin-top: 8px;">Выбрать гильдии</button>
        </div>
      `;
      return;
    }

    const dirs = Array.from(selectedCompareDirs);
    const compareData = dirs.map(dir => {
      const guild = dbCachedData.guilds[dir];
      if (!guild) return null;

      const changes = calculateGrowth(guild.history);
      changes.day = {
        diff: guild.today_growth || 0,
        pct: guild.total_coins_spent > 0 ? parseFloat((((guild.today_growth || 0) / Math.max(1, guild.total_coins_spent - (guild.today_growth || 0))) * 100).toFixed(2)) : 0
      };

      const members = Object.values(guild.members || {});
      const avgCoinsSpent = members.length > 0 ? Math.round(guild.total_coins_spent / members.length) : 0;
      const sortedMembers = [...members].sort((a, b) => b.coins_spent - a.coins_spent);
      const topContributor = sortedMembers[0] ? { username: sortedMembers[0].username, coins_spent: sortedMembers[0].coins_spent } : null;

      return {
        name: guild.name,
        dir: guild.dir,
        avatar: guild.avatar,
        cur_level: guild.cur_level,
        exp: guild.exp,
        members_count: guild.members_count,
        rank: guild.rank,
        total_coins_spent: guild.total_coins_spent,
        avg_coins_spent: avgCoinsSpent,
        top_contributor: topContributor,
        changes,
        history: guild.history
      };
    }).filter(Boolean);

    compareData.sort((a, b) => a.rank - b.rank);

    let cardsHtml = '';
    compareData.forEach(guild => {
      const growthDiff = guild.changes?.day?.diff || 0;
      const growthPct = guild.changes?.day?.pct || 0;

      let growthBadge = `<span class="growth-badge neutral">0</span>`;
      if (growthDiff > 0) {
        growthBadge = `<span class="growth-badge positive">+${formatShortNum(growthDiff)} (+${growthPct}%)</span>`;
      } else if (growthDiff < 0) {
        growthBadge = `<span class="growth-badge negative">${formatShortNum(growthDiff)} (${growthPct}%)</span>`;
      }

      cardsHtml += `
        <div class="compare-card-column glass-panel">
          <div class="guild-card-header" style="border-bottom: 1px solid var(--panel-border); padding-bottom: 12px; margin-bottom: 12px;">
            ${getAvatarHtml(guild.avatar, 'guild-card-avatar', 'width: 44px; height: 44px; border-radius: 12px;')}
            <div class="guild-card-title-block">
              <div class="guild-card-name" style="font-size: 15px;">${guild.name}</div>
              <div class="guild-card-rank-lvl" style="font-size: 11px;">Ранг #${guild.rank}</div>
            </div>
          </div>
          
          <div class="compare-metric-row">
            <span class="metric-label">Уровень</span>
            <span class="metric-val" style="color: var(--accent-color)">Ур. ${guild.cur_level}</span>
          </div>
          <div class="compare-metric-row">
            <span class="metric-label">Всего вкладов</span>
            <span class="metric-val">${formatNum(guild.total_coins_spent)} молний</span>
          </div>
          <div class="compare-metric-row">
            <span class="metric-label">Участников</span>
            <span class="metric-val">${guild.members_count} / 200</span>
          </div>
          <div class="compare-metric-row">
            <span class="metric-label">Ср. вклад участника</span>
            <span class="metric-val">${formatNum(guild.avg_coins_spent)} молний</span>
          </div>
          <div class="compare-metric-row">
            <span class="metric-label">Топ Донатер</span>
            <span class="metric-val" title="${guild.top_contributor?.username || ''}">${guild.top_contributor ? `${guild.top_contributor.username} (${formatShortNum(guild.top_contributor.coins_spent)})` : '-'}</span>
          </div>
          <div class="compare-metric-row">
            <span class="metric-label">Рост за сутки</span>
            <span class="metric-val">${growthBadge}</span>
          </div>
        </div>
      `;
    });

    container.innerHTML = `
      <div class="compare-grid">
        <div class="compare-cards-row">
          ${cardsHtml}
        </div>
        
        <div class="glass-panel chart-panel">
          <h3 class="panel-title"><i class="fa-solid fa-chart-line" style="color: var(--primary-color);"></i> Сравнение динамики роста вкладов</h3>
          <div class="chart-container" style="height: 320px;">
            <canvas id="compare-growth-chart"></canvas>
          </div>
        </div>
      </div>
    `;

    drawCompareGrowthChart(compareData);
  }

  function drawCompareGrowthChart(compareData) {
    if (charts['compareGrowth']) {
      charts['compareGrowth'].destroy();
    }

    const ctx = document.getElementById('compare-growth-chart').getContext('2d');

    const allTimestampsSet = new Set();
    compareData.forEach(guild => {
      if (guild.history) {
        guild.history.forEach(h => {
          allTimestampsSet.add(h.timestamp.substring(0, 10));
        });
      }
    });

    const sortedDates = Array.from(allTimestampsSet).sort();
    const labels = sortedDates.map(dateStr => {
      const d = new Date(dateStr);
      return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', timeZone: 'Europe/Moscow' });
    });

    const colors = [
      '#e84a5f',
      '#ffd369',
      '#006fee',
      '#2ec4b6',
      '#ec4899',
      '#ef4444',
      '#14b8a6'
    ];

    const datasets = compareData.map((guild, idx) => {
      const color = colors[idx % colors.length];
      
      const data = sortedDates.map(dateStr => {
        const match = guild.history?.find(h => h.timestamp.startsWith(dateStr));
        return match ? match.total_coins_spent : null;
      });

      return {
        label: guild.name,
        data,
        borderColor: color,
        borderWidth: 2,
        pointBackgroundColor: color,
        pointRadius: 4,
        fill: false,
        tension: 0.3
      };
    });

    charts['compareGrowth'] = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: '#ffffff',
              font: { family: 'Inter', size: 11, weight: '500' }
            }
          }
        },
        scales: {
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: {
              color: '#a1a1aa',
              font: { family: 'Inter', size: 10 },
              callback: (val) => formatShortNum(val)
            }
          },
          x: {
            grid: { display: false },
            ticks: {
              color: '#a1a1aa',
              font: { family: 'Inter', size: 10 }
            }
          }
        }
      }
    });
  }

  // --- SUB TAB SWITCHER ---
  function showTab(tabId) {
    const tab8Section = document.getElementById('tab8');
    if (!tab8Section) return;

    tab8Section.querySelectorAll('.tab-view').forEach(view => {
      view.classList.remove('active');
      view.style.display = 'none';
    });

    tab8Section.querySelectorAll('.nav-item').forEach(item => {
      item.classList.remove('active');
      if (item.getAttribute('data-tab') === tabId) {
        item.classList.add('active');
      }
    });

    const activeView = tab8Section.querySelector('#view-' + tabId);
    if (activeView) {
      activeView.classList.add('active');
      activeView.style.display = 'flex';
    }

    if (tabId === 'dashboard') {
      currentGuildDetail = null;
    } else if (tabId === 'compare') {
      renderCompareView();
    }
  }

  // Expose tab switcher to global window space for the compare button callback
  window.showTab8SubView = showTab;

  // Initialize once DOM is ready or run immediately if already loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
  } else {
    initDashboard();
  }
})();
