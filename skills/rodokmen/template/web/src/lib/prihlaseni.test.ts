// Záložní SHA-256 z přihlašovací stránky (prihlaseni.sablona.html) – musí dát stejný otisk jako server
// (export_web.py: hashlib.sha256). Spouští se s ostatními testy: npm test
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

const page = readFileSync(new URL('../../prihlaseni.sablona.html', import.meta.url), 'utf8');
const code = /\/\/ sha256-start([\s\S]*?)\/\/ sha256-end/.exec(page);
assert.ok(code, 'v prihlaseni.sablona.html chybí blok // sha256-start … // sha256-end');
const sha256 = new Function(`${code[1]}; return sha256;`)() as (b: Uint8Array) => string;
const expected = (b: Uint8Array) => createHash('sha256').update(b).digest('hex');

test('záložní SHA-256: známé hodnoty', () => {
  const enc = (s: string) => new TextEncoder().encode(s);
  assert.equal(sha256(enc('')), 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');
  assert.equal(sha256(enc('abc')), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
  assert.equal(sha256(enc('rodokmen:novak')), expected(enc('rodokmen:novak')));
});

test('záložní SHA-256: všechny délky přes hranice bloků (55/56/64 B …)', () => {
  for (let n = 0; n <= 200; n++) {
    const b = Uint8Array.from({ length: n }, (_, i) => (i * 31 + n) % 256);
    assert.equal(sha256(b), expected(b), `délka ${n}`);
  }
});
