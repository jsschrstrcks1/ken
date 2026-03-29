/**
 * Manatee Creek Flock Manager — Data Migration Script
 *
 * Migrates REAL DATA from old 113-tab spreadsheet to new 26-tab structure.
 * Chunked execution with checkpoint/resume to survive 6-minute Apps Script limit.
 *
 * SOURCE: 1Rt6N0yD6DPWZmiPH1I2RAB3K0a-qsMWVfJH661tw4gk
 * DEST:   1EQ5bOZL5Xmzu_7VvaMHTHWIwHPJqDKTJY_MMPduKrJU
 *
 * Usage:
 *   1. Open DEST spreadsheet > Extensions > Apps Script
 *   2. Paste this file
 *   3. Run migrateAll()
 *   4. If timeout, run migrateResume()
 */

var SOURCE_ID = '1Rt6N0yD6DPWZmiPH1I2RAB3K0a-qsMWVfJH661tw4gk';
var DEST_ID = '1EQ5bOZL5Xmzu_7VvaMHTHWIwHPJqDKTJY_MMPduKrJU';
var TIME_LIMIT_MS = 240000; // 4 minutes — aggressive guard, leaves 2 min buffer
var START_TIME;

// ============================================================
// ENTRY POINTS
// ============================================================

function migrateAll() {
  resetCheckpoint_();
  migrateResume();
}

function migrateResume() {
  START_TIME = Date.now();
  var phase = getCheckpoint_();
  var phases = [
    { name: 'identity', fn: migrateIdentity_ },
    { name: 'lambing', fn: migrateLambing_ },
    { name: 'medical', fn: migrateMedical_ },
    { name: 'penRosters', fn: migratePenRosters_ },
    { name: 'costs', fn: migrateCosts_ },
    { name: 'lambData', fn: migrateLambData_ },
    { name: 'weights', fn: migrateWeights_ },
    { name: 'eweRamData', fn: migrateEweRamData_ },
    { name: 'done', fn: null }
  ];

  var startIdx = 0;
  for (var i = 0; i < phases.length; i++) {
    if (phases[i].name === phase) { startIdx = i; break; }
  }

  for (var i = startIdx; i < phases.length; i++) {
    if (!phases[i].fn) { log_('Migration complete!'); return; }
    if (timeUp_()) {
      log_('Time guard hit before phase: ' + phases[i].name + '. Run migrateResume() to continue.');
      return;
    }
    log_('Starting phase: ' + phases[i].name);
    try {
      phases[i].fn();
    } catch (e) {
      log_('ERROR in ' + phases[i].name + ': ' + e.message);
      return;
    }
    // Save next phase as checkpoint
    var nextPhase = (i + 1 < phases.length) ? phases[i + 1].name : 'done';
    setCheckpoint_(nextPhase);
    log_('Completed phase: ' + phases[i].name);
  }
}

// ============================================================
// PHASE 1: ANIMAL IDENTITY → Master Flock List
// ============================================================

