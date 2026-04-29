const SHEET_NAME = 'scores';
const DUMMY_TARGET_COUNT = 10;
const DUMMY_NAMES = [
  'RODNEY', 'YENDOR', 'WIZRODNY', 'AMULETYN', 'HJKLUSER',
  'LEVEL26', 'CHMOD777', 'DEADBEEF', 'SIGSEGV', 'NULLPTR',
  'ROOT', 'SUDO', 'BINSH', 'DEVNULL', 'TARBALL',
  'PDP11', 'VAX1178', 'VT100', 'BSD43', 'V7UNIX',
  'KENTOMP', 'DMR', 'BJOY', 'WICHMAN', 'KENARNLD',
  'KESTREL', 'GRIFFON', 'JABBERWK', 'DRAGON', 'GRIDBUG',
  'RNGGOD', 'RNGHATER', 'PERMADTH', 'FOODLESS', 'SPEEDRUN',
  'SAVE_SC', 'LVL26F', 'RIPPER', 'RETRY', 'GAMEOVER',
  'MALLOC', 'FREE', 'STACKOVF', 'BITSHIFT', 'XOR',
  'GOTO10', 'EXIT0', 'STDOUT', 'STDIN', 'STDERR',
  'ASCII', 'HEXDUMP', 'BINARY', 'BYTE', 'OPCODE',
  'TTY0', 'ANSI80', 'CRLF', 'EOF', 'SOF',
  'PYXELDEV', '8BITLUV', 'PIXELART', 'SPRITE', 'PALETTE',
  'X86', 'Z80A', '6502', 'MOTOROLA', 'C64',
  'PASCAL', 'FORTRAN', 'COBOL', 'ALGOL', 'B_LANG',
  'LOBOLTO', 'UMORIA', 'NETHACK', 'ANGBAND', 'DUNGEON',
  'XYZZY', 'PLUGH', 'FROB', 'FOOBAR', 'BAZQUX',
  'STR0', 'CHAR1', 'VOID', 'CONST', 'STATIC',
  'VOLATILE', 'REGISTER', 'STRUCT', 'UNION', 'TYPEDEF',
  'MAXINT', 'MININT', 'ID001', 'USER99', 'GUEST'
];

function doGet(e) {
  if ((e.parameter.action || '') === 'seedDummy') return json({ rows: seedDummy() });
  if ((e.parameter.action || '') === 'rank') return json({ rank: scoreRank(e.parameter) });
  const period = (e.parameter.period || 'weekly').toLowerCase();
  const key = e.parameter.key || currentPeriods()[periodField(period)];
  ensureDummyRows(period, key);
  return json({ scores: topScores(period, key) });
}

function doPost(e) {
  const body = JSON.parse(e.postData.contents || '{}');
  if (body.action === 'seedDummy') return json({ rows: seedDummy() });
  if (body.action === 'submit') {
    appendScore(body.entry || {});
    return json({ ok: true });
  }
  return json({ ok: false });
}

function sheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) sh = ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.appendRow(['timestamp','period_day','period_week','period_season','player_name','score','depth','result_flags','killer','client_build','is_dummy','score_id']);
  } else {
    ensureScoreIdColumn(sh);
  }
  return sh;
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
    String(entry.result_flags || ''),
    String(entry.killer || '').slice(0, 40),
    String(entry.client_build || ''),
    Boolean(entry.is_dummy),
    scoreId
  ]);
  return true;
}

function ensureScoreIdColumn(sh) {
  const lastCol = sh.getLastColumn();
  const header = sh.getRange(1, 1, 1, lastCol).getValues()[0];
  if (header.indexOf('score_id') === -1) {
    sh.getRange(1, lastCol + 1).setValue('score_id');
  }
}

function scoreIdExists(scoreId) {
  if (!scoreId) return false;
  const sh = sheet();
  const data = sh.getDataRange().getValues();
  const header = data.shift();
  const idx = header.indexOf('score_id');
  if (idx === -1) return false;
  return data.some(row => String(row[idx] || '') === String(scoreId));
}

function scoreIdFor(entry, timestamp, name) {
  return [
    timestamp,
    name,
    Math.max(0, parseInt(entry.score || 0, 10)),
    Math.max(0, parseInt(entry.depth || entry.level || 0, 10)),
    String(entry.result_flags || ''),
    String(entry.killer || '')
  ].join('|');
}

function topScores(period, key) {
  const data = sheet().getDataRange().getValues();
  const header = data.shift();
  const idx = Object.fromEntries(header.map((h, i) => [h, i]));
  const field = periodField(period);
  const best = {};
  data.forEach(row => {
    if (String(row[idx[field]]) !== String(key)) return;
    const name = cleanName(row[idx.player_name]);
    const score = parseInt(row[idx.score] || 0, 10);
    if (!best[name] || score > best[name].score) {
      best[name] = {
        timestamp: row[idx.timestamp],
        period_week: row[idx.period_week],
        period_season: row[idx.period_season],
        player_name: name,
        score: score,
        depth: parseInt(row[idx.depth] || 0, 10),
        result_flags: row[idx.result_flags],
        killer: row[idx.killer],
        client_build: row[idx.client_build],
        is_dummy: row[idx.is_dummy] === true,
        score_id: idx.score_id === undefined ? '' : row[idx.score_id]
      };
    }
  });
  return Object.values(best).sort((a, b) => b.score - a.score).slice(0, 10);
}

