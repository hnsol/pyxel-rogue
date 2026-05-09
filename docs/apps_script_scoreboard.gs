const SHEET_NAME = "scores";
const USER_SHEET_NAME = "users";
const GUEST_METRICS_SHEET_NAME = "guest_metrics";
const DUMMY_TARGET_COUNT = 10;
const DUMMY_PAST_WEEKS = 10;
const DUMMY_BACKFILL_COUNT = 1;
const USER_NAME_MAX = 8;
const SYNC_COOLDOWN_HOURS = 24;
const USER_PASSWORD_FAIL_LIMIT = 5;
const USER_PASSWORD_LOCK_MINUTES = 10;
const DUMMY_NAMES = [
  "rodney",
  "yendor",
  "wizrodny",
  "amuletyn",
  "hjkluser",
  "level26",
  "chmod777",
  "deadbeef",
  "sigsegv",
  "nullptr",
  "root",
  "sudo",
  "binsh",
  "devnull",
  "tarball",
  "pdp11",
  "vax1178",
  "vt100",
  "bsd43",
  "v7unix",
  "kentomp",
  "dmr",
  "bjoy",
  "wichman",
  "kenarnld",
  "kestrel",
  "griffon",
  "jabberwk",
  "dragon",
  "gridbug",
  "rnggod",
  "rnghater",
  "permadth",
  "foodless",
  "speedrun",
  "savesc",
  "lvl26f",
  "ripper",
  "retry",
  "gameover",
  "malloc",
  "free",
  "stackovf",
  "bitshift",
  "xor",
  "goto10",
  "exit0",
  "stdout",
  "stdin",
  "stderr",
  "ascii",
  "hexdump",
  "binary",
  "byte",
  "opcode",
  "tty0",
  "ansi80",
  "crlf",
  "eof",
  "sof",
  "pyxeldev",
  "8bitluv",
  "pixelart",
  "sprite",
  "palette",
  "x86",
  "z80a",
  "6502",
  "motorola",
  "c64",
  "pascal",
  "fortran",
  "cobol",
  "algol",
  "blang",
  "lobolto",
  "umoria",
  "nethack",
  "angband",
  "dungeon",
  "xyzzy",
  "plugh",
  "frob",
  "foobar",
  "bazqux",
  "str0",
  "char1",
  "void",
  "const",
  "static",
  "volatile",
  "register",
  "struct",
  "union",
  "typedef",
  "maxint",
  "minint",
  "id001",
  "user99",
  "guest",
];

function doGet(e) {
  if ((e.parameter.action || "") === "seedDummy")
    return json({ rows: seedDummy() });
  if ((e.parameter.action || "") === "rank")
    return json({ rank: scoreRank(e.parameter) });
  const period = (e.parameter.period || "weekly").toLowerCase();
  const key = e.parameter.key || currentPeriods()[periodField(period)];
  const ctx = scoreContext();
  if (period === "weekly") {
    ensureDummyRows(period, key, DUMMY_TARGET_COUNT, ctx);
  }
  if (period === "season") {
    ensureDummyRows("weekly", currentPeriods().period_week, DUMMY_TARGET_COUNT, ctx);
    ensureHistoricalWeeklyRows(new Date(), key, ctx);
  }
  flushScoreRows(ctx);
  return json({ scores: topScores(period, key, ctx) });
}

function doPost(e) {
  const body = JSON.parse(e.postData.contents || "{}");
  if (body.action === "seedDummy") return json({ rows: seedDummy() });
  if (body.action === "checkUser") return json(checkUser(body));
  if (body.action === "registerUser") return json(registerUser(body));
  if (body.action === "linkUser") return json(linkUser(body));
  if (body.action === "syncScoreboard") return json(syncScoreboard(body));
  if (body.action === "guestScoreboardSync") return json(recordGuestScoreboardSync());
  if (body.action === "submit") {
    appendScore(body.entry || {});
    return json({ ok: true });
  }
  return json({ ok: false });
}

function userSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(USER_SHEET_NAME);
  if (!sh) sh = ss.insertSheet(USER_SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.appendRow([
      "user_name",
      "user_password",
      "server_token",
      "last_sync_at",
      "failed_attempts",
      "locked_until",
      "created_at",
    ]);
  }
  sh.getRange(1, 2, Math.max(1, sh.getMaxRows()), 1).setNumberFormat("@");
  return sh;
}

function guestMetricsSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(GUEST_METRICS_SHEET_NAME);
  if (!sh) sh = ss.insertSheet(GUEST_METRICS_SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.appendRow(["timestamp", "event"]);
  }
  return sh;
}

function recordGuestScoreboardSync() {
  guestMetricsSheet().appendRow([new Date().toISOString(), "scoreboard_sync"]);
  return { ok: true };
}

function userIndex(data) {
  const header = data[0];
  return Object.fromEntries(header.map((h, i) => [h, i]));
}

function findUser(userId) {
  const clean = cleanUserId(userId);
  const sh = userSheet();
  const data = sh.getDataRange().getValues();
  const idx = userIndex(data);
  for (let r = 1; r < data.length; r++) {
    if (String(data[r][idx.user_name]) === clean) {
      return { sheet: sh, row: r + 1, values: data[r], idx: idx };
    }
  }
  return null;
}

function checkUser(body) {
  const userName = cleanUserId(body.user_name);
  if (isReservedUserId(userName)) return { ok: true, exists: true, reserved: true };
  return { ok: true, exists: Boolean(findUser(userName)), reserved: false };
}

function registerUser(body) {
  const userId = cleanUserId(body.user_name);
  const password = cleanUserPassword(body.user_password);
  if (isReservedUserId(userId)) return { ok: false, status: "reserved" };
  if (!password) return { ok: false, status: "bad_password" };
  if (findUser(userId)) return { ok: false, status: "exists" };
  const token = makeServerToken();
  const sh = userSheet();
  sh.appendRow([
    userId,
    password,
    token,
    "",
    0,
    "",
    new Date().toISOString(),
  ]);
  sh.getRange(sh.getLastRow(), 2).setNumberFormat("@").setValue(password);
  return {
    ok: true,
    status: "registered",
    user_name: userId,
    server_token: token,
    last_sync_at: "",
    next_sync_at: "",
  };
}

function linkUser(body) {
  const user = findUser(body.user_name);
  const password = cleanUserPassword(body.user_password);
  if (!user || !password) return { ok: false, status: "auth_failed" };
  const lockedUntil = user.values[user.idx.locked_until];
  if (lockedUntil && new Date(lockedUntil).getTime() > Date.now()) {
    return { ok: false, status: "locked", locked_until: new Date(lockedUntil).toISOString() };
  }
  if (storedUserPassword(user.values[user.idx.user_password]) !== password) {
    const failures = parseInt(user.values[user.idx.failed_attempts] || 0, 10) + 1;
    user.sheet.getRange(user.row, user.idx.failed_attempts + 1).setValue(failures);
    if (failures >= USER_PASSWORD_FAIL_LIMIT) {
      const locked = new Date(Date.now() + USER_PASSWORD_LOCK_MINUTES * 60 * 1000);
      user.sheet.getRange(user.row, user.idx.locked_until + 1).setValue(locked.toISOString());
      return { ok: false, status: "locked", locked_until: locked.toISOString() };
    }
    return { ok: false, status: "auth_failed" };
  }
  user.sheet.getRange(user.row, user.idx.failed_attempts + 1).setValue(0);
  user.sheet.getRange(user.row, user.idx.locked_until + 1).setValue("");
  return {
    ok: true,
    status: "linked",
    user_name: String(user.values[user.idx.user_name]),
    server_token: String(user.values[user.idx.server_token]),
    last_sync_at: String(user.values[user.idx.last_sync_at] || ""),
    next_sync_at: nextSyncAt(user.values[user.idx.last_sync_at]),
  };
}

