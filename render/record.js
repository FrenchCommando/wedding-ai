// Plays the deck in headless Chrome and pipes the screencast into ffmpeg as a
// constant 30 fps H.264 stream -> out/video/stage.mp4. No frames touch the disk.
const puppeteer = require('puppeteer-core');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const REC = path.join(__dirname, 'out');
const FPS = 30;
const timing = JSON.parse(fs.readFileSync(path.join(REC, 'timing.json'), 'utf8').replace(/^\uFEFF/, ''));
const total = timing.reduce((a, b) => a + b.dur, 0);
fs.mkdirSync(path.join(REC, 'video'), { recursive: true });
const ffmpeg = execFileSync(
  process.env.PYTHON || path.join(__dirname, 'venv', 'Scripts', 'python.exe'),
  ['-c', 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'], { encoding: 'utf8' }).trim();

process.on('unhandledRejection', e => { console.error(e); process.exit(1); });

(async () => {
  const b = await puppeteer.launch({
    executablePath: process.env.CHROME_PATH || 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    headless: true, args: ['--window-size=1920,1080'],
  });
  const p = await b.newPage();
  await p.setViewport({ width: 1920, height: 1080 });
  const url = 'file:///' + path.join(__dirname, '..', 'keynote.html').replace(/\\/g, '/') + (process.env.PLAIN ? '' : '?stage');
  await p.goto(url, { waitUntil: 'networkidle0' });
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => { document.querySelector('footer .ctl').style.display = 'none'; const e = document.getElementById('exit'); if (e) e.remove(); });
  await p.evaluate((t) => { for (const x of t) SLIDES[x.s].l[x.j][0] = x.dur; }, timing);
  await new Promise(r => setTimeout(r, 1500));

  const enc = spawn(ffmpeg, [
    '-y', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', 'pipe:0',
    '-vf', 'format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-r', String(FPS),
    path.join(REC, 'video', process.env.PLAIN ? 'plain.mp4' : 'stage.mp4'),
  ], { stdio: ['pipe', 'inherit', 'inherit'] });

  // latest screencast frame; a 30 Hz clock writes it to ffmpeg (dup or drop as needed)
  let latest = null, written = 0;
  const cdp = await p.target().createCDPSession();
  cdp.on('Page.screencastFrame', ({ data, sessionId }) => {
    latest = Buffer.from(data, 'base64');
    cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {});
  });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 90, maxWidth: 1920, maxHeight: 1080, everyNthFrame: 1 });
  while (!latest) await new Promise(r => setTimeout(r, 20));

  const t0 = Date.now();
  await p.evaluate(() => play());
  const end = t0 + (total + 2) * 1000;
  while (Date.now() < end) {
    const due = Math.floor((Date.now() - t0) / 1000 * FPS);
    while (written <= due) { if (!enc.stdin.write(latest)) await new Promise(r => enc.stdin.once('drain', r)); written++; }
    await new Promise(r => setTimeout(r, 5));
  }
  await cdp.send('Page.stopScreencast');
  enc.stdin.end();
  await new Promise(r => enc.on('close', r));
  console.log(`${written} frames at ${FPS} fps = ${(written / FPS).toFixed(1)} s; audio ${total.toFixed(1)} s`);
  await b.close();
})();