function migrateIdentity_() {
  var src = SpreadsheetApp.openById(SOURCE_ID);
  var dest = SpreadsheetApp.openById(DEST_ID);
  var mfl = getOrCreateSheet_(dest, 'Master Flock List');

  // Get animal sheet names from source
  var animalSheets = getAnimalSheetNames_(src);
  var rows = [];

  // Standard breed list in order (rows 2-22 in animal sheets)
  var breeds = [
    'American Black Belly', 'Awassi', 'Babydoll', 'Barbados Black Belly',
    'Black Headed Dorper', 'Cotswald', 'Cracker', 'East Friesian',
    'Gulf Coast Native', 'Hampshire', 'Jacob', 'Karakul', 'Katahdin',
    'Southdown', 'St Augustine', 'St Croix', 'Suffolk', 'Texel',
    'Tunis', 'White Dorper', 'Wiltshire Horn'
  ];

  for (var i = 0; i < animalSheets.length; i++) {
    if (timeUp_()) { log_('Time guard in identity at sheet ' + i); setCheckpoint_('identity'); return; }
    var sheet = animalSheets[i];
    var data = sheet.getDataRange().getValues();
    if (data.length < 2) continue;

    var name = safeStr_(data[0][0]); // A1
    var sex = safeStr_(data[0][4] || data[0][3]); // E1 or D1
    var dob = data[0][7] || data[0][6] || data[0][10] || ''; // H1, G1, or K1
    var sire = safeStr_(data[0][8] || data[0][11] || ''); // I1 or L1
    var dam = safeStr_(data[0][9] || data[0][12] || ''); // J1 or M1
    var tag = data[0][1] || data[4] && data[4][1] || ''; // B1 or B5 (tag row)
    var inbreed = data[0][5] || data[0][9] || '';

    // Extract breed % — column B or C, rows 2-22
    var breedStr = '';
    var breedParts = [];
    for (var b = 1; b <= 21 && b < data.length; b++) {
      var pct = data[b][1] || data[b][2]; // Column B or C
      if (typeof pct === 'number' && pct > 0) {
        var breedName = (b - 1 < breeds.length) ? breeds[b - 1] : safeStr_(data[b][2] || data[b][3]);
        breedParts.push(Math.round(pct) + '% ' + breedName);
      }
    }
    breedStr = breedParts.join(' / ') || 'MC';

    // Weight — rows 22-23 area
    var weight = '';
    for (var w = 21; w <= 23 && w < data.length; w++) {
      var wv = data[w][1];
      if (typeof wv === 'number' && wv > 0) { weight = wv; break; }
    }

    rows.push([i + 1, '', tag, name, sex, breedStr, '', weight, '', dob, '', '', sire, dam, '', sheet.getName()]);
  }

  if (rows.length > 0) {
    // Find first empty row after header (row 4 is header in new sheet)
    var startRow = findFirstEmptyRow_(mfl, 5, 4); // col D (name)
    mfl.getRange(startRow, 1, rows.length, rows[0].length).setValues(rows);
    log_('Wrote ' + rows.length + ' animals to Master Flock List');
  }
}

// ============================================================
// PHASE 2: LAMBING RECORDS → Breeding Season Tracker
// ============================================================

