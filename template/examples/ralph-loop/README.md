# ralph-loop

> ultra cavemanified loop engineering. one file. no fancy. just loop.

## what is this

the most stripped-down possible Loop Engineering example. one file.
no separate experiment.py. no evaluate.py. no data.py. just ralph.

ralph doesn't know about "separation of concerns." ralph has one file
and he's not afraid to use it.

## how to run

```bash
cd template/examples/ralph-loop

# run the loop (it does everything in one file)
python ralph.py

# that's it. there's no config. there's no options. it just runs.
```

## what ralph does

ralph tries to find the best "compression ratio" for a list of numbers.
he doesn't know what that means. he just keeps trying ratios until
the score stops improving.

the loop:
1. plan: pick a ratio to try
2. execute: compress the numbers with that ratio
3. evaluate: score how well it worked
4. decide: keep going or stop

ralph doesn't know what SHIP/RETRAIN/PIVOT means. he just says
"good enough" or "try harder."

## files

```
ralph-loop/
├── ralph.py       <- everything. the whole thing. one file.
├── STATE.md       <- ralph's state (he updates it sometimes)
└── README.md      <- you're reading it
```

## the ralph philosophy

- one file is enough
- if it works, ship it
- if it doesn't work, try harder
- if trying harder doesn't work, try something else
- if nothing works, take a nap
- never over-engineer anything
- the loop is already here

## history

named after Ralph Wiggum, who famously said:
> "I'm in danger!"

which is also how most ML researchers feel during training.
