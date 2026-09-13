const puppeteer = require('puppeteer-core');
const fs = require('fs');
(async () => {
  const path = require('path');
  const b = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe', headless: true });
  const p = await b.newPage();
  await p.goto('file:///' + path.join(__dirname, '..', 'keynote.html').replace(/\\/g, '/'));
  const beats = await p.evaluate(() => SLIDES.flatMap((s, i) => s.l.map(([d, t], j) => ({ s: i, j, d, t }))));
  fs.writeFileSync(require('path').join(__dirname, 'out/beats.json'), JSON.stringify(beats, null, 1));
  console.log(beats.length, 'beats');
  await b.close();
})();