function migrateLambing_() {
  var src = SpreadsheetApp.openById(SOURCE_ID);
  var dest = SpreadsheetApp.openById(DEST_ID);
  var bst = getOrCreateSheet_(dest, 'Breeding Season Tracker');

  var animalSheets = getAnimalSheetNames_(src);
  var rows = [];

  for (var i = 0; i < animalSheets.length; i++) {
    if (timeUp_()) { log_('Time guard in lambing at sheet ' + i); setCheckpoint_('lambing'); return; }
    var sheet = animalSheets[i];
    var data = sheet.getDataRange().getValues();
    var parentName = safeStr_(data[0][0]);

    // Scan for year headers (numeric value 2019-2026 in column A, row >= 24)
    for (var r = 24; r < data.length; r++) {
      var cellA = data[r][0];
      // Stop at "Prospective Breedings" or "Medical" sections
      if (typeof cellA === 'string' && (cellA.indexOf('Prospective') >= 0)) break;

      // Year header row
      if (typeof cellA === 'number' && cellA >= 2019 && cellA <= 2026) {
        var year = cellA;
        // Read lambs until next year header or section break
        for (var lr = r + 1; lr < data.length; lr++) {
          var lambA = data[lr][0];
          // Next year header or section header
          if (typeof lambA === 'number' && lambA >= 2019 && lambA <= 2026) break;
          if (typeof lambA === 'string' && (lambA.indexOf('Prospective') >= 0 || lambA.indexOf('Medical') >= 0)) break;

          // Skip if row is all empty
          var hasData = false;
          for (var c = 0; c < Math.min(data[lr].length, 18); c++) {
            if (data[lr][c] !== '' && data[lr][c] !== null) { hasData = true; break; }
          }
          if (!hasData) continue;

          var lambName = safeStr_(lambA);
          // Columns vary but typical: A=name/tag, B=sire or birthWt, C=mateDate, D=dueDate, E=birthWt or birthDate
          // Handle both layout variants
          var sire = '', birthWt = '', birthDate = '', w30 = '', w60 = '', w90 = '';
          var keepSell = '', income = '', notes = '';

          // Layout 1 (older): A=name, B=birthWt, C=30d, D=60d, E=90d, F=FEC, G=DOB, H=sire, I=dam
          // Layout 2 (newer): A=name, B=sire, C=mateDate, D=dueDate, E=birthWt, F=30d, G=60d, H=90d
          if (data[r][1] === 'Birth Weight' || (typeof data[r][1] === 'string' && data[r][1].indexOf('Birth') >= 0)) {
            birthWt = data[lr][1] || '';
            w30 = data[lr][2] || '';
            w60 = data[lr][3] || '';
            w90 = data[lr][4] || '';
            birthDate = data[lr][6] || data[lr][7] || '';
            sire = safeStr_(data[lr][7] || data[lr][8] || '');
            keepSell = safeStr_(data[lr][10] || data[lr][11] || '');
            income = data[lr][11] || data[lr][12] || '';
            notes = safeStr_(data[lr][14] || data[lr][15] || data[lr][17] || '');
          } else if (data[r][1] === 'Sire') {
            sire = safeStr_(data[lr][1] || '');
            birthWt = data[lr][4] || data[lr][5] || '';
            birthDate = data[lr][6] || data[lr][9] || '';
            w30 = data[lr][5] || '';
            w60 = data[lr][6] || '';
            w90 = data[lr][7] || '';
            keepSell = safeStr_(data[lr][13] || data[lr][14] || '');
            notes = safeStr_(data[lr][17] || data[lr][15] || '');
          }

          rows.push([
            '', '', parentName, sire, '', '', '', '', birthDate,
            lambName || '', '', birthWt, notes + ' [' + year + ', src: ' + sheet.getName() + ']'
          ]);
        }
        // Skip to after the lamb rows (will be handled by the inner loop break)
      }
    }
  }

  if (rows.length > 0) {
    var startRow = findFirstEmptyRow_(bst, 4, 3); // col C (ewe name)
    bst.getRange(startRow, 1, rows.length, rows[0].length).setValues(rows);
    log_('Wrote ' + rows.length + ' lambing records to Breeding Season Tracker');
  }
}

// ============================================================
// PHASE 3: MEDICAL / FAMACHA → Health & Treatment Log
// ============================================================

function migrateMedical_() {
  var src = SpreadsheetApp.openById(SOURCE_ID);
  var dest = SpreadsheetApp.openById(DEST_ID);
  var htl = getOrCreateSheet_(dest, 'Health & Treatment Log');

  var animalSheets = getAnimalSheetNames_(src);
  var rows = [];

  for (var i = 0; i < animalSheets.length; i++) {
    if (timeUp_()) { log_('Time guard in medical at sheet ' + i); setCheckpoint_('medical'); return; }
    var sheet = animalSheets[i];
    var data = sheet.getDataRange().getValues();
    var animalName = safeStr_(data[0][0]);

    // Find "Medical" section
    for (var r = 0; r < data.length; r++) {
      var cellA = safeStr_(data[r][0]);
      if (cellA === 'Medical' || cellA === 'medical') {
        // Read medical rows until empty gap or next section
        for (var mr = r + 1; mr < data.length; mr++) {
          var dateVal = data[mr][0];
          if (dateVal === '' || dateVal === null) {
            // Allow one empty row
            if (mr + 1 < data.length && (data[mr + 1][0] === '' || data[mr + 1][0] === null)) break;
            continue;
          }
          // Stop if we hit a section header
          if (typeof dateVal === 'string' && (dateVal.indexOf('Prospective') >= 0 || dateVal.indexOf('If Bred') >= 0)) break;

          var treatment = safeStr_(data[mr][1] || '');
          var famacha = data[mr][2] || data[mr][3] || '';
          var fec = data[mr][3] || data[mr][4] || '';
          var notes = safeStr_(data[mr][4] || data[mr][5] || '');

          // Only add if there's a date-like value
          if (dateVal instanceof Date || (typeof dateVal === 'string' && dateVal.match(/\d{4}/))) {
            rows.push([dateVal, '', animalName, '', treatment, '', '', famacha, fec, '', '', '', notes + ' [src: ' + sheet.getName() + ']']);
          }
        }
        break; // Found medical section, done with this sheet
      }
    }
  }

  if (rows.length > 0) {
    // Write to columns M onward (the manual entry section, cols M-S in Health & Treatment Log)
    var startRow = findFirstEmptyRow_(htl, 4, 13); // col M
    htl.getRange(startRow, 13, rows.length, rows[0].length).setValues(rows);
    log_('Wrote ' + rows.length + ' medical records to Health & Treatment Log');
  }
}

