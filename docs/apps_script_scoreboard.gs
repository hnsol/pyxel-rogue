const SHEET_NAME = 'scores';
const DUMMY_NAMES = [
  'ACE','NOVA','RIN','KAI','MIO','LUNA','SAGE','ZERO','NIX','REI',
  'JIN','TOMO','YUKI','HAL','ROOK','MINT','ECHO','BYTE','DOT','ASH',
  'RUNE','KITE','NERO','ARIA','LYNX','VOLT','ONYX','MICA','SORA','NOA',
  'ZED','IVY','REX','SOL','NIA','MIKA','YURI','AKI','MAO','HANA',
  'RAY','KIR','NEMO','PICO','LOOP','BETA','GAMMA','DELTA','SIGMA','TAU',
  'MARS','VENUS','PLUTO','COMET','FINN','FAY','LEO','MAY','NOEL','OTTO',
  'PAX','QUIN','RIO','SKY','TEO','UMA','VAN','WREN','XAN','YALE',
  'ZARA','BOLT','DUSK','EMBER','FLUX','GLEN','HAZE','ION','JADE','KNOX',
  'LUX','MOON','NEON','OPAL','PEARL','QUEST','RIFT','SPAR','TIDE','VALE',
  'WAVE','XENO','YON','ZINC','ATLAS','MESA','ORBIT','PIXEL','QUARTZ','RUST'
];

function doGet(e) {
  const period = (e.parameter.period || 'weekly').toLowerCase();
  const key = e.parameter.key || currentPeriods()[period === 'season' ? 'period_season' : 'period_week'];
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
    sh.appendRow(['timestamp','period_day','period_week','period_season','player_name','score','depth','result_flags','killer','client_build','is_dummy']);
  }
  return sh;
}

function appendScore(entry) {
  const now = entry.timestamp || new Date().toISOString();
  const p = periodsFor(new Date(now));
  const name = cleanName(entry.player_name);
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
    Boolean(entry.is_dummy)
  ]);
}

function topScores(period, key) {
  const data = sheet().getDataRange().getValues();
  const header = data.shift();
  const idx = Object.fromEntries(header.map((h, i) => [h, i]));
  const field = period === 'season' ? 'period_season' : 'period_week';
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
        is_dummy: row[idx.is_dummy] === true
      };
    }
  });
  return Object.values(best).sort((a, b) => b.score - a.score).slice(0, 10);
}

function seedDummy() {
  const p = currentPeriods();
  return ensureDummyRows('weekly', p.period_week);
}

function ensureDummyRows(period, key) {
  const existing = topScores(period, key).filter(r => r.is_dummy).length;
  let rows = 0;
  for (let i = existing; i < 24 && i < DUMMY_NAMES.length; i++) {
    const p = periodsFromKey(period, key);
    appendScore({
      timestamp: timestampForPeriod(period, key, i),
      period_day: p.period_day,
      period_week: p.period_week,
      period_season: p.period_season,
      player_name: DUMMY_NAMES[i],
      score: 60 + Math.floor(Math.random() * 1200),
      depth: 1 + Math.floor(Math.random() * 13),
      result_flags: 'killed',
      killer: ['bat','orc','hobgoblin','snake','kestrel'][Math.floor(Math.random() * 5)],
      client_build: 'dummy',
      is_dummy: true
    });
    rows++;
  }
  return rows;
}

function periodsFromKey(period, key) {
  const now = currentPeriods();
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
