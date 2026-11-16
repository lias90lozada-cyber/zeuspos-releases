# -*- coding: utf-8 -*-
"""Guion + linea de tiempo del video ZEUS (90 s, 1080x1920).
Genera: timeline.json (para video y audio), subtitulos.srt y guion_voz.txt
Las palabras entre *asteriscos* se resaltan en dorado en los subtitulos.
"""
import json, re, os

OUT = os.path.join(os.path.dirname(__file__), "..", "build")
DELIV = os.path.join(os.path.dirname(__file__), "..")
os.makedirs(OUT, exist_ok=True)

SCENES = [
    dict(id="hook", name="GANCHO", start=0, end=6, voice_start=0.25,
         text="¿Abres tu *tienda* cada día sin saber qué está pasando *de verdad*? Quédate, porque esto lo *cambia todo*."),
    dict(id="problem", name="PROBLEMA", start=6, end=14, voice_start=6.2,
         text="Hojas de cálculo, diez pestañas abiertas, números por todas partes… y al final del día, sientes que *perdiste horas* sin avanzar."),
    dict(id="reveal", name="PRESENTACIÓN", start=14, end=22, voice_start=14.7,
         text="Eso se acabó. Te presento *Zeus*. Todo el *poder* de tu negocio, en un *solo lugar*."),
    dict(id="store", name="01 · TIENDA", start=22, end=34, voice_start=22.4,
         text="Primero, *tu tienda*. Mira cada *cambio* en el momento en que ocurre: productos, inventario y pedidos, todo en *tiempo real*. Sin buscar. Sin esperar."),
    dict(id="sales", name="02 · VENTAS", start=34, end=46, voice_start=34.4,
         text="Después, *tus ventas*. Descubre qué se vende, cuándo, y *cuánto estás ganando* de verdad. Zeus hace las cuentas por ti: decisiones con *datos*, no con suposiciones."),
    dict(id="views", name="03 · VISTAS", start=46, end=56, voice_start=46.4,
         text="*Tus vistas*. Entiende quién está mirando tus productos, cuáles *atraen más* y dónde estás *perdiendo clientes*."),
    dict(id="research", name="04 · INVESTIGACIÓN", start=56, end=66, voice_start=56.4,
         text="Y con la *investigación* de Zeus, encuentras *tendencias* y oportunidades antes que tu competencia. Sabes qué vender, *antes que todos*."),
    dict(id="productivity", name="05 · PRODUCTIVIDAD", start=66, end=76, voice_start=66.4,
         text="¿El resultado? Lo que antes te tomaba *horas*, ahora te toma *minutos*. Menos tiempo en hojas de cálculo, más tiempo para *hacer crecer* tu negocio."),
    dict(id="cta", name="CIERRE", start=76, end=90, voice_start=76.6,
         text="Si quieres ver *cambios reales* en tu tienda, en tus ventas, en tus vistas y en tu investigación, no esperes más. *Abre Zeus*. Tu negocio, con el *poder de un dios*."),
]

# Efectos de sonido (tiempo en s) -> usados por audio y por el render (sacudidas/flash)
SFX = [
    ("boom", 0.0), ("whoosh", 0.05),
    ("pop", 0.45), ("pop", 0.85), ("pop", 1.25), ("pop", 1.65),
    ("glitch", 5.3),
    ("whoosh", 6.0),
] + [("window", 6.4 + i * 0.55) for i in range(10)] + [
    ("stamp", 10.6),
    ("riser", 11.0),
    ("lightning", 14.0), ("boom", 14.0),
    ("whoosh", 14.5), ("shimmer", 15.0),
    ("whoosh", 17.4),
    ("swoosh_down", 20.6),
    ("transition", 22.0), ("click", 22.3),
] + [("pop", 23.4 + i * 0.12) for i in range(3)] + [("tick", 25.2 + i * 0.25) for i in range(4)] + [
    ("ding", 27.6), ("ding", 30.6), ("blip", 32.0),
    ("transition", 34.0), ("click", 34.3),
    ("counter", 35.0), ("kaching", 37.6),
] + [("pop", 38.4 + i * 0.09) for i in range(7)] + [
    ("whoosh", 40.4), ("shimmer", 42.0), ("pop", 44.0),
    ("transition", 46.0), ("click", 46.3),
    ("counter", 47.2), ("blip", 49.2), ("whoosh", 50.5),
] + [("pop", 51.6 + i * 0.2) for i in range(4)] + [
    ("error", 53.6),
    ("transition", 56.0), ("click", 56.3),
    ("sonar", 57.4), ("sonar", 59.4), ("found", 61.4), ("whoosh", 63.2), ("pop", 63.6), ("pop", 64.0),
    ("transition", 66.0), ("click", 66.3),
    ("stamp", 68.5), ("impact", 69.1),
    ("whoosh", 70.2),
] + [("check", 71.0 + i * 0.6) for i in range(4)] + [
    ("riser", 72.0),
    ("lightning", 76.0), ("boom", 76.0), ("whoosh", 76.3),
    ("whoosh", 79.0), ("impact", 83.0),
    ("click", 85.5), ("success", 85.65),
    ("shimmer", 86.6),
    ("lightning", 88.4), ("boom", 88.4),
]