// ============================================================
// PHASE 4: PEN ROSTERS → Pen sheets
// ============================================================

function migratePenRosters_() {
  var src = SpreadsheetApp.openById(SOURCE_ID);
  var dest = SpreadsheetApp.openById(DEST_ID);

  var onProp = safeGetSheet_(src, 'On Property');
  if (!onProp) { log_('No "On Property" sheet found, skipping pen rosters'); return; }

  var data = onProp.getDataRange().getValues();
  // Group animals by pen
  var penMap = {};
  for (var r = 1; r < data.length; r++) {
    var name = safeStr_(data[r][3]); // Name column
    var pen = safeStr_(data[r][11] || data[r][10] || data[r][9] || ''); // Pen column varies
    if (!name || !pen) continue;

    // Try to find pen in multiple columns
    for (var c = 0; c < data[r].length; c++) {
      var v = safeStr_(data[r][c]);
      if (v.indexOf('Pen') >= 0 || v === 'Tree Fort' || v === 'Goose') { pen = v; break; }
    }
    if (!pen) continue;

    if (!penMap[pen]) penMap[pen] = [];
    penMap[pen].push([
      data[r][2] || '', // Tag
      data[r][1] || '', // Abbv
      name,
      data[r][4] || '', // Sex
      data[r][5] || '', // Breed
      data[r][6] || '', // Color
      data[r][7] || '', // Weight
      data[r][8] || '', // DOB
      data[r][9] || '', // Sire
      data[r][10] || '', // Dam
      '' // Notes
    ]);
  }

  var penSheetMap = {
    'Pen 1': 'Pen 1', 'Pen 2': 'Pen 2', 'Pen 3': 'Pen 3',
    'Pen 4': 'Pen 4', 'Pen 5': 'Pen 5', 'Pen 6': 'Pen 6',
    'Tree Fort': 'Tree Fort Pen', 'Goose': 'Goose Pen', 'Goose Pen': 'Goose Pen'
  };

  for (var pen in penMap) {
    var destSheetName = penSheetMap[pen] || pen;
    var penSheet = safeGetSheet_(dest, destSheetName);
    if (!penSheet) { log_('Pen sheet not found: ' + destSheetName + ', skipping'); continue; }
    var animals = penMap[pen];
    if (animals.length > 0) {
      penSheet.getRange(5, 1, animals.length, animals[0].length).setValues(animals);
      log_('Wrote ' + animals.length + ' animals to ' + destSheetName);
    }
  }
}

// ============================================================
// PHASE 5: COSTS → Costs & Financials
// ============================================================