function syncScoreboard(body) {
  const user = findUser(body.user_name);
  if (!user || String(user.values[user.idx.server_token]) !== String(body.server_token || "")) {
    return { ok: false, status: "auth_failed" };
  }
  const userName = String(user.values[user.idx.user_name]);
  const entries = Array.isArray(body.entries) ? body.entries : [];
  const last = String(user.values[user.idx.last_sync_at] || "");
  const next = nextSyncAt(last);
  const firstScorePost = entries.length > 0 && !hasUserScore(userName);
  if (next && new Date(next).getTime() > Date.now() && !firstScorePost) {
    return {
      ok: false,
      status: "cooldown",
      last_sync_at: last,
      next_sync_at: next,
    };
  }
  if (entries.length === 0 && !last) {
    return {
      ok: true,
      status: "success",
      posted_count: 0,
      last_sync_at: "",
      next_sync_at: "",
    };
  }
  let posted = 0;
  entries.forEach((entry) => appendScore(Object.assign({}, entry, {
    user_name: userName,
    player_name: userName,
  })) && posted++);
  const now = new Date().toISOString();
  user.sheet.getRange(user.row, user.idx.last_sync_at + 1).setValue(now);
  return {
    ok: true,
    status: "success",
    posted_count: posted,
    last_sync_at: now,
    next_sync_at: nextSyncAt(now),
  };
}

function hasUserScore(userName) {
  const clean = cleanName(userName);
  const data = sheet().getDataRange().getValues();
  const header = data.shift();
  const idx = Object.fromEntries(header.map((h, i) => [h, i]));
  return data.some((row) =>
    cleanName(row[idx.player_name]) === clean && row[idx.is_dummy] !== true
  );
}

function nextSyncAt(lastSyncAt) {
  if (!lastSyncAt) return "";
  const d = new Date(lastSyncAt);
  if (isNaN(d.getTime())) return "";
  return new Date(d.getTime() + SYNC_COOLDOWN_HOURS * 60 * 60 * 1000).toISOString();
}

function makeServerToken() {
  return Utilities.getUuid().replace(/-/g, "") + "-" + Math.floor(Math.random() * 1000000);
}

function sheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) sh = ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.appendRow([
      "timestamp",
      "period_day",
      "period_week",
      "period_season",
      "player_name",
      "score",
      "depth",
      "result_flags",
      "killer",
      "client_build",
      "is_dummy",
      "score_id",
    ]);
  } else {
    ensureScoreIdColumn(sh);
  }
  return sh;
}

function scoreContext() {
  const sh = sheet();
  const data = sh.getDataRange().getValues();
  const header = data.shift();
  return {
    sheet: sh,
    header: header,
    idx: Object.fromEntries(header.map((h, i) => [h, i])),
    rows: data,
    pendingRows: [],
  };
}

function rowsForContext(ctx) {
  return ctx.rows.concat(ctx.pendingRows);
}

function flushScoreRows(ctx) {
  if (!ctx || ctx.pendingRows.length === 0) return 0;
  const rows = ctx.pendingRows;
  ctx.sheet.getRange(ctx.sheet.getLastRow() + 1, 1, rows.length, rows[0].length).setValues(rows);
  ctx.rows = ctx.rows.concat(rows);
  ctx.pendingRows = [];
  return rows.length;
}

function appendScore(entry) {
  const now = entry.timestamp || new Date().toISOString();
  const p = periodsFor(new Date(now));
  const name = cleanName(entry.player_name);
  const scoreId = String(entry.score_id || scoreIdFor(entry, now, name));
  if (scoreIdExists(scoreId)) return false;
  const sh = sheet();
  sh.appendRow([
    now,
    entry.period_day || p.period_day,
    entry.period_week || p.period_week,
    entry.period_season || p.period_season,
    name,
    Math.max(0, parseInt(entry.score || 0, 10)),
    Math.max(0, parseInt(entry.depth || entry.level || 0, 10)),
    String(entry.result_flags || ""),
    String(entry.killer || "").slice(0, 40),
    String(entry.client_build || ""),
    Boolean(entry.is_dummy),
    scoreId,
  ]);
  return true;
}

