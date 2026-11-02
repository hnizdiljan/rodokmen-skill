// Vojáci v rodu: fakta a poznámky, které zmiňují vojnu, válku, pluk, legie nebo odboj (stránka /vojaci/ a položka menu).
export const VOJ = /(?<![\p{L}])(vojn|vojen|voják|vojín|vojsk|pluk|praporu|setnin|legion|legii|padl|nezvěst|Verlust|seznam\p{L}* ztrát|záložník|v záloze|odveden|odvod|mobiliz|partyz|odboj|zajet|zajat|raněn|front|honvéd|landwehr|četník|důstojn|desátník|šikovatel|svobodník|kaprál|světov\p{L}* válk|válečn|Wehrmacht|gestap|SNP)/iu;
const roky = (s) => (s || '').match(/\d{4}/g)?.map(Number) || [];

/** Přímí předci s vojenskými fakty a příbuzní mimo přímou linii (SIDE, RODINA), řazení podle roku narození. */
export function vojaci(people) {
  const predci = Object.values(people)
    .map((p) => ({ p, fakta: [...p.facts, p.note].filter((f) => f && VOJ.test(f)) }))
    .filter(({ fakta }) => fakta.length)
    .sort((a, b) => (roky(a.p.years)[0] || 9999) - (roky(b.p.years)[0] || 9999));
  const bocni = Object.values(people).flatMap((p) => p.side.filter((s) => VOJ.test(`${s.name} ${s.text}`)).map((s) => ({ s, u: p })));
  return { predci, bocni };
}