function migrateCosts_() {
  var src = SpreadsheetApp.openById(SOURCE_ID);
  var dest = SpreadsheetApp.openById(DEST_ID);

  var costsSheet = safeGetSheet_(src, 'Costs');
  if (!costsSheet) { log_('No Costs sheet found, skipping'); return; }

  var data = costsSheet.getDataRange().getValues();
  var cf = getOrCreateSheet_(dest, 'Costs & Financials');
  var rows = [];

  // Find header row (look for "Sheep Name" or "Tag Number")
  var headerRow = -1;
  for (var r = 0; r < Math.min(data.length, 10); r++) {
    for (var c = 0; c < data[r].length; c++) {
      if (safeStr_(data[r][c]).indexOf('Sheep Name') >= 0 || safeStr_(data[r][c]).indexOf('Tag') >= 0) {
        headerRow = r; break;
      }
    }
    if (headerRow >= 0) break;
  }
  if (headerRow < 0) { log_('No header found in Costs sheet'); return; }

  for (var r = headerRow + 1; r < data.length; r++) {
    if (timeUp_()) { log_('Time guard in costs'); setCheckpoint_('costs'); return; }
    var name = safeStr_(data[r][2] || data[r][1]); // Sheep Name
    if (!name) continue;

    rows.push([
      data[r][1] || '', // Tag
      name,
      data[r][3] || '', // Sex
      data[r][4] || '', // Status
      data[r][5] || '', // DOB
      data[r][6] || '', // Date Acquired
      data[r][7] || '', // Date Sold/Died
      data[r][8] || '', // Months Owned
      data[r][9] || '', // Days Owned
      '', // Total Cost
      data[r][12] || '', // Price Paid
      data[r][13] || '', // Price Received
      '', // Profit/Loss
      data[r][14] || '', // Breed
      data[r][15] || '', // Sire
      data[r][16] || '', // Dam
      data[r][17] || '', // Breeder
      data[r][18] || '', // Babies Total
      data[r][19] || '', // Birth Weight
      data[r][20] || '', // 60-day Weight
      safeStr_(data[r][21] || data[r][22] || '') // Comments
    ]);
  }

  if (rows.length > 0) {
    var startRow = findFirstEmptyRow_(cf, 4, 2); // col B (name)
    cf.getRange(startRow, 1, rows.length, rows[0].length).setValues(rows);
    log_('Wrote ' + rows.length + ' cost records to Costs & Financials');
  }
}

// ============================================================
// PHASE 6: LAMB DATA → Weight History & ADG
// ============================================================

function migrateLambData_() {
  var src = SpreadsheetApp.openById(SOURCE_ID);
  var dest = SpreadsheetApp.openById(DEST_ID);

  var lambSheet = safeGetSheet_(src, 'Lamb Data');
  if (!lambSheet) { log_('No Lamb Data sheet found, skipping'); return; }

  var data = lambSheet.getDataRange().getValues();
  var wh = getOrCreateSheet_(dest, 'Weight History & ADG');
  var rows = [];

  // Find the data header row (contains "Lamb ID", "Ewe ID", etc.)
  var headerRow = -1;
  for (var r = 0; r < Math.min(data.length, 15); r++) {
    for (var c = 0; c < data[r].length; c++) {
      if (safeStr_(data[r][c]).indexOf('Lamb ID') >= 0) { headerRow = r; break; }
    }
    if (headerRow >= 0) break;
  }
  if (headerRow < 0) { log_('No header found in Lamb Data'); return; }

  for (var r = headerRow + 1; r < data.length; r++) {
    var lambId = data[r][1];
    if (lambId === '' || lambId === null) continue;

    rows.push([
      data[r][0] || '', // #
      lambId, // Lamb ID
      data[r][2] || '', // Ewe ID
      data[r][3] || '', // Ewe Age
      data[r][4] || '', // Ram ID
      data[r][5] || '', // Birth Date
      data[r][6] || '', // Sex
      data[r][7] || '', // Birth/Rearing Type
      data[r][8] || '', // Birth Weight
      data[r][9] || '', // Weaning Date
      data[r][10] || '', // Weaning Weight
      data[r][11] || '', // Weaning Age (days)
      data[r][12] || '', // Weaning Age Group
      data[r][13] || '', // WDA
      data[r][14] || '', // ADG
      data[r][15] || '', // Age Corrected WW
      data[r][16] || '', // Adj WW
      data[r][17] || ''  // Adj WW Ratio
    ]);
  }

  if (rows.length > 0) {
    var startRow = findFirstEmptyRow_(wh, 2, 1);
    // Write header first if sheet is empty
    if (startRow <= 2) {
      var headers = ['#', 'Lamb ID', 'Ewe ID', 'Ewe Age', 'Ram ID', 'Birth Date', 'Sex',
        'Birth/Rearing Type', 'Birth Wt', 'Weaning Date', 'Wng Wt', 'Wng Age',
        'Wng Age Group', 'WDA', 'ADG', 'Age Corr WW', 'Adj WW', 'Adj WW Ratio'];
      wh.getRange(1, 1, 1, headers.length).setValues([headers]);
      startRow = 2;
    }
    wh.getRange(startRow, 1, rows.length, rows[0].length).setValues(rows);
    log_('Wrote ' + rows.length + ' lamb records to Weight History & ADG');
  }
}