function ensureScoreIdColumn(sh) {
  const lastCol = sh.getLastColumn();
  const header = sh.getRange(1, 1, 1, lastCol).getValues()[0];
  if (header.indexOf("score_id") === -1) {
    sh.getRange(1, lastCol + 1).setValue("score_id");
  }
}

function scoreIdExists(scoreId) {
  if (!scoreId) return false;
  const sh = sheet();
  const data = sh.getDataRange().getValues();
  const header = data.shift();
  const idx = header.indexOf("score_id");
  if (idx === -1) return false;
  return data.some((row) => String(row[idx] || "") === String(scoreId));
}

function scoreIdFor(entry, timestamp, name) {
  return [
    timestamp,
    name,
    Math.max(0, parseInt(entry.score || 0, 10)),
    Math.max(0, parseInt(entry.depth || entry.level || 0, 10)),
    String(entry.result_flags || ""),
    String(entry.killer || ""),
  ].join("|");
}

function topScores(period, key, ctx) {
  const context = ctx || scoreContext();
  const data = rowsForContext(context);
  const idx = context.idx;
  const field = periodField(period);
  const best = {};
  data.forEach((row) => {
    if (periodCellValue(row[idx[field]], field) !== String(key)) return;
    const name = cleanName(row[idx.player_name]);
    const score = parseInt(row[idx.score] || 0, 10);
    if (!best[name] || score > best[name].score) {
      best[name] = {
        timestamp: row[idx.timestamp],
        period_day: periodCellValue(row[idx.period_day], "period_day"),
        period_week: periodCellValue(row[idx.period_week], "period_week"),
        period_season: periodCellValue(row[idx.period_season], "period_season"),
        player_name: name,
        score: score,
        depth: parseInt(row[idx.depth] || 0, 10),
        result_flags: row[idx.result_flags],
        killer: row[idx.killer],
        client_build: row[idx.client_build],
        is_dummy: row[idx.is_dummy] === true,
        score_id: idx.score_id === undefined ? "" : row[idx.score_id],
      };
    }
  });
  return Object.values(best)
    .sort((a, b) => b.score - a.score)
    .slice(0, 10);
}

function scoreRank(params) {
  const period = (params.period || "weekly").toLowerCase();
  const key = params.key || currentPeriods()[periodField(period)];
  const score = Math.max(0, parseInt(params.score || 0, 10));
  const scores = allScores(period, key);
  let rank = 1;
  scores.forEach((row) => {
    if (row.score > score) rank++;
  });
  return rank;
}

function allScores(period, key, ctx) {
  const context = ctx || scoreContext();
  const data = rowsForContext(context);
  const idx = context.idx;
  const field = periodField(period);
  const best = {};
  data.forEach((row) => {
    if (periodCellValue(row[idx[field]], field) !== String(key)) return;
    const name = cleanName(row[idx.player_name]);
    const score = parseInt(row[idx.score] || 0, 10);
    if (!best[name] || score > best[name].score) {
      best[name] = { player_name: name, score: score };
    }
  });
  return Object.values(best).sort((a, b) => b.score - a.score);
}

function periodCellValue(value, field) {
  if (field === "period_day" && value instanceof Date) {
    return Utilities.formatDate(
      value,
      SpreadsheetApp.getActiveSpreadsheet().getSpreadsheetTimeZone(),
      "yyyy-MM-dd",
    );
  }
  return String(value || "");
}

function seedDummy() {
  const ctx = scoreContext();
  const rows = ensureScoreboardDummyContext(ctx);
  flushScoreRows(ctx);
  return rows;
}

function ensureScoreboardDummyContext(ctx) {
  const now = new Date();
  let rows = 0;
  rows += ensureDummyRows("weekly", currentPeriods().period_week, DUMMY_TARGET_COUNT, ctx);
  rows += ensureHistoricalWeeklyRows(now, currentPeriods().period_season, ctx);
  return rows;
}

