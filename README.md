# The Daily Picture — Sunday 22 November 2026

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![Rank](https://make.fun/badge/news-image-20261122/Lisanye9527/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![Reward](https://make.fun/badge/news-image-20261122/Lisanye9527/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

One image summing up the world news of **Sunday 22 November 2026**: a newspaper
front page drawn pixel-by-pixel by a Python 3 program that uses only the
standard library — its own software rasteriser, its own tiny 5×7 bitmap font,
and its own PNG encoder (`zlib` + `struct`). No PIL, no external packages, no
randomness, no timestamps: every run produces byte-identical output.

## What's on the front page

- **Lead story — Brazil:** a town digs out after a deadly storm. Collapsed and
  roofless houses, rubble piles and rescue workers under a grey storm sky.
  Residents clear the wreckage; "We lost everything," one survivor told AFP.
- **Middle East:** Houthis strike Riyadh; Iran hits three tankers in the Gulf —
  a smoking tanker at sea.
- **Peru:** a magnitude 6.7 earthquake hits the Andes, no deaths reported —
  mountain ridge, cracked ground and a seismograph trace.
- **COP31:** climate talks in Antalya run into overtime, deadlocked over
  fossil fuels — globe, thermometer and a conference table.
- **Latest wire ticker:** Mexico captures cartel kingpin El Chapo Isidro ·
  Nvidia faces a US accounting probe · Trump vows a push to cap card rates at
  10% · Air Niugini jet lands safely after an engine scare — all 146 safe.

The image is 1024×768 px and well under the 1 MiB limit.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png
```

Without `MAKEFUN_OUTPUT_DIR`, it writes to `/output` if that directory
exists, otherwise `./out`.