// ============================================================
// PHASE 7: WEIGHTS AND AVERAGES
// ============================================================

function migrateWeights_() {
  var src = SpreadsheetApp.openById(SOURCE_ID);
  var dest = SpreadsheetApp.openById(DEST_ID);

  var waSrc = safeGetSheet_(src, 'Weights and Averages');
  if (!waSrc) { log_('No Weights and Averages sheet, skipping'); return; }

  var data = waSrc.getDataRange().getValues();
  var wh = getOrCreateSheet_(dest, 'Weight History & ADG');

  // Find a spot below the lamb data
  var startRow = findFirstEmptyRow_(wh, 1, 1) + 2; // Leave a gap

  // Write section header
  wh.getRange(startRow, 1).setValue('WEIGHTS AND AVERAGES — FROM SOURCE');
  startRow++;

  // Copy all non-empty rows
  var rows = [];
  for (var r = 0; r < data.length; r++) {
    var hasData = false;
    for (var c = 0; c < data[r].length; c++) {
      if (data[r][c] !== '' && data[r][c] !== null) { hasData = true; break; }
    }
    if (hasData) rows.push(data[r].slice(0, 15)); // Cap at 15 columns
  }

  if (rows.length > 0) {
    wh.getRange(startRow, 1, rows.length, rows[0].length).setValues(rows);
    log_('Wrote ' + rows.length + ' weight rows to Weight History & ADG');
  }
}

// ============================================================
// PHASE 8: EWE DATA + RAM DATA → Active Ewes / Active Rams
// ============================================================

