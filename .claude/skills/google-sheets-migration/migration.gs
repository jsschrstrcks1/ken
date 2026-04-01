/**
 * Manatee Creek Flock Manager — Data Migration Script v2
 *
 * Migrates REAL DATA from old 113-tab spreadsheet to new 26-tab structure.
 * Fixes from orchestra review: dynamic column detection, single-read cache,
 * sub-sheet checkpoints, 8-12 breed support, missing data phases.
 *
 * SOURCE: 1Rt6N0yD6DPWZmiPH1I2RAB3K0a-qsMWVfJH661tw4gk
 * DEST:   1EQ5bOZL5Xmzu_7VvaMHTHWIwHPJqDKTJY_MMPduKrJU
 *
 * Usage:
 *   1. Open DEST spreadsheet > Extensions > Apps Script
 *   2. Paste this file
 *   3. Run migrateAll()
 *   4. If timeout, run migrateResume()
 *   5. Check "Migration Log" tab for progress
 */

var SOURCE_ID = '1Rt6N0yD6DPWZmiPH1I2RAB3K0a-qsMWVfJH661tw4gk';
var DEST_ID = '1EQ5bOZL5Xmzu_7VvaMHTHWIwHPJqDKTJY_MMPduKrJU';
var TIME_LIMIT_MS = 200000; // 3m20s — very aggressive, leaves 2m40s buffer
var START_TIME;

// ============================================================
// ENTRY POINTS
// ============================================================

function migrateAll() {
  PropertiesService.getScriptProperties().deleteAllProperties();
  migrateResume();
}

function migrateResume() {
  START_TIME = Date.now();
  var props = PropertiesService.getScriptProperties();
  var phase = props.getProperty('phase') || 'animalSheets';

  var phases = [
    { name: 'animalSheets', fn: migrateAnimalSheets_ },
    { name: 'systemTabs', fn: migrateSystemTabs_ },
    { name: 'done', fn: null }
  ];

  for (var i = 0; i < phases.length; i++) {
    if (phases[i].name !== phase) continue;
    for (var j = i; j < phases.length; j++) {
      if (!phases[j].fn) { log_('MIGRATION COMPLETE — all phases done.'); return; }
      if (timeUp_()) { log_('Time guard before ' + phases[j].name + '. Run migrateResume().'); return; }
      log_('=== Starting phase: ' + phases[j].name + ' ===');
      var done = phases[j].fn();
      if (done === false) {
        log_('Phase ' + phases[j].name + ' paused for time. Run migrateResume().');
        return;
      }
      props.setProperty('phase', (j + 1 < phases.length) ? phases[j + 1].name : 'done');
      log_('=== Completed phase: ' + phases[j].name + ' ===');
    }
    break;
  }
}

// ============================================================
// PHASE 1: ALL ANIMAL SHEETS — single read, extract everything
// ============================================================

