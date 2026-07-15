// ============================================================
// 聖書協会共同訳（si.jbsbibleapp.com）引照・注 サイドパネル
// 元サイトの画面はそのまま。本文の点線（注のある節）をクリックすると
// 画面遷移せず、フローティングパネルに引照・注を表示する。
// パネルはヘッダーをドラッグで移動、右下角をドラッグでサイズ変更でき、
// 位置・大きさは次回も記憶する。
// ============================================================
(function () {
  if (window.__jbsNotesPanel) { window.__jbsNotesPanel.style.display = 'flex'; return; }

  // ── 保存済みの位置・大きさを読み込み（無ければ右下のデフォルト） ──
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem('jbsNotesRect') || '{}') || {}; } catch (e) {}
  var W = saved.w || 420;
  var H = saved.h || Math.round(window.innerHeight * 0.42);
  var L = (saved.left != null) ? saved.left : (window.innerWidth - W - 96);
  var T = (saved.top != null) ? saved.top : Math.round(window.innerHeight * 0.5);
  // 画面外に出ないよう補正
  L = Math.max(0, Math.min(L, window.innerWidth - 120));
  T = Math.max(0, Math.min(T, window.innerHeight - 80));

  // ── パネル（移動・リサイズ可能なフローティング） ──
  var panel = document.createElement('div');
  window.__jbsNotesPanel = panel;
  panel.id = 'jbs-notes-panel';
  panel.style.cssText = [
    'position:fixed',
    'left:' + L + 'px',
    'top:' + T + 'px',
    'width:' + W + 'px',
    'height:' + H + 'px',
    'min-width:240px',
    'min-height:120px',
    'display:flex',
    'flex-direction:column',
    'background:#ffffff',
    'border:2px solid #4a90d9',
    'border-radius:10px',
    'z-index:2147483647',
    'box-shadow:0 6px 24px rgba(0,0,0,0.18)',
    'font-family:sans-serif',
    'color:#1a1a1a',
    'overflow:hidden',
    'resize:both'            // 右下角をドラッグでサイズ変更
  ].join(';');

  // ヘッダー（青帯・ここをドラッグで移動）
  var header = document.createElement('div');
  header.style.cssText = 'background:#4a90d9;color:#fff;padding:8px 14px;font-size:14px;font-weight:bold;flex-shrink:0;display:flex;justify-content:space-between;align-items:center;cursor:move;user-select:none;';
  header.innerHTML = '<span id="jbs-notes-title">引照・注</span><span id="jbs-notes-hide" style="cursor:pointer;font-size:16px;padding:0 4px;">✕</span>';
  panel.appendChild(header);

  // 本体（スクロール）
  var body = document.createElement('div');
  body.id = 'jbs-notes-body';
  body.style.cssText = 'flex:1;overflow-y:auto;padding:14px 18px;font-size:14px;line-height:2.0;';
  body.innerHTML = '<div style="color:#888;font-size:13px;line-height:1.9;">本文の点線が付いた箇所（注のある節）を<br>クリックすると、ここに引照・注が表示されます。<br><br><span style="font-size:11px;">■ 青い帯をドラッグで移動／右下角をドラッグでサイズ変更</span></div>';
  panel.appendChild(body);

  document.body.appendChild(panel);

  // ── 位置・大きさを保存 ──
  function saveRect() {
    try {
      localStorage.setItem('jbsNotesRect', JSON.stringify({
        left: parseInt(panel.style.left, 10),
        top: parseInt(panel.style.top, 10),
        w: panel.offsetWidth,
        h: panel.offsetHeight
      }));
    } catch (e) {}
  }

  // ── ヘッダーをドラッグして移動 ──
  var drag = null;
  header.addEventListener('mousedown', function (e) {
    if (e.target && e.target.id === 'jbs-notes-hide') return;
    drag = { x: e.clientX, y: e.clientY, left: parseInt(panel.style.left, 10), top: parseInt(panel.style.top, 10) };
    e.preventDefault();
  });
  document.addEventListener('mousemove', function (e) {
    if (!drag) return;
    var nl = drag.left + (e.clientX - drag.x);
    var nt = drag.top + (e.clientY - drag.y);
    nl = Math.max(0, Math.min(nl, window.innerWidth - 60));
    nt = Math.max(0, Math.min(nt, window.innerHeight - 40));
    panel.style.left = nl + 'px';
    panel.style.top = nt + 'px';
  });
  document.addEventListener('mouseup', function () {
    if (drag) { drag = null; saveRect(); }
  });

  // ── リサイズ（右下角ドラッグ）を検知して保存 ──
  if (window.ResizeObserver) {
    var ro = new ResizeObserver(function () { saveRect(); });
    ro.observe(panel);
  }

  document.getElementById('jbs-notes-hide').addEventListener('click', function () {
    panel.style.display = 'none';
  });

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function cleanVal(v) {
    v = String(v || '').replace(/&quote;/g, '"');
    var d = document.createElement('div');
    d.innerHTML = v;
    return (d.textContent || '').replace(/\s+/g, ' ').trim();
  }

  var CIRC = ['①','②','③','④','⑤','⑥','⑦','⑧','⑨','⑩','⑪','⑫','⑬','⑭','⑮'];

  // ── 本文クリックを捕捉（capture段階でSPAの画面遷移より先に処理） ──
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    if (t.closest('#jbs-notes-panel')) return; // パネル内クリックは無視
    var a = t.closest('a.v');
    if (!a) return;

    var idx = a.getAttribute('index') || '';
    var p = a.closest('p');

    var seen = {};
    var notes = [];
    function add(s) {
      var key = s.className + '|' + s.getAttribute('value');
      if (seen[key]) return;
      seen[key] = 1;
      notes.push(s);
    }
    if (p && idx) {
      p.querySelectorAll('span.x[target="' + idx + '"][value], span.f[target="' + idx + '"][value]').forEach(add);
    }
    a.querySelectorAll('span.x[value], span.f[value]').forEach(add);

    if (notes.length === 0) return; // 注のない節は元の動作のまま

    e.preventDefault();
    e.stopPropagation();

    panel.style.display = 'flex';

    var clone = a.cloneNode(true);
    clone.querySelectorAll('span.x, span.f, .v-number, svg').forEach(function (n) { n.remove(); });

    var titleEl = document.getElementById('jbs-notes-title');
    if (titleEl) titleEl.textContent = '引照・注' + (idx ? '（' + idx + '節）' : '');

    var html =
      '<div style="border:1px solid #e3e8ee;border-radius:8px;padding:10px 12px;margin-bottom:14px;background:#f6f9fc;">' +
      (idx ? '<sup style="color:#4a90d9;font-weight:bold;margin-right:4px;font-size:11px;">' + esc(idx) + '</sup>' : '') +
      clone.innerHTML +
      '</div>';

    notes.forEach(function (s) {
      var isX = s.classList.contains('x');
      var no = (s.textContent || '').trim();
      var marker;
      if (isX) {
        var n = parseInt(no, 10);
        marker = CIRC[n - 1] || (no + ')');
      } else {
        marker = no || 'a';
      }
      html +=
        '<div style="margin-bottom:9px;">' +
        '<b style="margin-right:8px;color:#333;">' + esc(marker) + '</b>' +
        esc(cleanVal(s.getAttribute('value'))) +
        '</div>';
    });

    body.innerHTML = html;
    body.scrollTop = 0;
  }, true);
})();