function ensureHistoricalWeeklyRows(now, seasonKey, ctx) {
  const base = now || new Date();
  let rows = 0;
  for (let i = 1; i <= DUMMY_PAST_WEEKS; i++) {
    const p = periodsFor(addUtcDays(base, historicalWeeklyDayOffset(i)));
    if (seasonKey && p.period_season !== seasonKey) continue;
    rows += ensureSeededDummyRows(
      "weekly",
      p.period_week,
      DUMMY_BACKFILL_COUNT,
      ctx,
    );
  }
  return rows;
}

function historicalWeeklyDayOffset(i) {
  return -(2 + (i - 1) * 7);
}

function ensureDummyRows(period, key, targetCount, ctx) {
  return ensureDummyRowsForPeriod(period, key, targetCount, false, ctx);
}

function ensureSeededDummyRows(period, key, targetCount, ctx) {
  return ensureDummyRowsForPeriod(period, key, targetCount, true, ctx);
}

function ensureDummyRowsForPeriod(period, key, targetCount, countSeededOnly, ctx) {
  const context = ctx || scoreContext();
  const scores = topScores(period, key, context);
  const used = new Set(scores.map((r) => cleanName(r.player_name)));
  const seeded = seededDummyNames(period, key, context);
  seeded.forEach((name) => used.add(cleanName(name)));
  const visibleOrSeeded = countSeededOnly
    ? seeded.size
    : Math.max(scores.length, seeded.size);
  const needed = Math.max(0, targetCount - visibleOrSeeded);
  if (needed === 0) return 0;
  const offset = dummyNameOffset(period, key);
  let rows = 0;
  for (let i = 0; i < DUMMY_NAMES.length && rows < needed; i++) {
    const name = DUMMY_NAMES[(offset + i) % DUMMY_NAMES.length];
    const clean = cleanName(name);
    if (used.has(clean)) continue;
    const p = periodsFromKey(period, key, i);
    context.pendingRows.push([
      timestampForPeriod(period, key, i),
      p.period_day,
      p.period_week,
      p.period_season,
      clean,
      dummyScore(period, key, i, targetCount),
      dummyDepth(period, key, i),
      "killed",
      dummyKiller(period, key, i),
      "dummy",
      true,
      "dummy-" + period + "-" + key + "-" + clean,
    ]);
    used.add(clean);
    rows++;
  }
  if (!ctx) flushScoreRows(context);
  return rows;
}

function seededDummyNames(period, key, ctx) {
  const context = ctx || scoreContext();
  const data = rowsForContext(context);
  const idx = context.idx;
  const prefix = "dummy-" + period + "-" + key + "-";
  const names = new Set();
  data.forEach((row) => {
    if (String(row[idx.score_id] || "").indexOf(prefix) === 0) {
      names.add(cleanName(row[idx.player_name]));
    }
  });
  return names;
}

function dummyNameOffset(period, key) {
  return hashString(period + ":" + key) % DUMMY_NAMES.length;
}

function dummyValue(period, key, offset, salt, max) {
  return hashString([period, key, offset, salt].join(":")) % max;
}

function dummyScore(period, key, offset, targetCount) {
  const depth = dummyDepth(period, key, offset);
  return depth * 70 + dummyValue(period, key, offset, "score", 351);
}

function dummyDepth(period, key, offset) {
  return 1 + dummyValue(period, key, offset, "depth", 16);
}

function dummyKiller(period, key, offset) {
  const depth = dummyDepth(period, key, offset);
  const killers = dummyKillersForDepth(depth);
  return killers[dummyValue(period, key, offset, "killer", killers.length)];
}

function dummyKillersForDepth(depth) {
  const killersByDepth = [
    ["hobgoblin", "kestrel"],
    ["snake", "bat"],
    ["hobgoblin", "snake"],
    ["rattlesnake", "orc"],
    ["orc", "zombie"],
    ["rattlesnake", "zombie"],
    ["centaur", "quagga"],
    ["quagga", "yeti"],
    ["centaur", "yeti"],
    ["quagga", "yeti"],
    ["venus flytrap", "troll"],
    ["troll", "wraith"],
    ["venus flytrap", "wraith"],
    ["phantom", "vampire"],
    ["vampire", "xeroc"],
    ["phantom", "xeroc"],
  ];
  return killersByDepth[Math.max(1, Math.min(16, depth)) - 1];
}