function migrateAnimalSheets_() {
  var src = SpreadsheetApp.openById(SOURCE_ID);
  var dest = SpreadsheetApp.openById(DEST_ID);
  var props = PropertiesService.getScriptProperties();
  var startIdx = parseInt(props.getProperty('animalIdx') || '0');

  var animalSheets = getAnimalSheets_(src);

  var identityRows = [];
  var lambingRows = [];
  var medicalRows = [];

  // Standard breed names to match against (covers all 22 in the flock)
  var KNOWN_BREEDS = [
    'american black belly', 'awassi', 'babydoll', 'barbados black belly',
    'black headed dorper', 'cotswald', 'cotswold', 'cracker', 'east friesan',
    'east friesian', 'gulf coast native', 'hampshire', 'jacob', 'karakul',
    'katahdin', 'southdown', 'st augustine', 'st croix', 'suffolk', 'texel',
    'tunis', 'white dorper', 'wiltshire horn'
  ];

  for (var i = startIdx; i < animalSheets.length; i++) {
    if (timeUp_()) {
      // Save sub-checkpoint and flush what we have
      props.setProperty('animalIdx', String(i));
      props.setProperty('phase', 'animalSheets');
      flushAnimalData_(dest, identityRows, lambingRows, medicalRows);
      log_('Time guard at animal sheet ' + i + '/' + animalSheets.length);
      return false;
    }

    var sheet = animalSheets[i];
    var sheetName = sheet.getName();
    var data = sheet.getDataRange().getValues();
    if (data.length < 2) continue;

    // --- IDENTITY: header-based column detection ---
    var row0 = data[0];
    var hdr = {};
    for (var c = 0; c < row0.length; c++) {
      var h = String(row0[c] || '').toLowerCase().trim();
      if (h === 'name' || (c === 0 && !hdr['name'])) hdr['name'] = c;
      if (h === 'tag' || h === 'tag #') hdr['tag'] = c;
      if (h === 'sex') hdr['sex'] = c;
      if (h === 'dob' || h === 'date of birth') hdr['dob'] = c;
      if (h === 'sire') hdr['sire'] = c;
      if (h === 'dam') hdr['dam'] = c;
      if (h.indexOf('imbreed') >= 0 || h.indexOf('inbreed') >= 0) hdr['inbreed'] = c;
      if (h.indexOf('multiple') >= 0) hdr['multiple'] = c;
    }

    var name = safe_(data[0][hdr['name'] || 0]);
    var tag = data[0][hdr['tag'] || 1] || '';
    // Tag sometimes on row 5 col B
    if (!tag && data.length > 4) {
      var r4a = String(data[4][0] || '').toLowerCase();
      if (r4a === 'tag' || r4a === 'tag #') tag = data[4][1] || '';
    }
    var sex = safe_(data[0][hdr['sex'] || 4]);
    var dob = data[0][hdr['dob'] || 7] || '';
    // Some sheets put DOB in K1 (index 10)
    if (!dob && data[0][10]) dob = data[0][10];
    var sire = safe_(data[0][hdr['sire'] || 8]);
    var dam = safe_(data[0][hdr['dam'] || 9]);
    // Sire/dam sometimes in later columns (L1, M1)
    if (!sire && data[0][11]) sire = safe_(data[0][11]);
    if (!dam && data[0][12]) dam = safe_(data[0][12]);

    // --- BREED %: scan rows 1-24 for breed names + percentages ---
    var breedParts = [];
    for (var r = 1; r < Math.min(data.length, 25); r++) {
      // Find the breed name and percentage in this row
      var pct = null;
      var breedName = null;
      for (var c = 0; c < Math.min(data[r].length, 6); c++) {
        var v = data[r][c];
        if (typeof v === 'number' && v > 0 && v <= 100 && pct === null) pct = v;
        if (typeof v === 'string' && v.length > 2) {
          var vl = v.toLowerCase().trim();
          for (var b = 0; b < KNOWN_BREEDS.length; b++) {
            if (vl === KNOWN_BREEDS[b] || vl.indexOf(KNOWN_BREEDS[b]) >= 0) {
              breedName = v.trim(); break;
            }
          }
        }
      }
      if (pct !== null && pct > 0 && breedName) {
        breedParts.push(Math.round(pct * 100) / 100 + '% ' + breedName);
      }
    }
    var breedStr = breedParts.length > 0 ? breedParts.join(' / ') : 'MC';

    // Ram/Ewe weight from rows 22-24 area
    var weight = '';
    for (var r = 21; r < Math.min(data.length, 25); r++) {
      for (var c = 0; c < Math.min(data[r].length, 4); c++) {
        var v = data[r][c];
        if (typeof v === 'number' && v > 20 && v < 500) { weight = v; break; }
      }
      if (weight) break;
    }

    identityRows.push([
      i + 1, '', tag, name, sex, breedStr, '', weight, '', dob, '', '', sire, dam, '', sheetName
    ]);

    // --- LAMBING: scan for year headers ---
    var inProspective = false;
    for (var r = 24; r < data.length; r++) {
      var cellA = data[r][0];
      var cellAStr = String(cellA || '').toLowerCase();
      if (cellAStr.indexOf('prospective') >= 0 || cellAStr.indexOf('if bred') >= 0) {
        inProspective = true;
      }
      if (inProspective) continue;

      if (typeof cellA === 'number' && cellA >= 2019 && cellA <= 2026) {
        var year = cellA;
        // Detect header layout from THIS row
        var headerB = String(data[r][1] || '').toLowerCase();
        var isSireFirst = (headerB === 'sire');

        r++; // move to first lamb row
        while (r < data.length) {
          var la = data[r][0];
          var laStr = String(la || '').toLowerCase();
          if (laStr.indexOf('prospective') >= 0 || laStr.indexOf('if bred') >= 0) { inProspective = true; break; }
          if (laStr === 'medical' || laStr === 'medical:') break;
          if (typeof la === 'number' && la >= 2019 && la <= 2026) { r--; break; } // back up for outer loop

          // Check if row has any data
          var hasAny = false;
          for (var c = 0; c < Math.min(data[r].length, 10); c++) {
            if (data[r][c] !== '' && data[r][c] !== null && data[r][c] !== undefined) { hasAny = true; break; }
          }
          if (!hasAny) { r++; continue; }

          var lambName = safe_(la);
          var sireL = '', birthWt = '', birthDate = '', notes = '';

          if (isSireFirst) {
            sireL = safe_(data[r][1] || '');
            birthWt = data[r][4] || data[r][5] || '';
            birthDate = data[r][9] || data[r][6] || '';
            notes = safe_(data[r][17] || data[r][15] || '');
          } else {
            birthWt = data[r][1] || '';
            birthDate = data[r][6] || data[r][7] || '';
            sireL = safe_(data[r][7] || data[r][8] || '');
            notes = safe_(data[r][14] || data[r][15] || data[r][17] || '');
          }

          lambingRows.push([
            '', '', name, sireL, '', '', '', '', birthDate,
            1, '', birthWt, '[' + year + '] ' + lambName + ' [src:' + sheetName + '] ' + notes
          ]);
          r++;
        }
      }
    }

    // --- MEDICAL: find "Medical" section ---
    for (var r = 0; r < data.length; r++) {
      var cellA = String(data[r][0] || '').toLowerCase().trim();
      if (cellA === 'medical' || cellA === 'medical:') {
        // Detect if next row has sub-headers
        var hasFamachaCol = false;
        var famIdx = 2; // default col C
        if (r + 1 < data.length) {
          for (var c = 0; c < Math.min(data[r + 1].length, 6); c++) {
            if (String(data[r + 1][c] || '').toLowerCase().indexOf('famacha') >= 0) {
              famIdx = c; hasFamachaCol = true; break;
            }
          }
        }

        var emptyCount = 0;
        for (var mr = r + 1; mr < data.length; mr++) {
          var dateVal = data[mr][0];
          if (dateVal === '' || dateVal === null || dateVal === undefined) {
            emptyCount++;
            if (emptyCount >= 2) break;
            continue;
          }
          emptyCount = 0;
          var dvStr = String(dateVal).toLowerCase();
          if (dvStr.indexOf('prospective') >= 0 || dvStr.indexOf('if bred') >= 0) break;

          if (dateVal instanceof Date || (typeof dateVal === 'string' && dateVal.match(/\d{4}/))) {
            var treatment = safe_(data[mr][1] || '');
            var famacha = data[mr][famIdx] || '';
            medicalRows.push([
              dateVal, '', name, '', treatment, '', '', famacha, '', '', '', '',
              '[src:' + sheetName + ']'
            ]);
          }
        }
        break;
      }
    }
  }

  // Flush all accumulated data
  flushAnimalData_(dest, identityRows, lambingRows, medicalRows);
  props.setProperty('animalIdx', '0'); // reset for next full run
  return true;
}