function scoreRank(params) {
  const period = (params.period || 'weekly').toLowerCase();
  const key = params.key || currentPeriods()[periodField(period)];
  const score = Math.max(0, parseInt(params.score || 0, 10));
  const scores = allScores(period, key);
  let rank = 1;
  scores.forEach(row => {
    if (row.score > score) rank++;
  });
  return rank;
}

function allScores(period, key) {
  const data = sheet().getDataRange().getValues();
  const header = data.shift();
  const idx = Object.fromEntries(header.map((h, i) => [h, i]));
  const field = periodField(period);
  const best = {};
  data.forEach(row => {
    if (String(row[idx[field]]) !== String(key)) return;
    const name = cleanName(row[idx.player_name]);
    const score = parseInt(row[idx.score] || 0, 10);
    if (!best[name] || score > best[name].score) {
      best[name] = { player_name: name, score: score };
    }
  });
  return Object.values(best).sort((a, b) => b.score - a.score);
}

function seedDummy() {
  const p = currentPeriods();
  return ensureDummyRows('daily', p.period_day)
    + ensureDummyRows('weekly', p.period_week)
    + ensureDummyRows('season', p.period_season);
}

function ensureDummyRows(period, key) {
  const scores = topScores(period, key);
  const needed = Math.max(0, DUMMY_TARGET_COUNT - scores.length);
  if (needed === 0) return 0;
  const used = new Set(scores.map(r => cleanName(r.player_name)));
  const out = [];
  for (let i = 0; i < DUMMY_NAMES.length && out.length < needed; i++) {
    if (used.has(cleanName(DUMMY_NAMES[i]))) continue;
    const p = periodsFromKey(period, key);
    out.push([
      timestampForPeriod(period, key, i),
      p.period_day,
      p.period_week,
      p.period_season,
      DUMMY_NAMES[i],
      60 + Math.floor(Math.random() * 1200),
      1 + Math.floor(Math.random() * 13),
      'killed',
      ['bat','orc','hobgoblin','snake','kestrel'][Math.floor(Math.random() * 5)],
      'dummy',
      true,
      'dummy-' + period + '-' + key + '-' + DUMMY_NAMES[i]
    ]);
  }
  if (out.length > 0) {
    const sh = sheet();
    sh.getRange(sh.getLastRow() + 1, 1, out.length, out[0].length).setValues(out);
  }
  return out.length;
}

function periodsFromKey(period, key) {
  const now = currentPeriods();
  if (period === 'daily') {
    return {
      period_day: key,
      period_week: now.period_week,
      period_season: now.period_season
    };
  }
  if (period === 'season') {
    return {
      period_day: now.period_day,
      period_week: now.period_week,
      period_season: key
    };
  }
  return {
    period_day: now.period_day,
    period_week: key,
    period_season: now.period_season
  };
}

function periodField(period) {
  if (period === 'daily') return 'period_day';
  if (period === 'season') return 'period_season';
  return 'period_week';
}

function timestampForPeriod(period, key, offset) {
  const d = new Date();
  d.setUTCMinutes(d.getUTCMinutes() - offset * 17);
  return d.toISOString();
}

function currentPeriods() {
  return periodsFor(new Date());
}

function periodsFor(d) {
  const y = d.getUTCFullYear();
  const m = d.getUTCMonth() + 1;
  const seasonYear = m === 12 ? y + 1 : y;
  const day = Utilities.formatDate(d, 'UTC', 'yyyy-MM-dd');
  return {
    period_day: day,
    period_week: isoWeekKey(d),
    period_season: seasonYear + '-' + seasonName(m)
  };
}

function isoWeekKey(d) {
  const x = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  x.setUTCDate(x.getUTCDate() + 4 - (x.getUTCDay() || 7));
  const yearStart = new Date(Date.UTC(x.getUTCFullYear(), 0, 1));
  const week = Math.ceil((((x - yearStart) / 86400000) + 1) / 7);
  return x.getUTCFullYear() + '-W' + String(week).padStart(2, '0');
}

function seasonName(month) {
  if (month >= 3 && month <= 5) return 'Spring';
  if (month >= 6 && month <= 8) return 'Summer';
  if (month >= 9 && month <= 11) return 'Fall';
  return 'Winter';
}

function cleanName(name) {
  const s = String(name || 'ROGUE').toUpperCase().replace(/[^A-Z0-9 ]/g, '').trim().slice(0, 8);
  return s || 'ROGUE';
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