function migrateEweRamData_() {
  var src = SpreadsheetApp.openById(SOURCE_ID);
  var dest = SpreadsheetApp.openById(DEST_ID);

  // Ewe Data
  var eweSrc = safeGetSheet_(src, 'Ewe Data');
  if (eweSrc) {
    var data = eweSrc.getDataRange().getValues();
    var ae = getOrCreateSheet_(dest, 'Active Ewes');
    var rows = [];
    var headerRow = -1;
    for (var r = 0; r < Math.min(data.length, 10); r++) {
      for (var c = 0; c < data[r].length; c++) {
        if (safeStr_(data[r][c]).indexOf('Ewe ID') >= 0 || safeStr_(data[r][c]).indexOf('Ewe Name') >= 0) {
          headerRow = r; break;
        }
      }
      if (headerRow >= 0) break;
    }
    if (headerRow >= 0) {
      for (var r = headerRow + 1; r < data.length; r++) {
        var id = safeStr_(data[r][1]);
        if (!id) continue;
        rows.push([
          data[r][0] || '', id, '', data[r][2] || '', '', data[r][3] || '',
          '', '', '', data[r][7] || '', '', safeStr_(data[r][5] || '') + '/' + safeStr_(data[r][6] || '')
        ]);
      }
      if (rows.length > 0) {
        var startRow = findFirstEmptyRow_(ae, 5, 2);
        ae.getRange(startRow, 1, rows.length, rows[0].length).setValues(rows);
        log_('Wrote ' + rows.length + ' ewe records to Active Ewes');
      }
    }
  }

  // Ram Data
  var ramSrc = safeGetSheet_(src, 'Ram Data');
  if (ramSrc) {
    var data = ramSrc.getDataRange().getValues();
    var ar = getOrCreateSheet_(dest, 'Active Rams');
    var rows = [];
    var headerRow = -1;
    for (var r = 0; r < Math.min(data.length, 10); r++) {
      for (var c = 0; c < data[r].length; c++) {
        if (safeStr_(data[r][c]).indexOf('Ram ID') >= 0 || safeStr_(data[r][c]).indexOf('Ram Name') >= 0) {
          headerRow = r; break;
        }
      }
      if (headerRow >= 0) break;
    }
    if (headerRow >= 0) {
      for (var r = headerRow + 1; r < data.length; r++) {
        var id = safeStr_(data[r][1]);
        if (!id) continue;
        rows.push([
          data[r][0] || '', id, '', data[r][2] || '', '', data[r][3] || '',
          '', '', '', '', '', safeStr_(data[r][5] || '') + '/' + safeStr_(data[r][6] || '')
        ]);
      }
      if (rows.length > 0) {
        var startRow = findFirstEmptyRow_(ar, 5, 2);
        ar.getRange(startRow, 1, rows.length, rows[0].length).setValues(rows);
        log_('Wrote ' + rows.length + ' ram records to Active Rams');
      }
    }
  }
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

function getAnimalSheetNames_(ss) {
  var skip = [
    'Manatee Creek 2025', 'Manatee Creek (Old)', 'Master', 'Master (1)',
    'Weights and Averages', 'Breeding Plans for 24', 'Possibile Lambs',
    'Potential Offspring', 'Sheep Weight Calculator', 'Template', 'Pen Template',
    'Lamb Data', 'Ram Data', 'Ewe Data', 'Summary', 'User Guide', 'Config',
    '2022 30 day weights', 'On Property', 'Costs', 'Pedigree_Viewer',
    'Pedigree Name', 'Pedigree Tattoo', 'Pedigree Name (1)', 'Pedigree Tattoo (1)',
    'Tables', 'EXPORT_VALUES',
    // Pen sheets
    'Pen 1', 'Pen 2', 'Pen 1 (2024) ', 'Pen 1 (2024)', 'Pen 2 (2024)',
    'Pen 3 - Sam (5 Sheep)', 'Pen 4 - Southdown Ram (7 Sheep)',
    'Pen 5 - Rocky (5 sheep)', 'Pen 6 - Rocky (4 Sheep)',
    'Pen 6 - Fat Tail', '2024 Pen 4 (Kelsier)',
    // Scratch sheets
    'Sheet74', 'Sheet75', 'Sheet79', 'Sheet81', 'Sheet83', 'Sheet84', 'Sheet87'
  ];
  var sheets = ss.getSheets();
  var result = [];
  for (var i = 0; i < sheets.length; i++) {
    var name = sheets[i].getName();
    if (skip.indexOf(name) < 0 && skip.indexOf(name.trim()) < 0) {
      result.push(sheets[i]);
    }
  }
  return result;
}

function getOrCreateSheet_(ss, name) {
  var sheet = ss.getSheetByName(name);
  if (!sheet) sheet = ss.insertSheet(name);
  return sheet;
}

function safeGetSheet_(ss, name) {
  return ss.getSheetByName(name);
}

function safeStr_(val) {
  if (val === null || val === undefined) return '';
  var s = String(val).trim();
  // Skip formula references
  if (s.charAt(0) === '=' && s.indexOf('!') >= 0) return '';
  if (s === '#REF!') return '';
  return s;
}

function findFirstEmptyRow_(sheet, startRow, checkCol) {
  var data = sheet.getRange(startRow, checkCol, sheet.getMaxRows() - startRow + 1, 1).getValues();
  for (var i = 0; i < data.length; i++) {
    if (data[i][0] === '' || data[i][0] === null) return startRow + i;
  }
  return startRow + data.length;
}

function timeUp_() {
  return (Date.now() - START_TIME) > TIME_LIMIT_MS;
}

// ============================================================
// CHECKPOINT & LOGGING
// ============================================================

function getCheckpoint_() {
  return PropertiesService.getScriptProperties().getProperty('migrationPhase') || 'identity';
}

function setCheckpoint_(phase) {
  PropertiesService.getScriptProperties().setProperty('migrationPhase', phase);
}

function resetCheckpoint_() {
  PropertiesService.getScriptProperties().deleteProperty('migrationPhase');
}

function log_(msg) {
  var dest = SpreadsheetApp.openById(DEST_ID);
  var logSheet = dest.getSheetByName('Migration Log');
  if (!logSheet) {
    logSheet = dest.insertSheet('Migration Log');
    logSheet.getRange(1, 1, 1, 3).setValues([['Timestamp', 'Message', 'Phase']]);
  }
  var phase = getCheckpoint_();
  logSheet.appendRow([new Date(), msg, phase]);
  Logger.log(msg);
}
