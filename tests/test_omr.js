// 読み取り処理のテスト（Node.jsで実行: node tests/test_omr.js）
// 先に python tests/make_test_images.py で画像を作っておくこと。
// HTMLから LAYOUT と OMR の部分だけを取り出して動かす。
const fs = require('fs'), path = require('path');
const html = fs.readFileSync(path.join(__dirname, '..', 'marksheet-saiten.html'), 'utf8');
const s = html.indexOf('const LAYOUT'), e = html.indexOf('/* ============================================================\n   3.');
if (s < 0 || e < 0) { console.error('HTMLからOMR部分を取り出せません（区切りコメントを変えていないか確認）'); process.exit(1); }
const core = new Function('state', html.slice(s, e) + '\nreturn { OMR };');
const out = path.join(__dirname, 'out'), expected = JSON.parse(fs.readFileSync(path.join(out, 'expected.json'), 'utf8'));
let fail = 0;
for (const [name, ex] of Object.entries(expected)) {
  const state = { settings: { written: Array(ex.written).fill({}), writtenSize: ex.size } };
  const { OMR } = core(state);
  const b = fs.readFileSync(path.join(out, name + '.raw'));
  const w = b[0]*256 + b[1], h = b[2]*256 + b[3];
  const r = OMR.analyze(new Uint8Array(b.subarray(4)), w, h);
  const errs = [];
  if (r.error) errs.push(r.error);
  else {
    if (r.rotated !== ex.rotated) errs.push('上下判定が違う');
    const id = r.idFills.map(f => OMR.decide(f, 0.35).value);
    if (id.join() !== ex.id.join()) errs.push(`組番号 ${id} (正解 ${ex.id})`);
    ex.answers.forEach((a, q) => { const v = OMR.decide(r.fills[q].slice(0, 10), 0.35).value; if (v !== a) errs.push(`問${q+1}: ${v} (正解 ${a})`); });
  }
  console.log((errs.length ? 'FAIL ' : 'PASS ') + name + (errs.length ? '\n  ' + errs.slice(0, 10).join('\n  ') : ''));
  if (errs.length) fail++;
}
process.exit(fail ? 1 : 0);
