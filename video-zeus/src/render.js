// Uso: node render.js frames <outDir> <startFrame> <endFrame> [nosubs]
//      node render.js stills <outDir> t1,t2,...
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const TL = JSON.parse(fs.readFileSync(path.join(__dirname, '../build/timeline.json'), 'utf8'));

(async () => {
  const [mode, out, a, b, flag] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files', '--disable-web-security'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.addInitScript(tl => { window.__TL__ = tl; }, TL);
  page.on('pageerror', e => console.error('PAGEERR', e.message));
  await page.goto('file://' + path.join(__dirname, 'zeus.html'));
  await page.evaluate(() => window.ready);
  if (flag === 'nosubs') await page.evaluate(() => { window.SUBS = false; });
  const canvas = await page.$('#c');
  const shot = async (t, file) => { await page.evaluate(t => window.render(t), t); await canvas.screenshot({ path: file, type: 'jpeg', quality: 93 }); };
  if (mode === 'stills') {
    for (const t of a.split(',').map(Number)) await shot(t, path.join(out, `t_${t.toFixed(2)}.jpg`));
  } else {
    const s = +a, e = +b, t0 = Date.now();
    for (let f = s; f < e; f++) {
      await shot(f / TL.fps, path.join(out, `f_${String(f).padStart(5, '0')}.jpg`));
      if ((f - s) % 150 === 0) console.log(`[${s}-${e}] frame ${f} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
  }
  await browser.close();
})();
