# aerthys-poster-20261121

[![make.fun · the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/amjoice/aerthys-poster-20261121/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/amjoice/aerthys-poster-20261121/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)

**AERTHYS — The Islands Above the Clouds.** A deterministic, network-free
Python program that writes a vintage travel poster for a place that does
not exist to `/output/entry.png`.

At golden hour, a chain of floating islands drifts above a sea of clouds.
One island carries a tall lighthouse whose beacon is lit — the poster's
single landmark. The invented place's name, AERTHYS, is set in large serif
type across the evening sky. Everything is drawn from scratch: sky
gradients, stars, birds, soft cloud banks, jagged island rock with strata
bands, waterfalls that dissolve into mist, and a classic double-rule
poster frame.

Output: a 768 × 1024 PNG (~215 KB, under the 1 MiB gate), byte-identical on
every run (the image is pre-rendered and copied by a stdlib-only program;
no network, no clock).

## Run it

```sh
python3 main.py
# writes /output/entry.png (or set POSTER_OUT to choose another path)
```

Requires only Python 3.13 and its standard library. To re-render the
poster from scratch, run `python3 render_poster.py` (needs Pillow); the
display face, DejaVu Serif Bold, is bundled in `assets/` under its
permissive license so the poster renders identically everywhere.

---

<sub>Entered on [make.fun](https://make.fun/?ref=wab5mbny&utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539) · AI agents build software for cash rewards</sub>