function flushAnimalData_(dest, identityRows, lambingRows, medicalRows) {
  if (identityRows.length > 0) {
    var mfl = dest.getSheetByName('Master Flock List') || dest.insertSheet('Master Flock List');
    var startRow = firstEmpty_(mfl, 5, 4);
    mfl.getRange(startRow, 1, identityRows.length, identityRows[0].length).setValues(identityRows);
    log_('Wrote ' + identityRows.length + ' animals to Master Flock List');
  }
  if (lambingRows.length > 0) {
    var bst = dest.getSheetByName('Breeding Season Tracker') || dest.insertSheet('Breeding Season Tracker');
    var startRow = firstEmpty_(bst, 4, 3);
    bst.getRange(startRow, 1, lambingRows.length, lambingRows[0].length).setValues(lambingRows);
    log_('Wrote ' + lambingRows.length + ' lambing records to Breeding Season Tracker');
  }
  if (medicalRows.length > 0) {
    var htl = dest.getSheetByName('Health & Treatment Log') || dest.insertSheet('Health & Treatment Log');
    var startRow = firstEmpty_(htl, 4, 15); // col O (ANIMAL in manual section)
    htl.getRange(startRow, 13, medicalRows.length, medicalRows[0].length).setValues(medicalRows);
    log_('Wrote ' + medicalRows.length + ' medical records to Health & Treatment Log');
  }
}

// ============================================================
// PHASE 2: SYSTEM TABS — On Property, Costs, Lamb Data, etc.
// ============================================================

