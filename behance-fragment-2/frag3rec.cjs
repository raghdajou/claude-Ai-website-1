// Records Fragment Reveal II frame by frame at 2x. usage: node frag3rec.cjs <outdir> <fps>
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
(async () => {
  const [dir, fpsArg] = process.argv.slice(2), fps = +fpsArg;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1400, height: 788 }, deviceScaleFactor: 2 });
  await p.goto('http://localhost:8803/?capture'); await p.waitForFunction(() => window.__ready); await p.waitForTimeout(300);
  const total = await p.evaluate(() => window.__TOTAL), n = Math.round(total * fps);
  for (let i = 0; i < n; i++) { await p.evaluate(t => window.__render(t), i / fps); await p.screenshot({ path: `${dir}/f${String(i).padStart(4, '0')}.png` }); }
  console.log('frames', n, total); await b.close();
})();
