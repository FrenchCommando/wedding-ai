// One still of the stage view at a given slide/beat: node snap.js [slide] [beat] [out.png]
const puppeteer = require('puppeteer-core');
const path = require('path');
const [slide = 4, beat = 3, out = `out/snaps/s${slide}b${beat}.png`] = process.argv.slice(2);
require('fs').mkdirSync(path.join(__dirname, 'out', 'snaps'), { recursive: true });
(async () => {
  const b = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe', headless: true });
  const p = await b.newPage();
  await p.setViewport({ width: 1920, height: 1080 });
  await p.goto('file:///' + path.join(__dirname, '..', 'keynote.html').replace(/\\/g, '/') + '?stage', { waitUntil: 'networkidle0' });
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate((s, j) => { document.getElementById('exit').remove(); go(+s, +j); }, slide, beat);
  await new Promise(r => setTimeout(r, 1500));
  await p.screenshot({ path: path.join(__dirname, out) });
  const errs = await p.evaluate(() => window.__errs || []);
  console.log('saved', out, errs);
  await b.close();
})();