# Sacudidas de camara (t, amplitud px) y flashes (t, intensidad)
SHAKES = [(0.0, 18), (10.6, 22), (14.0, 46), (37.6, 14), (68.5, 18), (69.1, 24), (76.0, 46), (83.0, 22), (88.4, 40)]
FLASHES = [(14.0, 1.0), (14.15, 0.6), (76.0, 1.0), (76.12, 0.5), (88.4, 0.9)]


def tokens(text):
    out = []
    for w in text.split():
        hl = "*" in w
        out.append(dict(w=w.replace("*", ""), hl=hl))
    # palabras dentro de *...* multi-palabra
    inside = False
    for tk, raw in zip(out, text.split()):
        starts = raw.startswith("*") or raw.startswith("¿*")
        if starts:
            inside = True
        tk["hl"] = inside
        if raw.rstrip(".,:;?¿!…").endswith("*"):
            inside = False
    return out


def chunk(tks, maxw=4):
    chunks, cur = [], []
    for tk in tks:
        cur.append(tk)
        end_punct = re.search(r"[.,:;?!…]$", tk["w"]) is not None
        if len(cur) >= maxw or (end_punct and len(cur) >= 2) or re.search(r"[.?!…]$", tk["w"]):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    return chunks


def weight(ch):
    s = sum(len(t["w"]) + 1.6 for t in ch)
    if re.search(r"[.?!…]$", ch[-1]["w"]):
        s += 4.5
    elif re.search(r"[,:;]$", ch[-1]["w"]):
        s += 2.2
    return s


captions = []
for sc in SCENES:
    tks = tokens(sc["text"])
    chs = chunk(tks)
    nwords = len(tks)
    est = nwords / 2.75  # velocidad aprox. de TTS en espanol (palabras/s)
    v0 = sc["voice_start"]
    v1 = min(sc["end"] - 0.35, v0 + est)
    tot = sum(weight(c) for c in chs)
    t = v0
    for c in chs:
        d = (v1 - v0) * weight(c) / tot
        captions.append(dict(start=round(t, 3), end=round(t + d, 3), words=c, scene=sc["id"]))
        t += d

json.dump(dict(scenes=SCENES, captions=captions, sfx=SFX, shakes=SHAKES, flashes=FLASHES, duration=90, fps=30),
          open(os.path.join(OUT, "timeline.json"), "w"), ensure_ascii=False, indent=1)


def ts(x):
    ms = int(round(x * 1000)); h = ms // 3600000; m = ms // 60000 % 60; s = ms // 1000 % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms % 1000:03d}"


with open(os.path.join(DELIV, "subtitulos.srt"), "w", encoding="utf-8") as f:
    for i, c in enumerate(captions, 1):
        f.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{' '.join(t['w'] for t in c['words'])}\n\n")


def mmss(x):
    return f"{int(x)//60}:{int(x)%60:02d}"


with open(os.path.join(DELIV, "guion_voz.txt"), "w", encoding="utf-8") as f:
    f.write("ZEUS — GUION DE VOZ EN OFF (video vertical 1080x1920, 1:30)\n")
    f.write("=" * 62 + "\n\n")
    f.write("Cómo usarlo en CapCut:\n")
    f.write("  1. Copia cada bloque en 'Texto a voz' (o todo el TEXTO COMPLETO de abajo).\n")
    f.write("  2. Coloca cada audio en el segundo indicado (inicio del bloque).\n")
    f.write("  3. Recomendado: voz masculina o femenina enérgica, velocidad 1.0x–1.1x.\n")
    f.write("  4. Baja la música a ~ -6 dB mientras habla la voz (o usa la pista sin música).\n\n")
    for sc in SCENES:
        f.write(f"[{mmss(sc['start'])} – {mmss(sc['end'])}]  {sc['name']}  (voz empieza en {sc['voice_start']:.1f} s)\n")
        f.write(sc["text"].replace("*", "") + "\n\n")
    f.write("=" * 62 + "\nTEXTO COMPLETO (para pegar de una vez):\n\n")
    f.write("\n\n".join(sc["text"].replace("*", "") for sc in SCENES) + "\n")
    words = sum(len(sc["text"].split()) for sc in SCENES)
    f.write(f"\n({words} palabras · ~{words/2.6:.0f} s de locución)\n")

print("captions", len(captions), "words", sum(len(sc['text'].split()) for sc in SCENES))
