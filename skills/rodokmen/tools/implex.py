"""Předek v rodokmenu vícekrát (SAME v data/osoby.py, „implex“ – vzdálení příbuzní se vzali).

SAME = {alias: hlavní číslo}: údaje jsou jen u hlavního čísla, ale na místě aliasu (a nad ním) jsou titíž předci.
Vějíř, rodokmen na úvodu i rody je proto mají ukázat na obou místech: místo 2·alias je 2·hlavní, 4·alias+1 je
4·hlavní+1 atd. Výslovně zapsaná osoba v P má přednost (kdo předky nad aliasem zapsal i podruhé, má je tam)."""


def puvod(k, P, SAME, limit=64):
    """Číslo osoby v P, jejíž údaje patří na místo k: k samo, nebo místo zrcadlené přes SAME; None = nikdo.
    Alias s vlastní položkou v P (f=["TÁŽ OSOBA jako …"]) se bere z hlavního čísla."""
    for _ in range(limit):   # řetězce aliasů (alias nad aliasem) i chybná data (smyčka) skončí nejpozději tady
        if k in P and k not in SAME:
            return k
        for d in range(k.bit_length()):
            a = k >> d
            if a in SAME:
                k = (SAME[a] << d) | (k & ((1 << d) - 1))
                break
        else:
            return None
    return None


def zrcadla(P, SAME, max_gen=60):
    """{místo: číslo osoby v P} pro všechna místa na aliasech a nad nimi, kde je známý předek (bez míst, která
    mají vlastní osobu v P). Prochází se jen nahoru od aliasu, dokud jsou předci známí, nejvýš do max_gen."""
    out, stack = {}, [a for a in SAME if a.bit_length() - 1 <= max_gen]
    while stack:
        s = stack.pop()
        src = puvod(s, P, SAME)
        if src is None:
            continue
        if src != s:
            out[s] = src
        if s.bit_length() <= max_gen:   # rodiče mají generaci gen(s) + 1 = bit_length(s)
            stack += [2 * s, 2 * s + 1]
    return out
