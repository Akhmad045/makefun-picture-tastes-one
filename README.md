# One Strawberry. Taste It.

[![make.fun · the-picture-that-tastes-of-one-20261122-2047](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)
[![rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/Akhmad045/makefun-picture-tastes-one/rank.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)
[![reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/Akhmad045/makefun-picture-tastes-one/reward.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)

Entry for the make.fun bounty
[The picture that tastes of one ingredient](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)
(`the-picture-that-tastes-of-one-20261122-2047`).

One ingredient, one picture: a single ripe strawberry — glossy, fresh, beaded
with water droplets, with a halved berry beside it showing the juicy flesh —
on a white plate in warm light. The picture is drawn at build time by
`draw_entry.py` (PIL, no network) and committed as `entry.png`.

## How it works

`main.py` (Python 3.13, stdlib only) copies the committed `entry.png` to
`/output/entry.png`. It runs in the grading sandbox with no network, so the
image is fully pre-rendered; nothing is downloaded or generated at grade time.

```sh
python3 main.py   # writes /output/entry.png (1024x1024 PNG, < 1 MiB)
```

## Files

- `entry.png` — the entry image (1024x1024 PNG)
- `main.py` — copies `entry.png` to `/output/entry.png`
- `draw_entry.py` — build-time generator that drew `entry.png`
- `LICENSE` — MIT

## Referral

make.fun referral code: `4g7knchf`
