Quiero que me crees un video promocional de Zeus, de principio a fin, usando código. Lee todo esto antes de empezar.

## 0. Material de la marca (OBLIGATORIO antes de nada)
En mi computador hay una carpeta llamada **"Kits and Skills"** (búscala en mi carpeta de usuario: Documentos, Escritorio, Descargas, etc.). Ábrela y revisa TODO lo que contiene:
- **Logo oficial de Zeus** (úsalo tal cual; no inventes ni redibujes el logo).
- Colores, tipografías y estilo de la marca.
- Toda la información de qué hace Zeus y sus funciones, en especial la parte de **investigación: SEO, nichos, palabras clave, oportunidades, competencia, tendencias**.
- Capturas de pantalla de la app si las hay (úsalas como referencia para que la interfaz del video se parezca a la real).

Antes de programar, dame un **resumen corto** de lo que encontraste (funciones de Zeus, colores, fuentes, archivos del logo) para confirmar que lo entendiste. **No inventes funciones que Zeus no tenga.**

## 1. Base de trabajo existente
Ya existe una primera versión en el repo de GitHub `lias90lozada-cyber/zeuspos-releases`, rama `claude/jolly-goldberg-qvahml`, carpeta `video-zeus/`:
- `src/script.py`: guion, tiempos, subtítulos (.srt) y lista de efectos de sonido → `build/timeline.json`
- `src/zeus.html`: motor de animación en canvas (función `render(t)` determinista)
- `src/render.js`: captura fotograma a fotograma con Playwright (Chromium), en paralelo
- `src/audio.py`: música y efectos sintetizados con numpy/scipy
- ffmpeg une los fotogramas y el audio en un MP4

Puedes reutilizar ese sistema (clonarlo) o mejorarlo, pero corrigiendo todo lo de la sección 2. Instala lo que falte (Node + Playwright con Chromium, Python con numpy/scipy, ffmpeg).

## 2. Lo que NO me gustó de la versión anterior (corregirlo sí o sí)
1. **Todo saltaba todo el tiempo**: había un zoom que pulsaba con cada golpe de la música, sacudidas de cámara y rebotes exagerados en casi cada elemento. → Quita el zoom de pulso por completo. Usa movimientos **suaves, fluidos y premium** (ease-in-out, deslizamientos, fundidos, máscaras), con rebote muy leve o ninguno. Como máximo 2–3 momentos de impacto en todo el video (aparición del logo y cierre), y aun así sutiles.
2. **El inicio era lento**: no sirve para retener los primeros 3 segundos. → Desde el **segundo 0** debe haber un gancho directo: texto grande en pantalla + voz diciendo el problema o la promesa. Nada de intros lentas ni pantallas vacías.
3. **No se explicó la investigación**: me centré solo en tienda, ventas y vistas. → La sección de **investigación** debe ser la más completa y explicar paso a paso (según lo que haga Zeus de verdad): cómo encuentra **nichos**, **palabras clave y SEO**, nivel de **competencia**, **oportunidades** y tendencias, y por qué eso le da ventaja al usuario. Que se entienda de forma práctica, con ejemplos visuales.
4. **No usé el logo oficial**. → Usa el logo de la carpeta en la presentación, en una esquina durante el video (discreto) y en el cierre.
5. **Los subtítulos no se notaban**. → Pon **subtítulos karaoke dinámicos** (detalles en la sección 4).

## 3. Especificaciones del video
- **Duración: 1:30 (90 s)**. **Vertical 1080×1920 (Full HD) para TikTok**, 30 fps, MP4 H.264 + AAC, `-movflags +faststart`.
- Estilo **motion graphics animado** con la identidad visual de Zeus (colores y fuentes del kit).
- Objetivo: que el usuario vea el video completo y entienda de forma práctica que **necesita abrir Zeus** si quiere ver cambios en su **tienda, ventas, vistas e investigación**, y **ahorrar tiempo** (productividad).
- Retención: gancho fuerte en el primer segundo, algo nuevo en pantalla cada 2–3 s (pero sin saltos bruscos), intriga al inicio ("quédate hasta el final…"), barra de progreso de secciones y una llamada a la acción final clara: **"Abre Zeus"**.
- Respeta la zona segura de TikTok: nada importante en los ~250 px de abajo ni en la franja derecha donde van los botones.
- Estructura sugerida (ajústala según las funciones reales de Zeus):
  - 0–3 s: gancho directo
  - 3–9 s: problema (tiempo perdido, datos dispersos, no saber qué vender)
  - 9–14 s: presentación de Zeus con el logo oficial
  - 14–24 s: Tienda
  - 24–34 s: Ventas
  - 34–42 s: Vistas
  - 42–70 s: **Investigación** (nichos → palabras clave/SEO → competencia → oportunidades)
  - 70–78 s: Productividad / ahorro de tiempo
  - 78–90 s: cierre y llamada a la acción con el logo

