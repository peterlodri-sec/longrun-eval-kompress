# ENTHEA Neural Field Background

Self-hostable WebGL2 background shader. Drop-in, zero dependencies.

## Usage

```html
<script src="enthea-bg.js" defer></script>
```

That's it. The script creates a fixed full-screen canvas behind your content and renders a neural-field pattern in real time.

## What it does

- **Neural field simulation** — simplex noise + domain warping, inspired by Wilson-Cowan Turing bifurcation models
- **Klüver form constants** — tunnel-like radial mapping from the visual cortex math
- **Steganographic identity** — encodes a username into the shader seeds via ASCII folding
- **Low overhead** — 25% render resolution, 20fps cap, `powerPreference: "low-power"`
- **Accessibility** — disabled entirely when `prefers-reduced-motion: reduce`

## Customization

Edit the `ID` constant at the top of the IIFE to encode your own identity:

```js
const ID = "your-github-username";
```

Adjust these values:

| Constant | Effect |
|----------|--------|
| `SCALE` | Render resolution (0.25 = 25% of display) |
| `TARGET_FPS` | Frame rate cap |
| `opacity` | Canvas CSS opacity (in the style object) |

## License

**AGPL-3.0** — this is a derivative work of [ENTHEA](https://github.com/elder-plinius/ENTHEA) by [elder-plinius](https://github.com/elder-plinius) (Pliny the Liberator).

If you use this, credit the original:

```
Neural field background derived from ENTHEA (https://github.com/elder-plinius/ENTHEA)
by elder-plinius. Licensed under AGPL-3.0.
```

Respect the source. The math is the gift.
