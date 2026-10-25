// Records the Codigo slide frame by frame with Playwright's fake clock.
// usage: node cdrec.cjs <outdir> _ _ [fps] [onlyFrames,comma]
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
const { execFileSync } = require('child_process'), fs = require('fs');
(async () => {
  const [dir, t0, t1, fpsArg, only] = process.argv.slice(2), fps = +(fpsArg || 30);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1400, height: 788 }, deviceScaleFactor: 2 });
  const cache = {};
  await p.route(/^https:\/\/(cdn\.jsdelivr\.net|fonts\.googleapis\.com|fonts\.gstatic\.com)\//, async route => {
    const u = route.request().url();
    if (!cache[u]) {
      const out = execFileSync('curl', ['-sSL', '-D', '-', '-A', 'Mozilla/5.0 Chrome/120', u], { maxBuffer: 1 << 28 });
      let i = out.indexOf('\r\n\r\n'), head = out.slice(0, i).toString(), body = out.slice(i + 4);
      while (/^HTTP\/\S+ 3/.test(head) || /^HTTP\/\S+ 200 Connection established/i.test(head)) { const j = body.indexOf('\r\n\r\n'); head = body.slice(0, j).toString(); body = body.slice(j + 4); }
      cache[u] = { body, ct: (head.match(/content-type:\s*([^\r\n]+)/i) || [])[1] || 'application/javascript' };
    }
    await route.fulfill({ status: 200, body: cache[u].body, headers: { 'content-type': cache[u].ct, 'access-control-allow-origin': '*' } });
  });
  p.on('console', m => { if (/^dbg/.test(m.text())) console.log(m.text()) });
  p.on('pageerror', e => console.log('err:', e.message));
  await p.goto('http://localhost:8806/?capture' + (process.env.Q ? '&' + process.env.Q : ''));
  await p.waitForFunction(() => window.__ready, null, { timeout: 60000 });
  const H = await p.evaluate(() => window.__H || 788); await p.setViewportSize({ width: 1400, height: H }); console.log('height', H);
  const total = await p.evaluate(() => window.__TOTAL), n = Math.round((total + +(process.env.EXTRA || 0)) * fps);
  const want = only ? new Set(only.split(',').map(Number)) : null;
  for (let i = 0; i < n; i++) {
    if (want && !want.has(i)) continue;
    await p.evaluate(t => window.__render(t), i / fps);
    await p.screenshot({ path: `${dir}/f${String(i).padStart(4, '0')}.png` });
  }
  console.log('total', total);
  console.log('frames', n); await b.close();
})();