function migrateSystemTabs_() {
  var src = SpreadsheetApp.openById(SOURCE_ID);
  var dest = SpreadsheetApp.openById(DEST_ID);

  migratePenRosters_(src, dest);
  if (timeUp_()) return false;
  migrateCosts_(src, dest);
  if (timeUp_()) return false;
  migrateLambData_(src, dest);
  if (timeUp_()) return false;
  migrateWeights_(src, dest);
  if (timeUp_()) return false;
  migrateEweRamData_(src, dest);
  if (timeUp_()) return false;
  migratePedigree_(src, dest);
  if (timeUp_()) return false;
  migrate30DayWeights_(src, dest);
  return true;
}

// --- Pen Rosters ---
function migratePenRosters_(src, dest) {
  var op = src.getSheetByName('On Property');
  if (!op) { log_('No On Property sheet, skipping pens'); return; }
  var data = op.getDataRange().getValues();

  var penMap = {};
  for (var r = 1; r < data.length; r++) {
    var name = safe_(data[r][3]);
    if (!name) continue;
    var pen = '';
    for (var c = 0; c < data[r].length; c++) {
      var v = String(data[r][c] || '');
      if (v.match(/^Pen \d/) || v === 'Tree Fort' || v.indexOf('Goose') >= 0) { pen = v; break; }
    }
    if (!pen) continue;
    if (!penMap[pen]) penMap[pen] = [];
    penMap[pen].push([
      data[r][2] || '', data[r][1] || '', name, data[r][4] || '',
      data[r][5] || '', data[r][6] || '', data[r][7] || '',
      data[r][8] || '', data[r][9] || '', data[r][10] || '', ''
    ]);
  }

  var destNames = {
    'Pen 1':'Pen 1','Pen 2':'Pen 2','Pen 3':'Pen 3','Pen 4':'Pen 4',
    'Pen 5':'Pen 5','Pen 6':'Pen 6','Tree Fort':'Tree Fort Pen','Goose Pen':'Goose Pen'
  };
  for (var pen in penMap) {
    var dn = destNames[pen] || pen;
    var ps = dest.getSheetByName(dn);
    if (!ps) { log_('No dest sheet: ' + dn); continue; }
    ps.getRange(5, 1, penMap[pen].length, penMap[pen][0].length).setValues(penMap[pen]);
    log_('Wrote ' + penMap[pen].length + ' animals to ' + dn);
  }
}

// --- Costs ---
function migrateCosts_(src, dest) {
  var cs = src.getSheetByName('Costs');
  if (!cs) { log_('No Costs sheet'); return; }
  var data = cs.getDataRange().getValues();
  var cf = dest.getSheetByName('Costs & Financials') || dest.insertSheet('Costs & Financials');
  var rows = [];
  var hdrRow = findHeaderRow_(data, ['Sheep Name', 'Tag', 'Gender']);
  if (hdrRow < 0) { log_('No header in Costs'); return; }
  for (var r = hdrRow + 1; r < data.length; r++) {
    var nm = safe_(data[r][2] || data[r][1]);
    if (!nm) continue;
    rows.push([
      data[r][1]||'', nm, data[r][3]||'', data[r][4]||'', data[r][5]||'',
      data[r][6]||'', data[r][7]||'', data[r][8]||'', data[r][9]||'', '',
      data[r][12]||'', data[r][13]||'', '', data[r][14]||'', data[r][15]||'',
      data[r][16]||'', data[r][17]||'', data[r][18]||'', data[r][19]||'',
      data[r][20]||'', safe_(data[r][21]||'')
    ]);
  }
  if (rows.length > 0) {
    var sr = firstEmpty_(cf, 4, 2);
    cf.getRange(sr, 1, rows.length, rows[0].length).setValues(rows);
    log_('Wrote ' + rows.length + ' cost records');
  }
}