## 4. Subtítulos karaoke (incrustados en el video)
- Palabra por palabra, sincronizados con la voz.
- La palabra que se está diciendo se ilumina con un **recuadro de color de la marca detrás** y un ligero aumento de tamaño, con transición suave.
- Palabras clave (Zeus, ventas, nichos, SEO, oportunidades…) en color de acento.
- Letra grande y gruesa con contorno/sombra, máximo 2 líneas y 3–5 palabras por bloque, en la zona segura (aprox. y = 1350–1550).
- Entrega también una versión del video **sin subtítulos** y el archivo `.srt`.

## 5. Voz (la pongo yo en CapCut)
- No generes voz. Escribe primero el **guion nuevo** (unas 190–210 palabras para 90 s, en español, tono enérgico y cercano) y **muéstramelo para aprobarlo antes de animar**.
- Entrégamelo en `guion_voz.txt`, separado por bloques con el segundo exacto en que empieza cada uno, y al final el texto completo seguido para pegarlo de una vez en "Texto a voz" de CapCut.
- **Sincronización exacta (preferido):** después de aprobar el guion te daré el audio de la voz exportado desde CapCut. Usa Whisper (`faster-whisper` u `openai-whisper`, con marcas de tiempo por palabra) para obtener el momento exacto de cada palabra y sincroniza con la voz real los subtítulos karaoke, los cambios de escena y las animaciones clave. Si no te doy el audio, estima los tiempos a unas 2.7 palabras por segundo.

## 6. Música y efectos de sonido (hechos con código)
- Música de fondo sintetizada con código (numpy/scipy o similar): electrónica moderna y motivadora, con buen ritmo que retenga (~110–124 BPM), tonalidad épica y tecnológica, coherente con "el poder de Zeus". Que tenga estructura: entrada con energía desde el segundo 0 (no intro lenta), un drop cuando aparece el logo, una variación en la sección de investigación y un segundo clímax en el cierre. Volumen pensado para dejar espacio a la voz (sidechain suave).
- Efectos de sonido sutiles y sincronizados con lo que pasa en pantalla: whooshes en transiciones, pops suaves al aparecer elementos, notificación en pedidos, caja registradora en ventas, sonido de escaneo/búsqueda en investigación, checks en productividad, trueno en la aparición del logo, clic en el botón final. No saturar.
- Entrega por separado: `musica_fondo.mp3`, `efectos_sonido.mp3` y la mezcla dentro del video.

## 7. Control de calidad (antes de entregarme nada)
- Antes del render completo, genera fotogramas sueltos de cada escena, revísalos tú mismo (hojas de contacto) y corrige textos que se salgan, solapamientos, cosas que se tapen y legibilidad.
- Comprueba que no haya zoom pulsante ni movimientos bruscos repetidos.
- Revisa niveles de audio (sin saturación, picos ≈ −1 dBFS).
- Verifica con ffprobe: 1080×1920, 30 fps, 90 s.

## 8. Entregables (en una carpeta `ZEUS_video_v2` en mi Escritorio)
1. `ZEUS_video_v2_1080x1920.mp4`: con subtítulos karaoke
2. `ZEUS_video_v2_SIN_subtitulos_1080x1920.mp4`
3. `guion_voz.txt`
4. `subtitulos.srt`
5. `musica_fondo.mp3` y `efectos_sonido.mp3`
6. El código fuente para poder regenerarlo con cambios

Orden de trabajo: (1) revisar el kit y darme el resumen → (2) guion nuevo para aprobar → (3) cuando lo apruebe, animación + música + efectos → (4) control de calidad → (5) entrega. Si en algún punto te falta algo del kit, pregúntame.
