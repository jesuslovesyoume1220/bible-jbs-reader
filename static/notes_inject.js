// ============================================================
// 聖書協会共同訳（si.jbsbibleapp.com）引照・注 サイドパネル
// Macランチャーから注入される。元サイトの画面はそのまま、
// 本文の点線（注のある節）をクリックすると、右下の空きエリアに
// 引照・注を表示する（画面遷移しない）。
// ============================================================
(function () {
  if (window.__jbsNotesInjected) return;
  window.__jbsNotesInjected = true;

  // ── パネル（検索エリアはそのまま残し、その真下の空きスペースに表示） ──
  var panel = document.createElement('div');
  panel.id = 'jbs-notes-panel';
  panel.style.cssText = [
    'position:fixed',
    'right:100px',      // 位置は positionPanel() が検索エリアに合わせて自動調整
    'top:46%',
    'bottom:14px',
    'width:32%',
    'min-width:300px',
    'overflow-y:auto',
    'background:#ffffff',
    'border:1px solid #d0d7de',
    'border-radius:10px',
    'padding:14px 18px',
    'z-index:99999',
    'font-size:14px',
    'line-height:2.0',
    'box-shadow:0 4px 16px rgba(0,0,0,0.10)',
    'color:#1a1a1a'
  ].join(';');
  panel.innerHTML =
    '<div style="color:#888;font-size:13px;">本文の点線（注のある節）をクリックすると、ここに引照・注が表示されます</div>';
  document.body.appendChild(panel);

  // ── 検索エリアの位置を検出して、その真下にパネルを合わせる ──
  //    （検索マニュアル・タブ・検索ボックス・検索結果はそのまま画面に残る）
  function positionPanel() {
    try {
      // 右カラムの検索入力欄を探す（画面右側・上寄りにある幅広のinput）
      var inputs = document.querySelectorAll('input');
      var input = null;
      for (var i = 0; i < inputs.length; i++) {
        var r = inputs[i].getBoundingClientRect();
        if (r.width > 150 && r.height > 0 &&
            r.left > window.innerWidth * 0.35 &&
            r.top < window.innerHeight * 0.6) { input = inputs[i]; break; }
      }
      if (!input) return; // 見つからなければ前回位置を維持

      var ir = input.getBoundingClientRect();
      // 検索ボックスの行（🔍ボタン含む）の幅に合わせる
      var row = input.parentElement;
      var rr = row ? row.getBoundingClientRect() : ir;
      if (rr.width < ir.width) rr = ir;

      // 「検索結果がありません」等の行があればその下から開始
      var topY = ir.bottom + 64;
      var walker = document.querySelectorAll('div, p, span');
      for (var j = 0; j < walker.length; j++) {
        var el = walker[j];
        if (el.children.length === 0 && el.textContent.indexOf('検索結果') !== -1) {
          var er = el.getBoundingClientRect();
          if (er.height > 0 && er.top > ir.top) { topY = er.bottom + 16; break; }
        }
      }

      panel.style.left = rr.left + 'px';
      panel.style.width = rr.width + 'px';
      panel.style.top = topY + 'px';
      panel.style.right = 'auto';
    } catch (e) { /* 位置調整失敗時は前回位置のまま */ }
  }
  positionPanel();
  setInterval(positionPanel, 800);          // SPAの再描画・リサイズに追随
  window.addEventListener('resize', positionPanel);

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // value属性のHTML断片・エンティティを除去してテキスト化
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
    var a = t.closest('a.v');
    if (!a) return;

    var idx = a.getAttribute('index') || '';
    var p = a.closest('p');

    // この節に属する引照(x)・注(f)を収集
    // （先頭のxスパンは節アンカーの外側に置かれることがあるため、段落全体からtargetで拾う）
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

    if (notes.length === 0) return;  // 注のない節は元の動作のまま

    // 元サイトの注釈画面への遷移を止める
    e.preventDefault();
    e.stopPropagation();

    // 節本文（ルビ付き・注マーカー等は除去）
    var clone = a.cloneNode(true);
    clone.querySelectorAll('span.x, span.f, .v-number, svg').forEach(function (n) { n.remove(); });
    var verseHtml = clone.innerHTML;

    var html =
      '<div style="border:1px solid #e3e8ee;border-radius:8px;padding:10px 12px;margin-bottom:12px;background:#f8fafc;">' +
      (idx ? '<sup style="color:#4a90d9;font-weight:bold;margin-right:4px;font-size:11px;">' + esc(idx) + '</sup>' : '') +
      verseHtml +
      '</div>' +
      '<div style="font-weight:bold;margin-bottom:8px;">引照・注</div>';

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
        '<b style="margin-right:8px;">' + esc(marker) + '</b>' +
        esc(cleanVal(s.getAttribute('value'))) +
        '</div>';
    });

    panel.innerHTML = html;
    panel.scrollTop = 0;
  }, true);
})();