// --- Lamb Data (Extension Service) ---
function migrateLambData_(src, dest) {
  var ls = src.getSheetByName('Lamb Data');
  if (!ls) { log_('No Lamb Data sheet'); return; }
  var data = ls.getDataRange().getValues();
  var wh = dest.getSheetByName('Weight History & ADG') || dest.insertSheet('Weight History & ADG');
  var hdrRow = findHeaderRow_(data, ['Lamb ID', 'Ewe ID']);
  if (hdrRow < 0) { log_('No header in Lamb Data'); return; }

  var headers = ['#','Lamb ID','Ewe ID','Ewe Age','Ram ID','Birth Date','Sex',
    'Birth/Rearing','Birth Wt','Weaning Date','Wng Wt','Wng Age',
    'Wng Age Group','WDA','ADG','Age Corr WW','Adj WW','Adj WW Ratio'];
  var sr = firstEmpty_(wh, 1, 1);
  wh.getRange(sr, 1, 1, headers.length).setValues([headers]);
  sr++;

  var rows = [];
  for (var r = hdrRow + 1; r < data.length; r++) {
    if (!data[r][1] && data[r][1] !== 0) continue;
    var row = [];
    for (var c = 0; c < 18 && c < data[r].length; c++) row.push(data[r][c] || '');
    while (row.length < 18) row.push('');
    rows.push(row);
  }
  if (rows.length > 0) {
    wh.getRange(sr, 1, rows.length, 18).setValues(rows);
    log_('Wrote ' + rows.length + ' lamb records to Weight History');
  }
}

// --- Weights and Averages ---
function migrateWeights_(src, dest) {
  var ws = src.getSheetByName('Weights and Averages');
  if (!ws) { log_('No Weights sheet'); return; }
  var data = ws.getDataRange().getValues();
  var wh = dest.getSheetByName('Weight History & ADG') || dest.insertSheet('Weight History & ADG');
  var sr = firstEmpty_(wh, 1, 1) + 1;
  wh.getRange(sr, 1).setValue('=== WEIGHTS AND AVERAGES FROM SOURCE ===');
  sr++;
  var rows = [];
  for (var r = 0; r < data.length; r++) {
    var hasData = false;
    for (var c = 0; c < data[r].length; c++) { if (data[r][c]) { hasData = true; break; } }
    if (hasData) rows.push(data[r].slice(0, 15));
  }
  if (rows.length > 0) {
    wh.getRange(sr, 1, rows.length, rows[0].length).setValues(rows);
    log_('Wrote ' + rows.length + ' weight rows');
  }
}

// --- Ewe Data + Ram Data ---
function migrateEweRamData_(src, dest) {
  migrateRegistrySheet_(src, dest, 'Ewe Data', 'Active Ewes', 'Ewe ID', 'Ewe Name');
  migrateRegistrySheet_(src, dest, 'Ram Data', 'Active Rams', 'Ram ID', 'Ram Name');
}

function migrateRegistrySheet_(src, dest, srcName, destName, idCol, nameCol) {
  var ss = src.getSheetByName(srcName);
  if (!ss) { log_('No ' + srcName + ' sheet'); return; }
  var data = ss.getDataRange().getValues();
  var ds = dest.getSheetByName(destName) || dest.insertSheet(destName);
  var hdrRow = findHeaderRow_(data, [idCol, nameCol]);
  if (hdrRow < 0) { log_('No header in ' + srcName); return; }
  var rows = [];
  for (var r = hdrRow + 1; r < data.length; r++) {
    var id = safe_(data[r][1]);
    if (!id) continue;
    rows.push([
      data[r][0]||'', id, '', data[r][2]||'', '', data[r][3]||'',
      '', '', '', data[r][7]||'', '', safe_(data[r][5]||'') + '/' + safe_(data[r][6]||'')
    ]);
  }
  if (rows.length > 0) {
    var sr = firstEmpty_(ds, 5, 2);
    ds.getRange(sr, 1, rows.length, rows[0].length).setValues(rows);
    log_('Wrote ' + rows.length + ' records to ' + destName);
  }
}

// --- Pedigree ---
function migratePedigree_(src, dest) {
  var pn = src.getSheetByName('Pedigree Name (1)');
  if (!pn) pn = src.getSheetByName('Pedigree Name');
  if (!pn) { log_('No Pedigree sheet'); return; }
  var data = pn.getDataRange().getValues();
  var pd = dest.getSheetByName('Pedigree') || dest.insertSheet('Pedigree');
  var sr = firstEmpty_(pd, 2, 1);
  var rows = [];
  for (var r = 1; r < data.length; r++) {
    var hasData = false;
    for (var c = 0; c < data[r].length; c++) { if (data[r][c]) { hasData = true; break; } }
    if (hasData) rows.push(data[r].slice(0, 9));
  }
  if (rows.length > 0) {
    pd.getRange(sr, 1, rows.length, rows[0].length).setValues(rows);
    log_('Wrote ' + rows.length + ' pedigree rows');
  }
}

