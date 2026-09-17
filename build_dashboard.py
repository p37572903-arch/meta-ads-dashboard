import json
import sys

# Usage: python3 build_dashboard.py [input_data.json] [output_dashboard.html]
in_path = sys.argv[1] if len(sys.argv) > 1 else "data.json"
out_path = sys.argv[2] if len(sys.argv) > 2 else "meta_ads_dashboard.html"

with open(in_path) as f:
    data = json.load(f)

data_json = json.dumps(data, separators=(",", ":"))

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Meta Ads Performance Dashboard</title>
<style>
  :root {
    --surface-1:      #fcfcfb;
    --page-plane:     #f9f9f7;
    --text-primary:   #0b0b0b;
    --text-secondary: #52514e;
    --text-muted:     #898781;
    --gridline:       #e1e0d9;
    --baseline:       #c3c2b7;
    --border:         rgba(11,11,11,0.10);
    --series-1:       #2a78d6; /* blue */
    --series-2:       #1baf7a; /* aqua */
    --good:           #0ca30c;
    --critical:       #d03b3b;
    --card-shadow:    0 1px 2px rgba(11,11,11,0.04), 0 1px 1px rgba(11,11,11,0.03);
    /* categorical slots used as scoring-tier colors (fixed order: blue, aqua, yellow, violet) */
    --tier-1: #2a78d6; --tier-2: #1baf7a; --tier-3: #eda100; --tier-4: #4a3aa7;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --surface-1:      #1a1a19;
      --page-plane:     #0d0d0d;
      --text-primary:   #ffffff;
      --text-secondary: #c3c2b7;
      --text-muted:     #898781;
      --gridline:       #2c2c2a;
      --baseline:       #383835;
      --border:         rgba(255,255,255,0.10);
      --series-1:       #3987e5;
      --series-2:       #199e70;
      --good:           #0ca30c;
      --critical:       #e66767;
      --card-shadow:    0 1px 2px rgba(0,0,0,0.3), 0 1px 1px rgba(0,0,0,0.2);
      --tier-1: #3987e5; --tier-2: #199e70; --tier-3: #c98500; --tier-4: #9085e9;
    }
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0;
    background: var(--page-plane);
    color: var(--text-primary);
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  .wrap { max-width: 1280px; margin: 0 auto; padding: 28px 24px 56px; }
  header.page-header { margin-bottom: 20px; }
  header.page-header h1 { font-size: 22px; font-weight: 700; margin: 0 0 4px; letter-spacing: -0.01em; }
  header.page-header p { font-size: 13.5px; color: var(--text-secondary); margin: 0; }

  /* Filter row */
  .filters {
    display: flex; align-items: flex-start; gap: 10px; flex-wrap: wrap;
    margin-bottom: 10px;
  }
  .filter-group { position: relative; }
  .filter-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); margin: 0 0 6px 2px; }
  .filter-btn {
    display: flex; align-items: center; gap: 8px;
    background: var(--surface-1); color: var(--text-primary);
    border: 1px solid var(--border); border-radius: 8px;
    padding: 9px 12px; font-size: 13.5px; font-family: inherit;
    cursor: pointer; min-width: 190px; box-shadow: var(--card-shadow);
    transition: border-color .15s ease;
  }
  .filter-btn:hover { border-color: var(--baseline); }
  .filter-btn.open { border-color: var(--series-1); }
  .filter-btn .fb-text { flex: 1; text-align: left; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .filter-btn .fb-count {
    background: var(--series-1); color: #fff; border-radius: 999px;
    font-size: 11px; font-weight: 700; padding: 1px 7px; line-height: 16px; min-width: 16px; text-align:center;
  }
  .filter-btn .chev { color: var(--text-muted); font-size: 10px; transition: transform .15s ease; }
  .filter-btn.open .chev { transform: rotate(180deg); }

  .panel {
    position: absolute; top: calc(100% + 6px); left: 0; z-index: 40;
    width: 300px; max-width: 86vw;
    background: var(--surface-1); border: 1px solid var(--border); border-radius: 10px;
    box-shadow: 0 8px 24px rgba(11,11,11,0.14), 0 2px 6px rgba(11,11,11,0.08);
    display: none; flex-direction: column; overflow: hidden;
  }
  .panel.show { display: flex; }
  .panel-search {
    padding: 8px; border-bottom: 1px solid var(--gridline);
  }
  .panel-search input {
    width: 100%; border: 1px solid var(--border); border-radius: 6px;
    padding: 7px 9px; font-size: 13px; font-family: inherit;
    background: var(--page-plane); color: var(--text-primary);
  }
  .panel-search input:focus { outline: 2px solid var(--series-1); outline-offset: -1px; }
  .panel-actions {
    display: flex; gap: 6px; padding: 6px 8px; border-bottom: 1px solid var(--gridline);
  }
  .panel-actions button {
    flex: 1; background: none; border: 1px solid var(--border); border-radius: 6px;
    color: var(--text-secondary); font-size: 12px; font-family: inherit; padding: 5px 6px; cursor: pointer;
  }
  .panel-actions button:hover { background: var(--page-plane); color: var(--text-primary); }
  .panel-list { overflow-y: auto; max-height: 280px; padding: 4px 0; }
  .panel-empty { padding: 16px 12px; font-size: 12.5px; color: var(--text-muted); text-align: center; }
  .opt {
    display: flex; align-items: center; gap: 9px;
    padding: 7px 12px; cursor: pointer; font-size: 13px; color: var(--text-primary);
  }
  .opt:hover { background: var(--page-plane); }
  .opt input[type="checkbox"] { accent-color: var(--series-1); width: 15px; height: 15px; flex-shrink: 0; cursor: pointer; }
  .opt .opt-label { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  .mode-toggle {
    display: inline-flex; background: var(--surface-1); border: 1px solid var(--border); border-radius: 8px;
    padding: 3px; box-shadow: var(--card-shadow);
  }
  .mode-toggle button {
    border: none; background: none; font-family: inherit; font-size: 13px; font-weight: 600;
    padding: 7px 16px; border-radius: 6px; cursor: pointer; color: var(--text-secondary);
  }
  .mode-toggle button.active { background: var(--series-1); color: #fff; }

  .scope-line { font-size: 12.5px; color: var(--text-muted); margin: 4px 2px 4px; }
  .scope-line b { color: var(--text-secondary); font-weight: 600; }
  .compare-line { font-size: 12.5px; color: var(--text-muted); margin: 0 2px 22px; }
  .compare-line b { color: var(--series-1); font-weight: 600; }

  /* KPI grid */
  .kpi-grid {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
  }
  @media (max-width: 980px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 560px) { .kpi-grid { grid-template-columns: 1fr; } }

  .tile {
    background: var(--surface-1); border: 1px solid var(--border); border-radius: 12px;
    padding: 16px 16px 14px; box-shadow: var(--card-shadow);
    display: flex; flex-direction: column; gap: 6px; min-height: 92px; justify-content: center;
  }
  .tile .t-label {
    font-size: 11.5px; font-weight: 600; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: 0.03em;
    display: flex; align-items: center; gap: 6px;
  }
  .tile .t-index {
    display: inline-flex; align-items: center; justify-content: center;
    width: 16px; height: 16px; border-radius: 4px; background: var(--page-plane);
    color: var(--text-muted); font-size: 9.5px; font-weight: 700; flex-shrink: 0;
  }
  .tile .t-value {
    font-size: 24px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.01em;
    font-variant-numeric: proportional-nums;
  }
  .tile .t-sub { font-size: 11.5px; color: var(--text-muted); }

  .tile .t-compare {
    margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--gridline);
    display: flex; flex-direction: column; gap: 6px;
  }
  .t-compare .t-baseline { font-size: 11.5px; color: var(--text-muted); }
  .t-compare .t-baseline b { color: var(--text-secondary); font-weight: 600; }
  .t-badge {
    display: inline-flex; align-items: center; gap: 4px; font-size: 11.5px; font-weight: 700;
    padding: 2px 8px; border-radius: 999px; width: fit-content;
  }
  .t-badge.good { color: var(--good); background: color-mix(in srgb, var(--good) 14%, transparent); }
  .t-badge.bad { color: var(--critical); background: color-mix(in srgb, var(--critical) 14%, transparent); }
  .t-badge.neutral { color: var(--text-muted); background: var(--page-plane); }

  .t-badge-row { display: flex; align-items: center; gap: 8px; }
  .t-rank-inline { font-size: 11.5px; color: var(--text-muted); margin-left: auto; white-space: nowrap; flex-shrink: 0; }
  .t-rank-inline b { color: var(--text-primary); font-weight: 700; }

  /* Mini two-bar comparison chart embedded in each tile */
  .mini-bars { display: flex; flex-direction: column; gap: 4px; }
  .mini-bar-row { display: flex; align-items: center; gap: 6px; }
  .mini-bar-row .mb-label {
    font-size: 9px; color: var(--text-muted); width: 60px; flex-shrink: 0;
    text-transform: uppercase; letter-spacing: 0.01em; line-height: 1.2; white-space: normal;
  }
  .mini-bar-track {
    flex: 1; height: 8px; border-radius: 4px; background: var(--page-plane); overflow: hidden;
  }
  .mini-bar-fill { height: 100%; border-radius: 4px; min-width: 2px; }
  .mini-bar-fill.sel { background: var(--series-1); }
  .mini-bar-fill.base { background: var(--baseline); }
  .mini-bar-row .mb-value {
    font-size: 11px; font-weight: 700; color: var(--text-secondary); min-width: 58px;
    text-align: right; flex-shrink: 0; font-variant-numeric: tabular-nums;
  }

  /* Legend for the recurring Selected vs. Comparison-scope series */
  .compare-legend { display: flex; align-items: center; gap: 18px; font-size: 12px; color: var(--text-secondary); margin: 0 2px 14px; }
  .compare-legend .lg-item { display: flex; align-items: center; gap: 6px; }
  .compare-legend .lg-swatch { width: 10px; height: 10px; border-radius: 3px; display: inline-block; flex-shrink: 0; }
  .compare-legend .lg-swatch.sel { background: var(--series-1); }
  .compare-legend .lg-swatch.base { background: var(--baseline); }

  /* Performance score section */
  .score-section { margin-top: 32px; }
  .score-section h2 { font-size: 15px; font-weight: 700; margin: 0 0 3px; letter-spacing: -0.005em; }
  .score-section .score-sub { font-size: 12px; color: var(--text-muted); margin: 0 0 14px; }

  .score-level-toggle {
    display: inline-flex; background: var(--surface-1); border: 1px solid var(--border); border-radius: 8px;
    padding: 3px; box-shadow: var(--card-shadow); margin-bottom: 14px;
  }
  .score-level-toggle button {
    border: none; background: none; font-family: inherit; font-size: 13px; font-weight: 600;
    padding: 7px 16px; border-radius: 6px; cursor: pointer; color: var(--text-secondary);
  }
  .score-level-toggle button.active { background: var(--series-1); color: #fff; }

  .tier-legend { display: flex; align-items: center; flex-wrap: wrap; gap: 16px; font-size: 12px; color: var(--text-secondary); margin: 0 0 14px; }
  .tier-legend .lg-item { display: flex; align-items: center; gap: 6px; }
  .tier-legend .lg-swatch { width: 10px; height: 10px; border-radius: 3px; display: inline-block; flex-shrink: 0; }
  .tier-legend .lg-swatch.t1 { background: var(--tier-1); }
  .tier-legend .lg-swatch.t2 { background: var(--tier-2); }
  .tier-legend .lg-swatch.t3 { background: var(--tier-3); }
  .tier-legend .lg-swatch.t4 { background: var(--tier-4); }

  .score-table {
    background: var(--surface-1); border: 1px solid var(--border); border-radius: 12px;
    box-shadow: var(--card-shadow); overflow: hidden;
  }
  .score-row {
    display: grid; grid-template-columns: 34px 1fr 240px 56px; align-items: center;
    gap: 14px; padding: 12px 16px; border-bottom: 1px solid var(--gridline);
  }
  .score-row:last-child { border-bottom: none; }
  .score-row.head {
    font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em;
    color: var(--text-muted); background: var(--page-plane);
  }
  .score-rank { font-size: 13px; font-weight: 700; color: var(--text-muted); text-align: center; }
  .score-name-wrap { min-width: 0; }
  .score-name { font-size: 13px; font-weight: 600; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .score-detail { font-size: 11px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px; }
  .score-bar-track {
    height: 14px; border-radius: 4px; background: var(--gridline); overflow: hidden; display: flex;
  }
  .score-bar-seg { height: 100%; }
  .score-bar-seg.t1 { background: var(--tier-1); }
  .score-bar-seg.t2 { background: var(--tier-2); }
  .score-bar-seg.t3 { background: var(--tier-3); }
  .score-bar-seg.t4 { background: var(--tier-4); }
  .score-value { font-size: 14px; font-weight: 700; color: var(--text-primary); text-align: right; font-variant-numeric: tabular-nums; }
  .score-empty { padding: 20px 16px; font-size: 12.5px; color: var(--text-muted); }

  .score-formula {
    margin-top: 14px; font-size: 12px; color: var(--text-secondary); line-height: 1.75;
    background: var(--surface-1); border: 1px solid var(--border); border-radius: 12px; padding: 14px 18px;
  }
  .score-formula .sf-title { font-size: 12.5px; font-weight: 700; color: var(--text-primary); margin-bottom: 10px; }
  .score-formula .sf-tier { margin: 0 0 12px; padding-bottom: 12px; border-bottom: 1px solid var(--gridline); }
  .score-formula .sf-tier:last-of-type { border-bottom: none; padding-bottom: 0; }
  .score-formula .sf-line { font-variant-numeric: tabular-nums; margin: 4px 0; }
  .score-formula .sf-line b { color: var(--text-primary); }
  .score-formula .sf-line.sf-formula { color: var(--text-muted); }
  .score-formula .sf-line.sf-numbers { color: var(--text-secondary); }
  .score-formula .sf-line.sf-note { color: var(--text-muted); font-size: 11.5px; margin-top: 10px; }
  .score-formula .sf-line.sf-total { margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--gridline); color: var(--text-primary); font-weight: 600; }

  .score-methodology {
    margin-top: 14px; font-size: 12px; color: var(--text-muted); line-height: 1.65;
    background: var(--surface-1); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px;
  }
  .score-methodology h4 { font-size: 12.5px; font-weight: 700; color: var(--text-primary); margin: 12px 0 4px; }
  .score-methodology h4:first-child { margin-top: 0; }
  .score-methodology b { color: var(--text-secondary); }

  footer.note { margin-top: 26px; font-size: 12px; color: var(--text-muted); line-height: 1.6; }
  footer.note code { background: var(--surface-1); border: 1px solid var(--border); border-radius: 4px; padding: 1px 5px; }

  /* Collapsible worked-example / methodology sections — collapsed by default */
  .score-collapsible {
    margin-top: 14px; background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 12px; box-shadow: var(--card-shadow); overflow: hidden;
  }
  .score-collapsible > summary {
    cursor: pointer; list-style: none; padding: 14px 18px; font-size: 12.5px; font-weight: 700;
    color: var(--text-primary); display: flex; align-items: center; gap: 8px; user-select: none;
  }
  .score-collapsible > summary::-webkit-details-marker { display: none; }
  .score-collapsible > summary::before {
    content: '▸'; color: var(--text-muted); font-size: 11px; transition: transform .15s ease;
  }
  .score-collapsible[open] > summary::before { transform: rotate(90deg); }
  .score-collapsible[open] > summary { border-bottom: 1px solid var(--gridline); }
  .score-collapsible .score-formula, .score-collapsible .score-methodology, .score-collapsible footer.note {
    margin: 0; border: none; box-shadow: none; border-radius: 0; padding: 14px 18px;
  }
  .footer-collapsible { margin-top: 26px; }

  /* Top bar: date range + metrics multi-select (view-independent) */
  .top-filters { margin-bottom: 14px; }
  .date-range-inputs {
    display: flex; align-items: center; gap: 8px; background: var(--surface-1);
    border: 1px solid var(--border); border-radius: 8px; padding: 6px 10px; box-shadow: var(--card-shadow);
  }
  .date-input {
    border: none; background: none; font-family: inherit; font-size: 13px; color: var(--text-primary);
    min-width: 0;
  }
  .date-input::-webkit-calendar-picker-indicator { filter: var(--date-icon-filter, none); cursor: pointer; }
  @media (prefers-color-scheme: dark) { .date-input { --date-icon-filter: invert(1); } }
  :root[data-theme="dark"] .date-input { --date-icon-filter: invert(1); }
  .date-sep { color: var(--text-muted); font-size: 12px; }

  /* Chat assistant */
  .chat-fab {
    position: fixed; top: calc(20px + env(safe-area-inset-top, 0px)); right: 20px; z-index: 40;
    width: 46px; height: 46px; border-radius: 50%; border: 1px solid var(--border);
    background: var(--series-1); color: #fff; font-size: 19px; cursor: pointer;
    box-shadow: 0 2px 8px rgba(11,11,11,0.18); display: flex; align-items: center; justify-content: center;
  }
  .chat-fab:hover { filter: brightness(1.08); }
  .chat-panel {
    position: fixed; top: calc(74px + env(safe-area-inset-top, 0px)); right: 20px; z-index: 41;
    width: min(360px, calc(100vw - 32px)); max-height: min(70vh, 560px);
    background: var(--surface-1); border: 1px solid var(--border); border-radius: 14px;
    box-shadow: 0 8px 28px rgba(11,11,11,0.22); display: flex; flex-direction: column; overflow: hidden;
  }
  .chat-header {
    padding: 12px 14px; font-size: 13px; font-weight: 700; color: var(--text-primary);
    border-bottom: 1px solid var(--gridline); display: flex; align-items: center; justify-content: space-between;
    flex-shrink: 0;
  }
  .chat-close { border: none; background: none; color: var(--text-muted); font-size: 14px; cursor: pointer; padding: 2px 6px; }
  .chat-messages { flex: 1; overflow-y: auto; padding: 12px 14px; display: flex; flex-direction: column; gap: 8px; min-height: 120px; }
  .chat-msg { font-size: 12.5px; line-height: 1.55; padding: 8px 11px; border-radius: 10px; max-width: 92%; white-space: pre-wrap; }
  .chat-msg-bot { background: var(--page-plane); color: var(--text-secondary); align-self: flex-start; }
  .chat-msg-user { background: var(--series-1); color: #fff; align-self: flex-end; }
  .chat-msg-error { color: var(--critical); background: color-mix(in srgb, var(--critical) 12%, transparent); }
  .chat-suggestions { display: flex; flex-wrap: wrap; gap: 6px; padding: 0 14px 10px; flex-shrink: 0; }
  .chat-suggestions .chip {
    font-size: 11px; border: 1px solid var(--border); background: var(--page-plane); color: var(--text-secondary);
    border-radius: 999px; padding: 5px 10px; cursor: pointer;
  }
  .chat-suggestions .chip:hover { border-color: var(--series-1); color: var(--text-primary); }
  .chat-form { display: flex; gap: 8px; padding: 10px 14px; border-top: 1px solid var(--gridline); flex-shrink: 0; }
  .chat-form input {
    flex: 1; min-width: 0; border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px;
    font-family: inherit; font-size: 12.5px; background: var(--page-plane); color: var(--text-primary);
  }
  .chat-form input:focus { outline: 2px solid var(--series-1); outline-offset: -1px; }
  .chat-form button {
    border: none; background: var(--series-1); color: #fff; border-radius: 8px; padding: 8px 14px;
    font-family: inherit; font-size: 12.5px; font-weight: 600; cursor: pointer; flex-shrink: 0;
  }
  .chat-form button:disabled { opacity: 0.6; cursor: default; }
  @media (max-width: 560px) {
    .chat-fab { top: calc(12px + env(safe-area-inset-top, 0px)); right: 12px; }
    .chat-panel { top: calc(64px + env(safe-area-inset-top, 0px)); right: 8px; }
  }
  /* Belt-and-braces: guarantee the [hidden] attribute wins over the display:
     rules above regardless of whether a wrapping page supplies its own
     [hidden]{display:none} reset. */
  .chat-fab[hidden], .chat-panel[hidden] { display: none !important; }
</style>
</head>
<body>
<div class="wrap">
  <header class="page-header">
    <h1>Meta Ads Performance Dashboard</h1>
    <p id="page-subtitle">Campaign / Ad set / Ad level data</p>
  </header>

  <div class="filters top-filters">
    <div class="filter-group" id="fg-date">
      <div class="filter-label">Date range</div>
      <div class="date-range-inputs">
        <input type="date" id="date-from" class="date-input">
        <span class="date-sep">–</span>
        <input type="date" id="date-to" class="date-input">
      </div>
    </div>
    <div class="filter-group" id="fg-metrics">
      <div class="filter-label">Metrics</div>
      <button class="filter-btn" id="btn-metrics"><span class="fb-text">Metrics</span><span class="fb-count" id="cnt-metrics"></span><span class="chev">▾</span></button>
      <div class="panel" id="panel-metrics"></div>
    </div>
  </div>

  <div class="filters" id="filters-campaign">
    <div class="filter-group" id="fg-campaign">
      <div class="filter-label">Campaign</div>
      <button class="filter-btn" id="btn-campaign"><span class="fb-text">All campaigns</span><span class="fb-count" id="cnt-campaign"></span><span class="chev">▾</span></button>
      <div class="panel" id="panel-campaign"></div>
    </div>
    <div class="filter-group" id="fg-adset">
      <div class="filter-label">Ad set</div>
      <button class="filter-btn" id="btn-adset"><span class="fb-text">All ad sets</span><span class="fb-count" id="cnt-adset"></span><span class="chev">▾</span></button>
      <div class="panel" id="panel-adset"></div>
    </div>
    <div class="filter-group" id="fg-ad">
      <div class="filter-label">Ad</div>
      <button class="filter-btn" id="btn-ad"><span class="fb-text">All ads</span><span class="fb-count" id="cnt-ad"></span><span class="chev">▾</span></button>
      <div class="panel" id="panel-ad"></div>
    </div>
  </div>

  <div id="main-content">
  <div class="scope-line" id="scope-line"></div>
  <div class="compare-line" id="compare-line"></div>
  <div class="compare-legend" id="compare-legend"></div>

  <div class="kpi-grid" id="kpi-grid"></div>

  <div class="score-section">
    <h2>Performance score</h2>
    <p class="score-sub" id="score-sub"></p>

    <div class="score-level-toggle" id="score-level-toggle-campaign">
      <button id="score-lvl-campaign" class="active" data-level="campaign">Campaigns</button>
      <button id="score-lvl-adset" data-level="adset">Ad sets</button>
      <button id="score-lvl-ad" data-level="ad">Ads</button>
    </div>

    <div class="tier-legend">
      <div class="lg-item"><span class="lg-swatch t1"></span>ROAS + Revenue (40%)</div>
      <div class="lg-item"><span class="lg-swatch t2"></span>AOV + Adds to cart (25%)</div>
      <div class="lg-item"><span class="lg-swatch t3"></span>CTR + Impressions (20%)</div>
      <div class="lg-item"><span class="lg-swatch t4"></span>Everything else (15%)</div>
    </div>

    <div class="score-table" id="score-table"></div>

    <details class="score-collapsible">
      <summary>Worked example — how the top-ranked entity got its score</summary>
      <div class="score-formula" id="score-formula"></div>
    </details>

    <details class="score-collapsible">
      <summary>How the score works</summary>
    <div class="score-methodology">
      <h4>How the score works</h4>
      A 0–100 score is calculated for every entity at the level you pick above — campaigns, ad sets, or ads in
      Campaign view; product numbers, day types, creator numbers, or concept numbers in Product view — grouped
      from your current filter selection, so you can rank them against each other. It's a weighted blend of
      four priority tiers, exactly as ordered:
      <b>ROAS and Revenue matter most (40% combined)</b> — ROAS is the purest read on whether the money spent
      is actually paying back, and Revenue is the bottom-line outcome, so between them they set the largest
      share of the score. <b>AOV and Adds to cart come next (25% combined)</b> — a strong AOV signals the
      selection is attracting higher-value orders, and adds to cart is the clearest sign that mid-funnel
      demand exists even before a purchase closes. <b>CTR and Impressions follow (20% combined)</b> — CTR
      shows the creative/targeting is compelling enough to earn a click, and Impressions reflects how much
      reach the entity actually had a chance to prove itself on. <b>Everything else fills the remaining 15%</b>
      — spend, link clicks, and orders each contribute a small, direct share, and the rest of the funnel
      metrics (reach, hook/hold rate, LPVR, ATCR, checkout rates, CVR, CPM, 3 sec views, ThruPlays, landing
      page views, checkouts initiated) are averaged into one supporting component.
      <h4>Why saliency is built in, not bolted on</h4>
      Revenue, Amount spent, Impressions, Link clicks, and Orders are scored by <b>saliency</b> — each
      entity's share of the total for that metric across everything being compared — rather than by
      normalizing them like a rate. This is deliberate: a tiny ad with one lucky sale can post a spectacular
      ROAS or AOV, but if it only carried 0.1% of total spend and impressions, its saliency scores stay low
      and pull the overall score back down. An entity only scores well overall if it is both <i>efficient</i>
      (high ROAS, AOV, CTR relative to peers) <i>and</i> actually carries real weight in the total spend,
      revenue, impressions, clicks, and orders — so the leaderboard can't be topped by statistically thin
      outliers.
      <h4>How each number becomes a 0–100 score</h4>
      ROAS, AOV, adds to cart, CTR, and the "everything else" metrics are <b>min–max normalized</b> against
      only the entities currently being compared (the best performer scores 100, the weakest scores 0, and
      CPM is inverted since lower is better). Revenue, spend, impressions, link clicks, and orders are scored
      as their <b>% share of the combined total</b> for that metric across the same set. The four tier scores
      are then combined using the weights above. Frequency is left out of the score entirely — as in the
      tiles above, there's no agreed "better" direction for it. Entities with a zero denominator (e.g. no
      landing page views) score 0 on the affected metric rather than being excluded.
    </div>
    </details>
  </div>

  <details class="score-collapsible footer-collapsible">
    <summary>How the numbers are calculated</summary>
    <footer class="note">
      Numbers are summed across every row matching the current filters. Amount spent, revenue, reach,
      impressions, 3 sec views, ThruPlays, link clicks and landing page views are shown in lakhs (2 decimals);
      adds to cart, checkouts initiated and orders are shown in thousands (1 decimal); average order value is
      a whole number. Frequency is recalculated as total impressions ÷ total reach, and Average Order Value as
      total revenue ÷ total orders, rather than averaging the per-row values — this keeps aggregates correct
      when more than one ad is selected. Ratio metrics are calculated from those same summed totals (not
      averaged row-by-row): CPM, hook rate, hold rate, LPVR, ATCR, checkout initiated rate, checkout completion
      rate and AOV are rounded to whole numbers; CTR, ROAS and CVR keep 2 decimals. <code>–</code> means the
      denominator is zero for the current selection.
      <br><br>
      <b>Comparison:</b> each tile also shows a comparison figure, chosen by how far you've narrowed the
      filters — select specific campaign(s) and it compares to all campaigns; narrow to specific ad set(s)
      within a campaign and it compares to all ad sets in that campaign; narrow to specific ad(s) within an ad
      set and it compares to all ads in that ad set. For summable volume metrics (spend, revenue, reach,
      impressions, 3 sec views, ThruPlays, link clicks, landing page views, adds to cart, checkouts initiated,
      orders) the comparison shows the total for that scope and this selection's <b>share</b> of it — a share
      isn't inherently good or bad, so it's shown as two neutral bars (this selection vs. the scope total). For
      rate/derived metrics the comparison shows two bars scaled to the larger of the pair, plus a badge for how
      far the selection is above/below the scope — green when that's the better direction, red when it's worse
      (lower CPM/CPA/CPC/Cost per ATC is better; higher is better everywhere else). Frequency has no agreed
      "better" direction, so its bars are shown without a colored badge. When every filter is at "All," there's
      nothing to compare against, so the bars and badge are omitted.
    </footer>
  </details>
  </div>
</div>

<button class="chat-fab" id="chat-fab" hidden aria-label="Ask about your data">💬</button>
<div class="chat-panel" id="chat-panel" hidden>
  <div class="chat-header">
    <span>Ask about your data</span>
    <button class="chat-close" id="chat-close" aria-label="Close">✕</button>
  </div>
  <div class="chat-messages" id="chat-messages">
    <div class="chat-msg chat-msg-bot">Ask me things like "which creatives are good", "which campaigns need improvement", or "which campaigns are getting worse over time" — answers are grounded in the numbers currently on screen.</div>
  </div>
  <div class="chat-suggestions" id="chat-suggestions">
    <button type="button" class="chip" data-q="Which creatives are performing best right now, and why?">Best creatives</button>
    <button type="button" class="chip" data-q="Which campaigns need improvement, and what's dragging them down?">Needs improvement</button>
    <button type="button" class="chip" data-q="Which campaigns are getting worse over time?">Worsening trend</button>
  </div>
  <form class="chat-form" id="chat-form">
    <input type="text" id="chat-input" placeholder="Ask a question…" autocomplete="off">
    <button type="submit" id="chat-send">Send</button>
  </form>
</div>

<script>
const DATA = __DATA_JSON__;
document.getElementById('page-subtitle').textContent =
  DATA.length + ' row' + (DATA.length === 1 ? '' : 's') +
  (DATA.some(d => d.date) ? '' : ' · no date column found in this export, date filter disabled');

// ---------- Build lookup maps ----------
const campaigns = [...new Set(DATA.map(d => d.c))].sort();
const campToAdsets = {};
const adsetToAds = {};
const adsetToCamp = {};
for (const d of DATA) {
  (campToAdsets[d.c] ??= new Set()).add(d.s);
  (adsetToAds[d.s] ??= new Set()).add(d.a);
  adsetToCamp[d.s] = d.c;
}

// ---------- State ----------
const viewMode = 'campaign'; // Product view was removed — Campaign view is the only mode now.
let selCampaigns = new Set(campaigns);
let selAdsets = new Set(Object.keys(adsetToAds));
let selAds = new Set(DATA.map(d => d.a));
let selMetrics = new Set(); // populated once ALL_METRICS/DEFAULT_METRIC_KEYS are defined below
// ---------- Date range filter state ----------
// Populated after DATA loads (see wiring below); null when the export has no
// usable date column at all, in which case every row is always "in range".
let allDates = [...new Set(DATA.map(d => d.date).filter(Boolean))].sort();
let dateFrom = allDates.length ? allDates[allDates.length - 1] : null;
let dateTo = allDates.length ? allDates[allDates.length - 1] : null;
function inDateRange(d) {
  if (dateFrom === null || dateTo === null || !d.date) return true;
  return d.date >= dateFrom && d.date <= dateTo;
}

function availableAdsets(camps) {
  const s = new Set();
  for (const c of camps) for (const a of (campToAdsets[c] || [])) s.add(a);
  return s;
}
function availableAds(adsets) {
  const s = new Set();
  for (const a of adsets) for (const x of (adsetToAds[a] || [])) s.add(x);
  return s;
}

// The fully filtered row set — campaign/ad set/ad filters AND the date range filter both apply.
function getFilteredRows() {
  return DATA.filter(d => selCampaigns.has(d.c) && selAdsets.has(d.s) && selAds.has(d.a) && inDateRange(d));
}

// Sorts plain names alphabetically (unchanged from before) but sorts purely-numeric
// option strings ("01".."266") in numeric order, with non-numeric sentinels like
// "No creator" / "No concept" pinned to the top — plain .sort() would put "100" before
// "99" since it compares character by character.
function naturalCompare(a, b) {
  const aNum = /^\d+$/.test(a), bNum = /^\d+$/.test(b);
  if (aNum && bNum) return parseInt(a, 10) - parseInt(b, 10);
  if (aNum !== bNum) return aNum ? 1 : -1;
  return a.localeCompare(b);
}

// Tracks the upward-backfill "flush" for whichever dropdown panel is currently
// open (null if none, or if the open panel has no upward backfill to defer).
// Only one panel can be open at a time, so a single shared slot is enough.
// See makeDropdown's `onClose` param for why this is deferred rather than run
// on every checkbox click.
let openPanelFlush = null;

// ---------- Generic multi-select dropdown ----------
function makeDropdown({ btnId, panelId, getAllOptions, getSelected, setSelected, onCommit, onClose, singularLabel, pluralLabel }) {
  const btn = document.getElementById(btnId);
  const panel = document.getElementById(panelId);
  let searchTerm = '';

  // Prevent clicks inside the panel (which re-render its innerHTML, detaching
  // the original event target) from bubbling to the document click-outside handler.
  panel.addEventListener('click', (e) => e.stopPropagation());

  // `onClose` (only provided by dropdowns that backfill ancestor filters) runs
  // once, when this panel actually closes — not on every checkbox click. This
  // matters because the backfill narrows ancestor filters that this panel's
  // OWN getAllOptions() depends on (e.g. the Ad panel's list is
  // availableAds(selAdsets), and the Ad panel's own backfill narrows
  // selAdsets); running it live would shrink the option list out from under
  // the user mid-selection, making it impossible to then pick a second item
  // from a different ad set/campaign/etc. in the same session — exactly the
  // "two options in low hierarchy" case. Deferring to close means the whole
  // multi-selection happens against a stable option list, and the backfill
  // reflects the union once the user is done.
  function flush() { if (onClose) onClose(); }
  function close() {
    if (panel.classList.contains('show') && openPanelFlush === flush) { flush(); openPanelFlush = null; }
    panel.classList.remove('show'); btn.classList.remove('open');
  }
  function toggleOpen() {
    const willOpen = !panel.classList.contains('show');
    if (openPanelFlush) { openPanelFlush(); openPanelFlush = null; }
    document.querySelectorAll('.panel.show').forEach(p => { p.classList.remove('show'); });
    document.querySelectorAll('.filter-btn.open').forEach(b => b.classList.remove('open'));
    if (willOpen) {
      render(); panel.classList.add('show'); btn.classList.add('open');
      if (onClose) openPanelFlush = flush;
    }
  }
  btn.addEventListener('click', (e) => { e.stopPropagation(); toggleOpen(); });

  function render() {
    const all = [...getAllOptions()].sort(naturalCompare);
    const selected = getSelected();
    const term = searchTerm.trim().toLowerCase();
    const filtered = term ? all.filter(o => o.toLowerCase().includes(term)) : all;

    panel.innerHTML = '';

    const searchWrap = document.createElement('div');
    searchWrap.className = 'panel-search';
    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = 'Search ' + pluralLabel + '…';
    input.value = searchTerm;
    input.addEventListener('input', (e) => { searchTerm = e.target.value; render(); });
    searchWrap.appendChild(input);
    panel.appendChild(searchWrap);

    const actions = document.createElement('div');
    actions.className = 'panel-actions';
    const allBtn = document.createElement('button');
    allBtn.textContent = 'Select all';
    allBtn.addEventListener('click', () => {
      const s = new Set(selected);
      filtered.forEach(o => s.add(o));
      setSelected(s);
      onCommit();
      render();
    });
    const noneBtn = document.createElement('button');
    noneBtn.textContent = 'Clear';
    noneBtn.addEventListener('click', () => {
      const s = new Set(selected);
      filtered.forEach(o => s.delete(o));
      setSelected(s);
      onCommit();
      render();
    });
    actions.appendChild(allBtn);
    actions.appendChild(noneBtn);
    panel.appendChild(actions);

    const list = document.createElement('div');
    list.className = 'panel-list';
    if (filtered.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'panel-empty';
      empty.textContent = 'No matches.';
      list.appendChild(empty);
    } else {
      for (const opt of filtered) {
        const row = document.createElement('label');
        row.className = 'opt';
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.checked = selected.has(opt);
        cb.addEventListener('change', () => {
          const s = new Set(getSelected());
          if (cb.checked) s.add(opt); else s.delete(opt);
          setSelected(s);
          onCommit();
          render();
        });
        const lbl = document.createElement('span');
        lbl.className = 'opt-label';
        lbl.textContent = opt;
        row.appendChild(cb);
        row.appendChild(lbl);
        list.appendChild(row);
      }
    }
    panel.appendChild(list);
    updateButtonLabel();
  }

  function updateButtonLabel() {
    const all = getAllOptions();
    const selected = getSelected();
    const total = all.size;
    const n = [...selected].filter(x => all.has(x)).length;
    const textEl = btn.querySelector('.fb-text');
    const countEl = document.getElementById(btnId.replace('btn-', 'cnt-'));
    if (n === total) {
      textEl.textContent = 'All ' + pluralLabel;
      countEl.textContent = '';
      countEl.style.display = 'none';
    } else if (n === 0) {
      textEl.textContent = 'No ' + pluralLabel + ' selected';
      countEl.style.display = 'none';
    } else if (n === 1) {
      textEl.textContent = [...selected].find(x => all.has(x));
      countEl.style.display = 'none';
    } else {
      textEl.textContent = n + ' ' + pluralLabel + ' selected';
      countEl.textContent = n;
      countEl.style.display = 'inline-block';
    }
  }

  document.addEventListener('click', (e) => {
    if (!panel.contains(e.target) && e.target !== btn && !btn.contains(e.target)) close();
  });

  return { render, updateButtonLabel, close };
}

// ---------- Wire up the three cascading dropdowns ----------
const campaignDD = makeDropdown({
  btnId: 'btn-campaign', panelId: 'panel-campaign',
  getAllOptions: () => new Set(campaigns),
  getSelected: () => selCampaigns,
  setSelected: (s) => { selCampaigns = s; },
  onCommit: () => {
    const avail = availableAdsets(selCampaigns);
    selAdsets = new Set(avail);
    const availA = availableAds(selAdsets);
    selAds = new Set(availA);
    adsetDD.render();
    adDD.render();
    renderAll();
  },
  singularLabel: 'campaign', pluralLabel: 'campaigns'
});

const adsetDD = makeDropdown({
  btnId: 'btn-adset', panelId: 'panel-adset',
  getAllOptions: () => availableAdsets(selCampaigns),
  getSelected: () => selAdsets,
  setSelected: (s) => { selAdsets = s; },
  onCommit: () => {
    // Downward: auto-select every ad under the newly chosen ad set(s). Runs
    // live, on every checkbox click.
    const availA = availableAds(selAdsets);
    selAds = new Set(availA);
    adDD.render();
    renderAll();
  },
  onClose: () => {
    // Upward: narrow Campaign to exactly the campaign(s) that own the selected
    // ad set(s) — picking an ad set directly (without touching Campaign first)
    // should surface its parent campaign(s) rather than leaving "all" selected.
    // Deferred until the panel closes (rather than run per checkbox click) so
    // that while it's open, this dropdown's own option list
    // (availableAdsets(selCampaigns)) doesn't shrink out from under a user
    // picking a second ad set from a different campaign in the same session.
    // Skipped when nothing is selected (e.g. user just clicked "Clear") so
    // clearing this filter can't collapse Campaign to empty and lock the ad
    // set dropdown's own options out at zero with no way back in.
    if (selAdsets.size > 0) {
      selCampaigns = new Set([...selAdsets].map(s => adsetToCamp[s]).filter(Boolean));
      campaignDD.render();
      renderAll();
    }
  },
  singularLabel: 'ad set', pluralLabel: 'ad sets'
});

const adDD = makeDropdown({
  btnId: 'btn-ad', panelId: 'panel-ad',
  getAllOptions: () => availableAds(selAdsets),
  getSelected: () => selAds,
  setSelected: (s) => { selAds = s; },
  onCommit: () => {
    renderAll();
  },
  onClose: () => {
    // Upward: picking ad(s) directly should surface their own ad set(s) and
    // campaign(s) — e.g. selecting one specific ad selects its respective ad
    // set and campaign, rather than leaving those filters at "all". Deferred
    // until the panel closes so this dropdown's own option list
    // (availableAds(selAdsets)) stays stable while multiple ads — possibly
    // from different ad sets/campaigns — are being picked in one session.
    // Skipped when nothing is selected so clearing this filter can't collapse
    // its own ancestors (and therefore its own available options) to zero.
    if (selAds.size > 0) {
      const matchingRows = DATA.filter(d => selAds.has(d.a));
      selAdsets = new Set(matchingRows.map(d => d.s));
      selCampaigns = new Set(matchingRows.map(d => d.c));
      adsetDD.render();
      campaignDD.render();
      renderAll();
    }
  },
  singularLabel: 'ad', pluralLabel: 'ads'
});


// ---------- Metrics filter: which tiles show, multi-select checkbox dropdown ----------
// Reuses the same generic makeDropdown factory as the campaign/product filters.
// Option identity is each metric's LABEL (unique across ALL_METRICS, same
// pattern as every other dropdown using plain display strings as identity).
const metricsDD = makeDropdown({
  btnId: 'btn-metrics', panelId: 'panel-metrics',
  getAllOptions: () => new Set(ALL_METRICS.map(m => m.label)),
  getSelected: () => new Set([...selMetrics].map(k => METRICS_BY_KEY.get(k).label)),
  setSelected: (labelSet) => {
    const labelToKey = new Map(ALL_METRICS.map(m => [m.label, m.key]));
    selMetrics = new Set([...labelSet].map(l => labelToKey.get(l)).filter(Boolean));
  },
  onCommit: () => renderAll(),
  singularLabel: 'metric', pluralLabel: 'metrics'
});

// ---------- Date range filter ----------
const dateFromInput = document.getElementById('date-from');
const dateToInput = document.getElementById('date-to');
const dateFilterGroup = document.getElementById('fg-date');
if (allDates.length === 0) {
  dateFilterGroup.style.display = 'none';
} else {
  const minD = allDates[0], maxD = allDates[allDates.length - 1];
  dateFromInput.min = minD; dateFromInput.max = maxD; dateFromInput.value = dateFrom;
  dateToInput.min = minD; dateToInput.max = maxD; dateToInput.value = dateTo;
  function onDateChange() {
    let f = dateFromInput.value || minD, t = dateToInput.value || maxD;
    if (f > t) { [f, t] = [t, f]; }
    dateFrom = f; dateTo = t;
    dateFromInput.value = f; dateToInput.value = t;
    renderAll();
  }
  dateFromInput.addEventListener('change', onDateChange);
  dateToInput.addEventListener('change', onDateChange);
}

// ---------- Formatting helpers ----------
const nf0 = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 });
const nf1 = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 1, minimumFractionDigits: 1 });
const nf2 = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2, minimumFractionDigits: 2 });
function inr(v) { return '₹' + nf0.format(Math.round(v)); }
function inr0(v) { return '₹' + nf0.format(Math.round(v)); }
function inr2(v) { return '₹' + nf2.format(v); }
function pct(v) { return nf2.format(v * 100) + '%'; }
function pct0(v) { return nf0.format(v * 100) + '%'; }
function lakh(v) { return nf2.format(v / 100000); }
function inrLakh(v) { return '₹' + lakh(v) + ' L'; }
function numLakh(v) { return lakh(v) + ' L'; }
function thousand(v) { return nf1.format(v / 1000) + ' K'; }
function safeDiv(a, b) { return (b === 0 || b === null || a === null) ? null : a / b; }
function fmtOrDash(v, fmt) { return v === null ? '–' : fmt(v); }
function escapeHtml(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

// Returns plain (unescaped) text — callers put it in textContent/createTextNode
// (auto-safe) or must escapeHtml() it themselves before using it in innerHTML.
function joinNames(set, max) {
  const arr = [...set].sort(naturalCompare);
  if (arr.length <= max) return arr.join(', ');
  return arr.slice(0, max).join(', ') + ' + ' + (arr.length - max) + ' more';
}

// ---------- Aggregate a set of rows into every Number + Ratio metric ----------
function aggregate(rows) {
  const sum = (key) => rows.reduce((acc, r) => acc + r[key], 0);
  const spend = sum('spend'), revenue = sum('revenue'), reach = sum('reach'), impr = sum('impr'),
        clicks = sum('clicks'), lpv = sum('lpv'), atc = sum('atc'), purchases = sum('purchases'),
        sec3 = sum('sec3'), thru = sum('thru'), ci = sum('ci');
  const frequency = safeDiv(impr, reach);
  const aov = safeDiv(revenue, purchases);
  const cpmR = safeDiv(spend, impr); const cpm = cpmR === null ? null : cpmR * 1000;
  const hook = safeDiv(sec3, impr), hold = safeDiv(thru, sec3), ctr = safeDiv(clicks, impr),
        lpvr = safeDiv(lpv, clicks), atcr = safeDiv(atc, lpv), cir = safeDiv(ci, atc),
        ccr = safeDiv(purchases, ci), cvr = safeDiv(purchases, lpv), roas = safeDiv(revenue, spend);
  // Cost metrics for the default view — lower is better for all three.
  const cpa = safeDiv(spend, purchases);       // cost per acquisition = spend / orders
  const cpc = safeDiv(spend, clicks);          // cost per click = spend / link clicks
  const costPerAtc = safeDiv(spend, atc);      // cost per add-to-cart = spend / adds to cart
  return { spend, revenue, reach, impr, clicks, lpv, atc, purchases, sec3, thru, ci,
           frequency, aov, cpm, hook, hold, ctr, lpvr, atcr, cir, ccr, cvr, roas,
           cpa, cpc, costPerAtc, rowCount: rows.length };
}

// share metric = comparison shows "total + % share" in neutral blue (additive volume metrics)
// index metric = comparison shows "scope value + delta%" colored green/red by direction
//
// ALL_METRICS is the single catalog every metric is defined in — the tile grid
// and the "Metrics" multi-select filter both read from it. Order here is the
// FIXED tile order whenever a metric is selected (selecting/deselecting never
// reorders tiles). The first 14 entries are exactly the requested default
// view, in the requested order; DEFAULT_METRIC_KEYS below slices them out.
const ALL_METRICS = [
  { key: 'spend',      label: 'Spends',        fmt: inrLakh, sub: '₹, in lakhs',                                    kind: 'share' },
  { key: 'roas',       label: 'ROAS',          fmt: v => nf2.format(v) + '×', sub: 'Sale ÷ amount spent',          kind: 'index', dir: true },
  { key: 'purchases',  label: 'Orders',        fmt: thousand, sub: 'Purchases, in thousands',                       kind: 'share' },
  { key: 'cpa',        label: 'CPA',           fmt: inr0, sub: 'Amount spent ÷ orders (cost per acquisition)',      kind: 'index', dir: false },
  { key: 'revenue',    label: 'Sale',          fmt: inrLakh, sub: 'Purchases conversion value, ₹ in lakhs',         kind: 'share' },
  { key: 'aov',        label: 'AOV',           fmt: inr0, sub: 'Sale ÷ orders',                                     kind: 'index', dir: true },
  { key: 'ctr',        label: 'CTR',           fmt: pct,  sub: 'Link clicks ÷ impressions',                         kind: 'index', dir: true },
  { key: 'cpm',        label: 'CPM',           fmt: inr0, sub: 'Amount spent per 1,000 impressions',                kind: 'index', dir: false },
  { key: 'cpc',        label: 'CPC',           fmt: inr2, sub: 'Amount spent ÷ link clicks (cost per click)',       kind: 'index', dir: false },
  { key: 'lpvr',       label: 'LP rate',       fmt: pct0, sub: 'Landing page views ÷ link clicks',                  kind: 'index', dir: true },
  { key: 'atcr',       label: 'ATC rate',      fmt: pct0, sub: 'Adds to cart ÷ landing page views',                 kind: 'index', dir: true },
  { key: 'costPerAtc', label: 'Cost per ATC',  fmt: inr0, sub: 'Amount spent ÷ adds to cart',                       kind: 'index', dir: false },
  { key: 'cir',        label: 'IC rate',       fmt: pct0, sub: 'Checkouts initiated ÷ adds to cart',                kind: 'index', dir: true },
  { key: 'cvr',        label: 'CVR',           fmt: pct,  sub: 'Orders ÷ landing page views',                       kind: 'index', dir: true },
  // Everything else — available from the Metrics filter, not shown by default.
  { key: 'reach',      label: 'Reach',                fmt: numLakh, sub: 'People, in lakhs',                        kind: 'share' },
  { key: 'frequency',  label: 'Frequency',            fmt: v => nf2.format(v), sub: 'Impressions ÷ reach',          kind: 'index', dir: null },
  { key: 'impr',       label: 'Impressions',          fmt: numLakh, sub: 'In lakhs',                                kind: 'share' },
  { key: 'sec3',       label: '3 sec views',          fmt: numLakh, sub: 'In lakhs',                                kind: 'share' },
  { key: 'thru',       label: 'ThruPlays',            fmt: numLakh, sub: 'In lakhs',                                kind: 'share' },
  { key: 'clicks',     label: 'Link clicks',          fmt: numLakh, sub: 'In lakhs',                                kind: 'share' },
  { key: 'lpv',        label: 'Landing page views',   fmt: numLakh, sub: 'In lakhs',                                kind: 'share' },
  { key: 'atc',        label: 'Adds to cart',         fmt: thousand, sub: 'In thousands',                          kind: 'share' },
  { key: 'ci',         label: 'Checkouts initiated',  fmt: thousand, sub: 'In thousands',                          kind: 'share' },
  { key: 'hook',       label: 'Hook rate',            fmt: pct0, sub: '3 sec views ÷ impressions',                  kind: 'index', dir: true },
  { key: 'hold',       label: 'Hold rate',            fmt: pct0, sub: 'ThruPlays ÷ 3 sec views',                    kind: 'index', dir: true },
  { key: 'ccr',        label: 'Checkout completion rate', fmt: pct0, sub: 'Orders ÷ checkouts initiated',           kind: 'index', dir: true },
];
const DEFAULT_METRIC_KEYS = ALL_METRICS.slice(0, 14).map(m => m.key);
const METRICS_BY_KEY = new Map(ALL_METRICS.map(m => [m.key, m]));
selMetrics = new Set(DEFAULT_METRIC_KEYS);

// ---------- Work out what to compare the current selection against ----------
function getCampaignViewScope() {
  const availAdsCur = availableAds(selAdsets);
  const availAdsetsCur = availableAdsets(selCampaigns);
  if (selAds.size < availAdsCur.size) {
    return {
      level: 'ad',
      baselineRows: DATA.filter(d => selAdsets.has(d.s) && inDateRange(d)),
      label: 'all ads in ' + (selAdsets.size === 1 ? [...selAdsets][0] : joinNames(selAdsets, 2) + ' (' + selAdsets.size + ' ad sets)')
    };
  }
  if (selAdsets.size < availAdsetsCur.size) {
    return {
      level: 'adset',
      baselineRows: DATA.filter(d => selCampaigns.has(d.c) && inDateRange(d)),
      label: 'all ad sets in ' + (selCampaigns.size === 1 ? [...selCampaigns][0] : joinNames(selCampaigns, 2) + ' (' + selCampaigns.size + ' campaigns)')
    };
  }
  if (selCampaigns.size < campaigns.length) {
    return { level: 'campaign', baselineRows: DATA.filter(inDateRange), label: 'all campaigns' };
  }
  return { level: 'none', baselineRows: null, label: null };
}

function getComparisonScope() {
  return getCampaignViewScope();
}

// Two-row horizontal bar chart: "Selected" (this selection) vs the comparison
// scope's overall total (label varies by which filter level is narrowed).
const OVERALL_LABEL_BY_LEVEL = {
  campaign: 'Overall Campaign', adset: 'Overall Ad Set', ad: 'Overall Ads',
};
function overallLabel(level) { return OVERALL_LABEL_BY_LEVEL[level] || 'Overall'; }

// widthFn receives (value) and returns a 0-100 bar width for that row.
function buildMiniBars(selDisplay, selWidth, baseDisplay, baseWidth, scopeLabel) {
  const wrap = document.createElement('div');
  wrap.className = 'mini-bars';
  [['Selected', selDisplay, selWidth, 'sel'], [scopeLabel, baseDisplay, baseWidth, 'base']].forEach(([lbl, disp, width, cls]) => {
    const row = document.createElement('div');
    row.className = 'mini-bar-row';
    const lblSpan = document.createElement('span');
    lblSpan.className = 'mb-label';
    lblSpan.textContent = lbl;
    const track = document.createElement('div');
    track.className = 'mini-bar-track';
    const fill = document.createElement('div');
    fill.className = 'mini-bar-fill ' + cls;
    fill.style.width = Math.max(0, Math.min(100, width)) + '%';
    track.appendChild(fill);
    const valSpan = document.createElement('span');
    valSpan.className = 'mb-value';
    valSpan.textContent = disp;
    row.appendChild(lblSpan);
    row.appendChild(track);
    row.appendChild(valSpan);
    wrap.appendChild(row);
  });
  return wrap;
}

// Ranks the current selection's aggregate value for one metric against every
// individual peer entity in the active comparison scope (e.g. all 13 campaigns,
// or all ads in the selected ad set) — "out of total available options" for
// whichever filter level is currently narrowed.
function computeRank(spec, selValue, peerAggByEntity) {
  if (!peerAggByEntity || peerAggByEntity.length === 0 || selValue === null) return null;
  const higherBetter = spec.dir === false ? false : true; // only CPM (dir:false) ranks ascending
  let better = 0;
  peerAggByEntity.forEach(agg => {
    const v = agg[spec.key];
    if (v === null) return;
    if (higherBetter ? v > selValue : v < selValue) better++;
  });
  return { rank: better + 1, total: peerAggByEntity.length };
}

function metricTile(spec, index, selAgg, baseAgg, scope) {
  const tile = document.createElement('div');
  tile.className = 'tile';

  const labelDiv = document.createElement('div');
  labelDiv.className = 't-label';
  const idxSpan = document.createElement('span');
  idxSpan.className = 't-index';
  idxSpan.textContent = String(index + 1);
  labelDiv.appendChild(idxSpan);
  labelDiv.appendChild(document.createTextNode(spec.label));
  tile.appendChild(labelDiv);

  const selVal = selAgg[spec.key];
  const valueDiv = document.createElement('div');
  valueDiv.className = 't-value';
  valueDiv.textContent = selVal === null ? '–' : spec.fmt(selVal);
  tile.appendChild(valueDiv);

  if (spec.sub) {
    const subDiv = document.createElement('div');
    subDiv.className = 't-sub';
    subDiv.textContent = spec.sub;
    tile.appendChild(subDiv);
  }

  if (baseAgg) {
    const baseVal = baseAgg[spec.key];
    const compare = document.createElement('div');
    compare.className = 't-compare';

    const rankInfo = scope.singleSelected ? computeRank(spec, selVal, scope.peerAggByEntity) : null;

    // Puts the existing badge on the left and "| Rank X of Y" on the right of the
    // same line, so the saliency/delta reading and the rank are visible together.
    function appendBadgeRow(badgeEl) {
      const row = document.createElement('div');
      row.className = 't-badge-row';
      row.appendChild(badgeEl);
      if (rankInfo) {
        const rankSpan = document.createElement('span');
        rankSpan.className = 't-rank-inline';
        rankSpan.appendChild(document.createTextNode('| Rank '));
        const rb = document.createElement('b');
        rb.textContent = rankInfo.rank;
        rankSpan.appendChild(rb);
        rankSpan.appendChild(document.createTextNode(' of ' + rankInfo.total + ' ' + levelWords(scope.level).plural));
        row.appendChild(rankSpan);
      }
      compare.appendChild(row);
    }

    const baseLine = document.createElement('div');
    baseLine.className = 't-baseline';

    if (baseVal === null || selVal === null) {
      baseLine.textContent = 'No comparison data for ' + scope.plainLabel;
      compare.appendChild(baseLine);
    } else if (spec.kind === 'share') {
      baseLine.appendChild(document.createTextNode('Total (' + scope.plainLabel + '): '));
      const b = document.createElement('b');
      b.textContent = baseVal === 0 ? '–' : spec.fmt(baseVal);
      baseLine.appendChild(b);
      compare.appendChild(baseLine);

      if (baseVal !== 0) {
        const share = Math.max(0, Math.min(100, (selVal / baseVal) * 100));
        compare.appendChild(buildMiniBars(
          spec.fmt(selVal), share,
          spec.fmt(baseVal), 100,
          overallLabel(scope.level)
        ));
        const shareLabel = document.createElement('div');
        shareLabel.className = 't-badge neutral';
        shareLabel.textContent = nf1.format(share) + '% of total';
        appendBadgeRow(shareLabel);
      }
    } else {
      // index metric: two bars scaled to the larger value, plus a delta badge
      baseLine.appendChild(document.createTextNode(capitalize(scope.plainLabel) + ': '));
      const b = document.createElement('b');
      b.textContent = baseVal === 0 ? '–' : spec.fmt(baseVal);
      baseLine.appendChild(b);
      compare.appendChild(baseLine);

      if (baseVal !== 0) {
        const maxVal = Math.max(selVal, baseVal, 0.0001);
        compare.appendChild(buildMiniBars(
          spec.fmt(selVal), (selVal / maxVal) * 100,
          spec.fmt(baseVal), (baseVal / maxVal) * 100,
          overallLabel(scope.level)
        ));

        const deltaPct = (selVal / baseVal - 1) * 100;
        const badge = document.createElement('div');
        let colorClass = 'neutral', arrow = '●', text;
        if (Math.abs(deltaPct) < 0.05) {
          text = 'even with ' + scope.plainLabel;
        } else {
          arrow = deltaPct > 0 ? '▲' : '▼';
          text = nf1.format(Math.abs(deltaPct)) + '% ' + (deltaPct > 0 ? 'above' : 'below');
          if (spec.dir === true) colorClass = deltaPct > 0 ? 'good' : 'bad';
          else if (spec.dir === false) colorClass = deltaPct < 0 ? 'good' : 'bad';
        }
        badge.className = 't-badge ' + colorClass;
        badge.textContent = arrow + ' ' + text;
        appendBadgeRow(badge);
      }
    }
    tile.appendChild(compare);
  }

  return tile;
}
function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

// ---------- Legend for the Selected vs. Comparison-scope series ----------
function renderLegend(scope) {
  const el = document.getElementById('compare-legend');
  el.innerHTML = '';
  if (scope.level === 'none') return;
  const items = [
    ['sel', 'This selection'],
    ['base', capitalize(scope.plainLabel)],
  ];
  items.forEach(([cls, text]) => {
    const item = document.createElement('div');
    item.className = 'lg-item';
    const sw = document.createElement('span');
    sw.className = 'lg-swatch ' + cls;
    const txt = document.createElement('span');
    txt.textContent = text;
    item.appendChild(sw);
    item.appendChild(txt);
    el.appendChild(item);
  });
}

// ---------- Performance score ----------
let scoreLevelCampaign = 'campaign';
function currentScoreLevel() { return scoreLevelCampaign; }

['campaign', 'adset', 'ad'].forEach(lvl => {
  document.getElementById('score-lvl-' + lvl).addEventListener('click', () => {
    scoreLevelCampaign = lvl;
    ['campaign', 'adset', 'ad'].forEach(l => {
      document.getElementById('score-lvl-' + l).classList.toggle('active', l === lvl);
    });
    renderScores();
  });
});

// Grouping key + display words for every level the score table can be shown at.
function scoreKeyFn(level) {
  switch (level) {
    case 'campaign': return d => d.c;
    case 'adset': return d => d.s;
    case 'ad': return d => d.a;
  }
}
function levelWords(level) {
  switch (level) {
    case 'campaign': return { plural: 'campaigns', singular: 'Campaign' };
    case 'adset': return { plural: 'ad sets', singular: 'Ad set' };
    case 'ad': return { plural: 'ads', singular: 'Ad' };
  }
}

function clampPct(v) { return Math.max(0, Math.min(100, v)); }

// value -> 0-100, best of the peer set = 100, worst = 0 (inverted when higherBetter is false)
function normMinMax(value, min, max, higherBetter) {
  if (value === null) return 0;
  if (max === min) return 50;
  let t = (value - min) / (max - min);
  if (higherBetter === false) t = 1 - t;
  return clampPct(t * 100);
}
// value -> 0-100, this entity's % share of the total across the peer set
function salShare(value, total) {
  if (value === null || total <= 0) return 0;
  return clampPct((value / total) * 100);
}

// Tier 4's "everything else" composite: every remaining metric, direction-aware, averaged.
const OTHER_METRICS = [
  { key: 'reach', dir: true }, { key: 'sec3', dir: true }, { key: 'thru', dir: true },
  { key: 'lpv', dir: true }, { key: 'ci', dir: true }, { key: 'hook', dir: true },
  { key: 'hold', dir: true }, { key: 'lpvr', dir: true }, { key: 'atcr', dir: true },
  { key: 'cir', dir: true }, { key: 'ccr', dir: true }, { key: 'cvr', dir: true },
  { key: 'cpm', dir: false },
];

function computeScores(level, rows) {
  const keyFn = scoreKeyFn(level);
  const groups = new Map();
  rows.forEach(d => {
    const k = keyFn(d);
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(d);
  });

  const entities = [...groups.entries()].map(([name, groupRows]) => ({
    name, count: groupRows.length, agg: aggregate(groupRows)
  }));
  if (entities.length === 0) return { entities, mm: null, totals: null };

  const totalRevenue = entities.reduce((a, e) => a + e.agg.revenue, 0);
  const totalSpend = entities.reduce((a, e) => a + e.agg.spend, 0);
  const totalImpr = entities.reduce((a, e) => a + e.agg.impr, 0);
  const totalClicks = entities.reduce((a, e) => a + e.agg.clicks, 0);
  const totalOrders = entities.reduce((a, e) => a + e.agg.purchases, 0);

  function minMaxOf(key) {
    const vals = entities.map(e => e.agg[key]).filter(v => v !== null);
    if (vals.length === 0) return { min: 0, max: 0 };
    return { min: Math.min(...vals), max: Math.max(...vals) };
  }
  const mmROAS = minMaxOf('roas');
  const mmAOV = minMaxOf('aov');
  const mmATC = minMaxOf('atc');
  const mmCTR = minMaxOf('ctr');
  const mmOther = {};
  OTHER_METRICS.forEach(m => { mmOther[m.key] = minMaxOf(m.key); });

  entities.forEach(e => {
    const a = e.agg;
    const normROAS = normMinMax(a.roas, mmROAS.min, mmROAS.max, true);
    const normAOV = normMinMax(a.aov, mmAOV.min, mmAOV.max, true);
    const normATC = normMinMax(a.atc, mmATC.min, mmATC.max, true);
    const normCTR = normMinMax(a.ctr, mmCTR.min, mmCTR.max, true);
    const salRevenue = salShare(a.revenue, totalRevenue);
    const salImpr = salShare(a.impr, totalImpr);
    const salSpend = salShare(a.spend, totalSpend);
    const salClicks = salShare(a.clicks, totalClicks);
    const salOrders = salShare(a.purchases, totalOrders);

    const otherScores = OTHER_METRICS.map(m => normMinMax(a[m.key], mmOther[m.key].min, mmOther[m.key].max, m.dir));
    const otherComposite = otherScores.reduce((s, v) => s + v, 0) / otherScores.length;

    e.tier1 = 0.22 * normROAS + 0.18 * salRevenue;
    e.tier2 = 0.13 * normAOV + 0.12 * normATC;
    e.tier3 = 0.11 * normCTR + 0.09 * salImpr;
    e.tier4 = 0.04 * salSpend + 0.04 * salClicks + 0.04 * salOrders + 0.03 * otherComposite;
    e.score = e.tier1 + e.tier2 + e.tier3 + e.tier4;
    e.parts = { normROAS, salRevenue, normAOV, normATC, normCTR, salImpr, salSpend, salClicks, salOrders, otherComposite };
    e.detail = 'ROAS ' + (a.roas === null ? '–' : nf2.format(a.roas) + '×') +
      ' · Revenue ' + inrLakh(a.revenue) + ' (' + nf1.format(salRevenue) + '% of total)' +
      ' · AOV ' + (a.aov === null ? '–' : inr0(a.aov)) +
      ' · ATC ' + thousand(a.atc) +
      ' · CTR ' + (a.ctr === null ? '–' : pct(a.ctr)) +
      ' · Impr ' + numLakh(a.impr) + ' (' + nf1.format(salImpr) + '% of total)';
  });

  entities.sort((x, y) => y.score - x.score);
  return {
    entities,
    mm: { roas: mmROAS, aov: mmAOV, atc: mmATC, ctr: mmCTR },
    totals: { revenue: totalRevenue, spend: totalSpend, impr: totalImpr, clicks: totalClicks, orders: totalOrders },
  };
}

const SCORE_LIMIT = 20;

// Renders a fully worked numeric example of the formula, using the #1-ranked
// entity's own component scores. Each tier gets its formula written out as an
// explicit min-max / share-of-total fraction (not shorthand), then the same
// fraction with this entity's real numbers substituted in, exactly like:
//   Tier 1 -> [22% * (ROAS - Min ROAS) / (Max ROAS - Min ROAS) * 100] + [18% * Revenue / Total Revenue * 100]
function renderScoreFormula(entities, mm, totals, level) {
  const box = document.getElementById('score-formula');
  box.innerHTML = '';
  if (entities.length === 0 || !mm) { box.style.display = 'none'; return; }
  box.style.display = '';
  const top = entities[0];
  const p = top.parts;
  const a = top.agg;
  const t1 = 0.22 * p.normROAS + 0.18 * p.salRevenue;
  const t2 = 0.13 * p.normAOV + 0.12 * p.normATC;
  const t3 = 0.11 * p.normCTR + 0.09 * p.salImpr;
  const t4 = 0.04 * p.salSpend + 0.04 * p.salClicks + 0.04 * p.salOrders + 0.03 * p.otherComposite;
  const total = t1 + t2 + t3 + t4;
  const who = 'this ' + levelWords(level).singular.toLowerCase();

  const title = document.createElement('div');
  title.className = 'sf-title';
  title.textContent = 'Worked example — how "' + top.name + '" scored ' + nf1.format(top.score) + ' (rank 1):';
  box.appendChild(title);

  const roasTxt = a.roas === null ? '–' : nf2.format(a.roas) + '×';
  const aovTxt = a.aov === null ? '–' : inr0(a.aov);
  const ctrTxt = a.ctr === null ? '–' : pct(a.ctr);

  // A min-max bracket: "22% × (value − Min) / (Max − Min) × 100"; falls back to a
  // flat 50 when every entity in the group is tied (Max = Min), same as the score.
  function mmBracket(weightPct, label, valTxt, mmObj, fmt) {
    if (mmObj.max === mmObj.min) return weightPct + '% × 50  [tied — Min ' + label + ' = Max ' + label + ']';
    return weightPct + '% × (' + valTxt + ' − Min ' + label + ' ' + fmt(mmObj.min) + ') / (Max ' + label + ' ' + fmt(mmObj.max) + ' − Min ' + label + ' ' + fmt(mmObj.min) + ') × 100';
  }
  // A share-of-total bracket: "18% × value / total × 100"
  function shareBracket(weightPct, label, valTxt, totalTxt) {
    return weightPct + '% × ' + label + ' ' + valTxt + ' / Total ' + label + ' ' + totalTxt + ' × 100';
  }

  function appendTier(num, tierName, weightPct, formulaParts, numberParts, subtotal) {
    const wrap = document.createElement('div');
    wrap.className = 'sf-tier';

    const head = document.createElement('div');
    head.className = 'sf-line';
    const b = document.createElement('b');
    b.textContent = 'Tier ' + num + ' — ' + tierName + ' (' + weightPct + '%)';
    head.appendChild(b);
    wrap.appendChild(head);

    const formulaLine = document.createElement('div');
    formulaLine.className = 'sf-line sf-formula';
    formulaLine.textContent = 'Formula:  ' + formulaParts.join('  +  ');
    wrap.appendChild(formulaLine);

    const numbersLine = document.createElement('div');
    numbersLine.className = 'sf-line sf-numbers';
    numbersLine.textContent = 'Numbers:  ' + numberParts.join('  +  ') + '  =  ' + nf1.format(subtotal);
    wrap.appendChild(numbersLine);

    box.appendChild(wrap);
  }

  appendTier(1, 'ROAS + Revenue', 40,
    [
      '[22% × (ROAS of ' + who + ' − Min ROAS) / (Max ROAS − Min ROAS) × 100]',
      '[18% × Revenue of ' + who + ' / Total Revenue × 100]',
    ],
    [
      '[' + mmBracket(22, 'ROAS', roasTxt, mm.roas, v => nf2.format(v) + '×') + ']',
      '[' + shareBracket(18, 'Revenue', inrLakh(a.revenue), inrLakh(totals.revenue)) + ']',
    ],
    t1);

  appendTier(2, 'AOV + Adds to cart', 25,
    [
      '[13% × (AOV of ' + who + ' − Min AOV) / (Max AOV − Min AOV) × 100]',
      '[12% × (Adds to Cart of ' + who + ' − Min Adds to Cart) / (Max Adds to Cart − Min Adds to Cart) × 100]',
    ],
    [
      '[' + mmBracket(13, 'AOV', aovTxt, mm.aov, inr0) + ']',
      '[' + mmBracket(12, 'Adds to Cart', thousand(a.atc), mm.atc, thousand) + ']',
    ],
    t2);

  appendTier(3, 'CTR + Impressions', 20,
    [
      '[11% × (CTR of ' + who + ' − Min CTR) / (Max CTR − Min CTR) × 100]',
      '[9% × Impressions of ' + who + ' / Total Impressions × 100]',
    ],
    [
      '[' + mmBracket(11, 'CTR', ctrTxt, mm.ctr, pct) + ']',
      '[' + shareBracket(9, 'Impressions', numLakh(a.impr), numLakh(totals.impr)) + ']',
    ],
    t3);

  appendTier(4, 'Everything else', 15,
    [
      '[4% × Spend of ' + who + ' / Total Spend × 100]',
      '[4% × Link Clicks of ' + who + ' / Total Link Clicks × 100]',
      '[4% × Orders of ' + who + ' / Total Orders × 100]',
      '[3% × Other-Metrics Avg]',
    ],
    [
      '[' + shareBracket(4, 'Spend', inrLakh(a.spend), inrLakh(totals.spend)) + ']',
      '[' + shareBracket(4, 'Link Clicks', numLakh(a.clicks), numLakh(totals.clicks)) + ']',
      '[' + shareBracket(4, 'Orders', thousand(a.purchases), thousand(totals.orders)) + ']',
      '[3% × ' + nf1.format(p.otherComposite) + ']',
    ],
    t4);

  const note = document.createElement('div');
  note.className = 'sf-line sf-note';
  note.textContent = 'Other-Metrics Avg (' + nf1.format(p.otherComposite) + ') is itself the average of 13 further min-max-normalized metrics: '
    + 'reach, hook rate, hold rate, LPVR, ATCR, checkout initiated rate, checkout completion rate, CVR, CPM (inverted — lower is better), '
    + '3 sec views, ThruPlays, landing page views, and checkouts initiated.';
  box.appendChild(note);

  const totalLine = document.createElement('div');
  totalLine.className = 'sf-line sf-total';
  totalLine.textContent = 'Final Score = Tier 1 + Tier 2 + Tier 3 + Tier 4 = '
    + nf1.format(t1) + ' + ' + nf1.format(t2) + ' + ' + nf1.format(t3) + ' + ' + nf1.format(t4) + ' = ' + nf1.format(total);
  box.appendChild(totalLine);
}

function renderScoreTable(level, rows) {
  const { entities, mm, totals } = computeScores(level, rows);
  renderScoreFormula(entities, mm, totals, level);
  const sub = document.getElementById('score-sub');
  const { plural: levelWord, singular } = levelWords(level);
  sub.textContent = entities.length === 0
    ? 'No ' + levelWord + ' in the current filter selection.'
    : 'Ranking ' + entities.length + ' ' + levelWord + ' in the current filter selection' +
      (entities.length > SCORE_LIMIT ? ' · showing the top ' + SCORE_LIMIT : '') + '.';

  const table = document.getElementById('score-table');
  table.innerHTML = '';
  if (entities.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'score-empty';
    empty.textContent = 'Nothing to score — widen the filters above.';
    table.appendChild(empty);
    return;
  }

  const head = document.createElement('div');
  head.className = 'score-row head';
  ['#', singular, 'Score breakdown', 'Score'].forEach(t => {
    const c = document.createElement('div');
    c.textContent = t;
    head.appendChild(c);
  });
  table.appendChild(head);

  entities.slice(0, SCORE_LIMIT).forEach((e, i) => {
    const row = document.createElement('div');
    row.className = 'score-row';

    const rank = document.createElement('div');
    rank.className = 'score-rank';
    rank.textContent = String(i + 1);
    row.appendChild(rank);

    const nameWrap = document.createElement('div');
    nameWrap.className = 'score-name-wrap';
    const name = document.createElement('div');
    name.className = 'score-name';
    name.textContent = e.name;
    name.title = e.name;
    const detail = document.createElement('div');
    detail.className = 'score-detail';
    detail.textContent = e.detail;
    detail.title = e.detail;
    nameWrap.appendChild(name);
    nameWrap.appendChild(detail);
    row.appendChild(nameWrap);

    const barTrack = document.createElement('div');
    barTrack.className = 'score-bar-track';
    [['t1', e.tier1], ['t2', e.tier2], ['t3', e.tier3], ['t4', e.tier4]].forEach(([cls, val]) => {
      const seg = document.createElement('div');
      seg.className = 'score-bar-seg ' + cls;
      seg.style.width = clampPct(val) + '%';
      seg.title = e.name;
      barTrack.appendChild(seg);
    });
    row.appendChild(barTrack);

    const scoreVal = document.createElement('div');
    scoreVal.className = 'score-value';
    scoreVal.textContent = nf1.format(e.score);
    row.appendChild(scoreVal);

    table.appendChild(row);
  });
}

function renderScores() {
  renderScoreTable(currentScoreLevel(), getFilteredRows());
}

// ---------- Render everything ----------
function renderAll() {
  const rows = getFilteredRows();
  const selAgg = aggregate(rows);

  const scopeEl = document.getElementById('scope-line');
  const compareEl = document.getElementById('compare-line');

  const totalAdsAvail = availableAds(selAdsets).size;
  scopeEl.innerHTML =
    '<b>' + selCampaigns.size + '</b> of ' + campaigns.length + ' campaigns · ' +
    '<b>' + selAdsets.size + '</b> of ' + Object.keys(adsetToAds).length + ' ad sets · ' +
    '<b>' + selAds.size + '</b> of ' + totalAdsAvail + ' ads selected · ' +
    '<b>' + rows.length + '</b> of ' + DATA.length + ' rows matched';

  const scope = getComparisonScope();
  let baseAgg = null;
  compareEl.textContent = '';
  if (scope.level !== 'none') {
    baseAgg = aggregate(scope.baselineRows);
    scope.plainLabel = scope.label;
    // One aggregate per individual peer entity at this scope's level (e.g. each of the
    // 13 campaigns), reused by every tile to rank the current selection against them.
    const keyFn = scoreKeyFn(scope.level);
    const groups = new Map();
    scope.baselineRows.forEach(d => {
      const k = keyFn(d);
      if (!groups.has(k)) groups.set(k, []);
      groups.get(k).push(d);
    });
    scope.peerAggByEntity = [...groups.values()].map(rs => aggregate(rs));
    // Rank is only meaningful when the current selection is exactly one entity at the
    // narrowed (bottom-most) filter level — a combined multi-entity selection has no
    // single rank to report.
    const selSizeAtLevel = { ad: selAds.size, adset: selAdsets.size, campaign: selCampaigns.size }[scope.level];
    scope.singleSelected = selSizeAtLevel === 1;
    compareEl.appendChild(document.createTextNode('Comparing this selection against '));
    const b = document.createElement('b');
    b.textContent = scope.label;
    compareEl.appendChild(b);
    compareEl.appendChild(document.createTextNode('.'));
  } else {
    compareEl.textContent = 'Narrow the campaign, ad set, or ad filter to see a side-by-side comparison.';
  }

  renderLegend(scope);

  const grid = document.getElementById('kpi-grid');
  grid.innerHTML = '';
  const metrics = ALL_METRICS.filter(m => selMetrics.has(m.key));
  metrics.forEach((spec, i) => grid.appendChild(metricTile(spec, i, selAgg, baseAgg, scope)));

  renderScores();
}

campaignDD.render();
adsetDD.render();
adDD.render();
metricsDD.render();
renderAll();

// ---------- Chat assistant ("sample" capability — asks Claude, on the viewer's own account) ----------
(function () {
  const fab = document.getElementById('chat-fab');
  const panel = document.getElementById('chat-panel');
  const closeBtn = document.getElementById('chat-close');
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  const messagesEl = document.getElementById('chat-messages');
  const suggestEl = document.getElementById('chat-suggestions');
  const sendBtn = document.getElementById('chat-send');

  let sampleFn = null;
  let chatTurns = []; // {role:'user'|'assistant', content}
  let sending = false;
  let ctl = null;

  const RULES = "You are a sharp, concise paid-media analyst embedded in a Meta Ads performance dashboard. " +
    "You are given a DATA SNAPSHOT computed directly by the dashboard's own code (ground truth — trust these " +
    "numbers exactly; never recompute, round differently, or contradict them), reflecting whatever campaign/ad " +
    "and date-range filters the viewer currently has selected, followed by the viewer's question. Answer " +
    "directly: one short lead sentence with your verdict, then up to 5 tight bullet points citing real names " +
    "and numbers from the snapshot (spend, ROAS, CPA, CTR, CVR, Score, trend%). No filler, no disclaimers, no " +
    "restating the question, no markdown headers. Scores are this dashboard's own 0-100 Performance Score " +
    "(already blends ROAS, revenue, AOV, adds-to-cart, CTR, impressions and more) — prefer it over any single " +
    "metric when asked what is 'good' or 'bad'. For 'good'/'best' questions, favor high Score with real spend " +
    "or order volume, not a thin outlier. For 'needs improvement' or 'worsening' questions, favor low Score, a " +
    "negative ROAS trend, or heavy spend paired with weak ROAS/CVR. If the snapshot lacks what's needed (e.g. " +
    "no date data for a trend question), say so plainly instead of guessing.";

  function trendDelta(rows, metricKey) {
    const dated = rows.filter(r => r.date);
    const days = [...new Set(dated.map(r => r.date))].sort();
    if (days.length < 2) return null;
    const mid = days[Math.floor(days.length / 2)];
    const early = dated.filter(r => r.date < mid), late = dated.filter(r => r.date >= mid);
    if (!early.length || !late.length) return null;
    const v1 = aggregate(early)[metricKey], v2 = aggregate(late)[metricKey];
    if (v1 === null || v2 === null || v1 === 0) return null;
    return (v2 - v1) / v1;
  }

  function digestTable(level, rows, cap) {
    const keyFn = scoreKeyFn(level);
    const groups = new Map();
    rows.forEach(d => { const k = keyFn(d); if (!groups.has(k)) groups.set(k, []); groups.get(k).push(d); });
    const scored = computeScores(level, rows).entities;
    return scored.slice(0, cap).map(e => {
      const rs = groups.get(e.name) || [];
      const a = e.agg;
      const trend = trendDelta(rs, 'roas');
      return [
        e.name, nf1.format(e.score), Math.round(a.spend), Math.round(a.revenue),
        a.roas === null ? '-' : nf2.format(a.roas), Math.round(a.purchases),
        a.cpa === null ? '-' : Math.round(a.cpa),
        a.ctr === null ? '-' : pct(a.ctr), a.cvr === null ? '-' : pct(a.cvr),
        trend === null ? 'n/a' : (trend >= 0 ? '+' : '') + Math.round(trend * 100) + '%'
      ].join(' | ');
    }).join('\n');
  }

  function buildDataDigest() {
    const rows = getFilteredRows();
    if (!rows.length) return 'No rows match the current filters — nothing to analyze.';
    const overall = aggregate(rows);
    const dates = [...new Set(rows.map(r => r.date).filter(Boolean))].sort();
    const dateNote = dates.length
      ? ('Date range in view: ' + dates[0] + ' to ' + dates[dates.length - 1] + ' (' + dates.length + ' distinct day(s) of data).')
      : 'No per-day date data in this export — trend columns will read n/a.';
    return [
      'OVERALL (current filters): spend=₹' + Math.round(overall.spend) + ', sale=₹' + Math.round(overall.revenue) +
        ', ROAS=' + (overall.roas === null ? '-' : nf2.format(overall.roas)) + ', orders=' + Math.round(overall.purchases) +
        ', CTR=' + (overall.ctr === null ? '-' : pct(overall.ctr)) + ', CVR=' + (overall.cvr === null ? '-' : pct(overall.cvr)) + '.',
      dateNote,
      '\nCAMPAIGNS ranked by the dashboard 0-100 Performance Score (highest first):\n' +
        'Campaign | Score | Spend | Sale | ROAS | Orders | CPA | CTR | CVR | ROAS trend (2nd half vs 1st half of range)\n' +
        digestTable('campaign', rows, 25),
      '\nADS / CREATIVES ranked the same way:\n' +
        'Ad | Score | Spend | Sale | ROAS | Orders | CPA | CTR | CVR | ROAS trend\n' +
        digestTable('ad', rows, 25),
    ].join('\n');
  }

  function addMsg(role, text) {
    const el = document.createElement('div');
    el.className = 'chat-msg chat-msg-' + (role === 'user' ? 'user' : 'bot');
    el.textContent = text;
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return el;
  }

  function errorCopy(e) {
    const code = e && e.code;
    if (code === 'not_granted') return "This viewer hasn't allowed the assistant for this dashboard.";
    if (['sampling_disabled', 'not_declared', 'capability_disabled', 'capability_removed'].includes(code)) return "The assistant isn't available in this view.";
    if (code === 'rate_limited') return 'Too many requests right now — try again in a moment.';
    if (code === 'prompt_too_large') return 'Too much data in view to analyze at once — narrow your filters and try again.';
    if (code === 'cancelled') return 'Stopped.';
    if (code === 'refused') return 'The assistant declined to answer that — try rephrasing.';
    if (code === 'empty_completion') return 'No answer came back — try rephrasing.';
    return (e && e.text) ? e.text : 'Something went wrong — try again.';
  }

  function setSending(v) {
    sending = v;
    sendBtn.disabled = v;
    input.disabled = v;
  }

  async function ask(question) {
    if (!sampleFn || sending || !question.trim()) return;
    addMsg('user', question);
    chatTurns.push({ role: 'user', content: question });
    const botEl = addMsg('bot', 'Thinking…');
    setSending(true);
    ctl = new AbortController();
    try {
      const leading = { role: 'user', content: RULES + '\n\nDATA SNAPSHOT:\n' + buildDataDigest() };
      const turns = [leading, ...chatTurns];
      const { text } = await sampleFn(turns, {
        cache: false, modelTier: 'default', signal: ctl.signal,
        onText: ({ text }) => { botEl.textContent = text; messagesEl.scrollTop = messagesEl.scrollHeight; },
      });
      chatTurns.push({ role: 'assistant', content: text });
      if (chatTurns.length > 16) chatTurns = chatTurns.slice(-16); // keep the chat small; RULES+snapshot is rebuilt fresh every call
    } catch (e) {
      botEl.textContent = errorCopy(e);
      botEl.classList.add('chat-msg-error');
    } finally {
      setSending(false);
    }
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const q = input.value;
    input.value = '';
    ask(q);
  });
  suggestEl.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => { if (!sending) ask(chip.dataset.q); });
  });
  fab.addEventListener('click', () => {
    panel.hidden = !panel.hidden;
    if (!panel.hidden) input.focus();
  });
  closeBtn.addEventListener('click', () => { panel.hidden = true; });

  (async () => {
    try { sampleFn = window.claude ? await window.claude.use('sample') : null; } catch (e) { sampleFn = null; }
    fab.hidden = !sampleFn;
    if (!sampleFn) panel.hidden = true;
  })();
})();
</script>
</body>
</html>
"""

html = html.replace("__DATA_JSON__", data_json)

with open(out_path, "w") as f:
    f.write(html)

print(f"Built dashboard ({len(html)} bytes) -> {out_path}")