function hashString(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return h;
}

function periodsFromKey(period, key, offset) {
  if (period === "weekly") {
    const p = periodsFor(dateForIsoWeek(key, offset % 7));
    p.period_week = key;
    return p;
  }
  const p = periodsFor(dateForSeason(key, offset * 7));
  p.period_season = key;
  return p;
}

function periodField(period) {
  if (period === "season") return "period_season";
  return "period_week";
}

function timestampForPeriod(period, key, offset) {
  let d;
  if (period === "weekly") {
    d = dateForIsoWeek(key, offset % 7);
  } else {
    d = dateForSeason(key, offset * 7);
  }
  d.setUTCHours(12, (offset * 17) % 60, 0, 0);
  return d.toISOString();
}

function addUtcDays(d, days) {
  return new Date(
    Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() + days),
  );
}

function dateForIsoWeek(key, dayOffset) {
  const m = String(key).match(/^(\d{4})-W(\d{2})$/);
  const year = m ? parseInt(m[1], 10) : new Date().getUTCFullYear();
  const week = m ? parseInt(m[2], 10) : 1;
  const jan4 = new Date(Date.UTC(year, 0, 4));
  const monday = addUtcDays(jan4, 1 - (jan4.getUTCDay() || 7));
  return addUtcDays(monday, (week - 1) * 7 + dayOffset);
}

function dateForSeason(key, dayOffset) {
  const parts = String(key).split("-");
  const year = parseInt(parts[0], 10) || new Date().getUTCFullYear();
  const season = parts[1] || "Spring";
  const month = { Spring: 2, Summer: 5, Fall: 8, Winter: 11 }[season] || 2;
  const startYear = season === "Winter" ? year - 1 : year;
  return addUtcDays(new Date(Date.UTC(startYear, month, 1)), dayOffset);
}

function currentPeriods() {
  return periodsFor(new Date());
}

function periodsFor(d) {
  const y = d.getUTCFullYear();
  const m = d.getUTCMonth() + 1;
  const seasonYear = m === 12 ? y + 1 : y;
  const day = Utilities.formatDate(d, "UTC", "yyyy-MM-dd");
  return {
    period_day: day,
    period_week: isoWeekKey(d),
    period_season: seasonYear + "-" + seasonName(m),
  };
}

function isoWeekKey(d) {
  const x = new Date(
    Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()),
  );
  x.setUTCDate(x.getUTCDate() + 4 - (x.getUTCDay() || 7));
  const yearStart = new Date(Date.UTC(x.getUTCFullYear(), 0, 1));
  const week = Math.ceil(((x - yearStart) / 86400000 + 1) / 7);
  return x.getUTCFullYear() + "-W" + String(week).padStart(2, "0");
}

function seasonName(month) {
  if (month >= 3 && month <= 5) return "Spring";
  if (month >= 6 && month <= 8) return "Summer";
  if (month >= 9 && month <= 11) return "Fall";
  return "Winter";
}

function cleanName(name) {
  const s = String(name || "rogue54")
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "")
    .trim()
    .slice(0, USER_NAME_MAX);
  return s || "rogue54";
}

function cleanUserId(userId) {
  const id = String(userId || "rogue54")
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "")
    .slice(0, USER_NAME_MAX);
  return id || "rogue54";
}

function cleanDisplayName(displayName) {
  return String(displayName || "rogue54")
    .replace(/[^\x20-\x7e]/g, "")
    .slice(0, USER_NAME_MAX) || "rogue54";
}

function cleanUserPassword(password) {
  const text = String(password || "");
  return /^\d{6}$/.test(text) ? text : "";
}

function storedUserPassword(password) {
  const text = String(password || "");
  return /^\d{1,6}$/.test(text) ? text.padStart(6, "0") : text;
}

function isReservedUserId(userId) {
  const id = cleanUserId(userId);
  if (id === "guest" || id === "rogue54") return true;
  return DUMMY_NAMES.some((name) => cleanUserId(name) === id);
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(
    ContentService.MimeType.JSON,
  );
}