// --- 2022 30-day weights ---
function migrate30DayWeights_(src, dest) {
  var ws = src.getSheetByName('2022 30 day weights');
  if (!ws) { log_('No 2022 30 day weights'); return; }
  var data = ws.getDataRange().getValues();
  var wh = dest.getSheetByName('Weight History & ADG') || dest.insertSheet('Weight History & ADG');
  var sr = firstEmpty_(wh, 1, 1) + 1;
  wh.getRange(sr, 1).setValue('=== 2022 30-DAY WEIGHTS FROM SOURCE ===');
  sr++;
  var rows = [];
  for (var r = 0; r < data.length; r++) {
    var hasData = false;
    for (var c = 0; c < data[r].length; c++) { if (data[r][c]) { hasData = true; break; } }
    if (hasData) rows.push(data[r].slice(0, 10));
  }
  if (rows.length > 0) {
    wh.getRange(sr, 1, rows.length, rows[0].length).setValues(rows);
    log_('Wrote ' + rows.length + ' 30-day weight rows');
  }
}

// ============================================================
// UTILITIES
// ============================================================

function getAnimalSheets_(ss) {
  var SKIP = {
    'Manatee Creek 2025':1, 'Manatee Creek (Old)':1, 'Master':1, 'Master (1)':1,
    'Weights and Averages':1, 'Breeding Plans for 24':1, 'Possibile Lambs':1,
    'Potential Offspring':1, 'Sheep Weight Calculator':1, 'Template':1, 'Pen Template':1,
    'Lamb Data':1, 'Ram Data':1, 'Ewe Data':1, 'Summary':1, 'User Guide':1, 'Config':1,
    '2022 30 day weights':1, 'On Property':1, 'Costs':1, 'Pedigree_Viewer':1,
    'Pedigree Name':1, 'Pedigree Tattoo':1, 'Pedigree Name (1)':1, 'Pedigree Tattoo (1)':1,
    'Tables':1, 'EXPORT_VALUES':1,
    'Pen 1':1, 'Pen 2':1, 'Pen 1 (2024) ':1, 'Pen 1 (2024)':1, 'Pen 2 (2024)':1,
    'Pen 3 - Sam (5 Sheep)':1, 'Pen 4 - Southdown Ram (7 Sheep)':1,
    'Pen 5 - Rocky (5 sheep)':1, 'Pen 6 - Rocky (4 Sheep)':1,
    'Pen 6 - Fat Tail':1, '2024 Pen 4 (Kelsier)':1,
    'Sheet74':1,'Sheet75':1,'Sheet79':1,'Sheet81':1,'Sheet83':1,'Sheet84':1,'Sheet87':1
  };
  var sheets = ss.getSheets();
  var result = [];
  for (var i = 0; i < sheets.length; i++) {
    var n = sheets[i].getName();
    if (!SKIP[n] && !SKIP[n.trim()]) result.push(sheets[i]);
  }
  return result;
}

function safe_(val) {
  if (val === null || val === undefined) return '';
  var s = String(val).trim();
  if (s.charAt(0) === '=' && s.indexOf('!') >= 0) return '';
  if (s === '#REF!') return '';
  return s;
}

function firstEmpty_(sheet, startRow, col) {
  var maxR = sheet.getMaxRows();
  if (startRow > maxR) return startRow;
  var vals = sheet.getRange(startRow, col, maxR - startRow + 1, 1).getValues();
  for (var i = 0; i < vals.length; i++) {
    if (!vals[i][0] && vals[i][0] !== 0) return startRow + i;
  }
  return startRow + vals.length;
}

function findHeaderRow_(data, keywords) {
  for (var r = 0; r < Math.min(data.length, 15); r++) {
    for (var c = 0; c < data[r].length; c++) {
      var v = String(data[r][c] || '');
      for (var k = 0; k < keywords.length; k++) {
        if (v.indexOf(keywords[k]) >= 0) return r;
      }
    }
  }
  return -1;
}

function timeUp_() { return (Date.now() - START_TIME) > TIME_LIMIT_MS; }

function log_(msg) {
  var dest = SpreadsheetApp.openById(DEST_ID);
  var ls = dest.getSheetByName('Migration Log');
  if (!ls) {
    ls = dest.insertSheet('Migration Log');
    ls.getRange(1, 1, 1, 3).setValues([['Timestamp', 'Message', 'Phase']]);
  }
  ls.appendRow([new Date(), msg, PropertiesService.getScriptProperties().getProperty('phase') || '?']);
}
