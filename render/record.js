const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const REC = path.join(__dirname, 'out');
process.on('unhandledRejection', e => { console.error(e); process.exit(1); });
const timing = JSON.parse(fs.readFileSync(path.join(REC, 'timing.json'), 'utf8').replace(/^﻿/, ''));
const total = timing.reduce((a, b) => a + b.dur, 0);

const log = m => fs.appendFileSync(path.join(REC, 'log.txt'), m + '\n');
(async () => { try {
  const b = await puppeteer.launch({
    executablePath: process.env.CHROME_PATH || 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    headless: true, args: ['--window-size=1920,1080', '--autoplay-policy=no-user-gesture-required'],
  });
  const p = await b.newPage();
  await p.setViewport({ width: 1920, height: 1080 });
  await p.goto('file:///' + path.join(__dirname, '..', 'keynote.html').replace(/\\/g, '/'), { waitUntil: 'networkidle0' });
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => { document.querySelector('footer .ctl').style.display = 'none'; });
  await p.evaluate((t) => { for (const x of t) SLIDES[x.s].l[x.j][0] = x.dur; }, timing);
  await new Promise(r => setTimeout(r, 1500));

  const cdp = await p.target().createCDPSession();
  const frames = [];
  let n = 0;
  cdp.on('Page.screencastFrame', async ({ data, metadata, sessionId }) => {
    fs.writeFileSync(path.join(REC, `f${String(n).padStart(5, '0')}.jpg`), Buffer.from(data, 'base64'));
    frames.push({ i: n, t: metadata.timestamp }); n++;
    await cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {});
  });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 85, maxWidth: 1920, maxHeight: 1080, everyNthFrame: 1 });
  await new Promise(r => setTimeout(r, 500));
  await p.evaluate(() => play());
  await new Promise(r => setTimeout(r, (total + 3) * 1000));
  log('stopping '+frames.length); await cdp.send('Page.stopScreencast'); log('stopped');

  // concat demuxer list with per-frame durations
  const lines = ['ffconcat version 1.0'];
  for (let k = 0; k < frames.length; k++) {
    const d = k + 1 < frames.length ? frames[k + 1].t - frames[k].t : 0.05;
    lines.push(`file 'f${String(frames[k].i).padStart(5, '0')}.jpg'`, `duration ${d.toFixed(4)}`);
  }
  lines.push(`file 'f${String(frames[frames.length - 1].i).padStart(5, '0')}.jpg'`);
  fs.writeFileSync(path.join(REC, 'frames.txt'), lines.join('\n'));
  fs.writeFileSync(path.join(REC, 'audio.txt'), timing.map(x => `file '${path.basename(x.file)}'`).join('\n'));
  console.log(frames.length, 'frames over', (frames[frames.length - 1].t - frames[0].t).toFixed(1), 's; audio', total.toFixed(1), 's');
  await b.close(); log("done"); } catch(e){ log("ERR "+(e&&e.stack||e)); process.exit(1);} })();
