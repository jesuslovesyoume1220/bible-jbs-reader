// ============================================================
// 聖書協会共同訳（si.jbsbibleapp.com）引照・注 サイドパネル
// 元サイトの画面はそのまま。本文の点線（注のある節）をクリックすると
// 画面遷移せず、右下に固定表示したパネルに引照・注を表示する。
// ============================================================
(function () {
  if (window.__jbsNotesPanel) { window.__jbsNotesPanel.style.display = 'flex'; return; }

  // ── パネル（右下・はっきり見える固定表示） ──
  var panel = document.createElement('div');
  window.__jbsNotesPanel = panel;
  panel.id = 'jbs-notes-panel';
  panel.style.cssText = [
    'position:fixed',
    'right:96px',            // 右端のアイコン列を避ける
    'top:52%',
    'bottom:16px',
    'width:30%',
    'min-width:320px',
    'max-width:560px',
    'display:flex',
    'flex-direction:column',
    'background:#ffffff',
    'border:2px solid #4a90d9',
    'border-radius:10px',
    'z-index:2147483647',
    'box-shadow:0 6px 24px rgba(0,0,0,0.18)',
    'font-family:sans-serif',
    'color:#1a1a1a',
    'overflow:hidden'
  ].join(';');

  // ヘッダー（青帯・常に見える）
  var header = document.createElement('div');
  header.style.cssText = 'background:#4a90d9;color:#fff;padding:8px 14px;font-size:14px;font-weight:bold;flex-shrink:0;display:flex;justify-content:space-between;align-items:center;';
  header.innerHTML = '<span id="jbs-notes-title">引照・注</span><span id="jbs-notes-hide" style="cursor:pointer;font-size:16px;padding:0 4px;">✕</span>';
  panel.appendChild(header);

  // 本体（スクロール）
  var body = document.createElement('div');
  body.id = 'jbs-notes-body';
  body.style.cssText = 'flex:1;overflow-y:auto;padding:14px 18px;font-size:14px;line-height:2.0;';
  body.innerHTML = '<div style="color:#888;font-size:13px;line-height:1.9;">本文の点線が付いた箇所（注のある節）を<br>クリックすると、ここに引照・注が表示されます。</div>';
  panel.appendChild(body);

  document.body.appendChild(panel);

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
