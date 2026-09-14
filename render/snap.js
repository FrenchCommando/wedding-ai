// One still of the stage view: node snap.js [slide] [beat] [cam: wide|close|threeq|speaker] [out.png]
const puppeteer = require('puppeteer-core');
const path = require('path');
const [slide = 4, beat = 3, camArg = '', out = `out/snaps/s${slide}b${beat}${camArg && '-' + camArg}.png`] = process.argv.slice(2);
require('fs').mkdirSync(path.join(__dirname, 'out', 'snaps'), { recursive: true });
(async () => {
  const b = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe', headless: true });
  const p = await b.newPage();
  await p.setViewport({ width: 1920, height: 1080 });
  await p.goto('file:///' + path.join(__dirname, '..', 'keynote.html').replace(/\\/g, '/') + '?stage', { waitUntil: 'networkidle0' });
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate((s, j, c) => { document.querySelector('.ctl').remove(); go(+s, +j); if (c) { cam = c; camSince = performance.now(); } }, slide, beat, camArg);
  await new Promise(r => setTimeout(r, 1500));
  await p.screenshot({ path: path.join(__dirname, out) });
  console.log('saved', out, 'cam =', await p.evaluate(() => cam));
  await b.close();
})();
