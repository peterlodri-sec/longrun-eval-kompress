# How to Make Full glyphcss Render (Gap-Free Blocks)

## The Problem

Unicode block characters (█ ▀ ▄ ▌ ▐ etc.) rendered via font glyphs leave
thin gaps between cells. This is because:

1. Font metrics don't perfectly fill the cell height/width
2. Browser font smoothing adds anti-aliasing at edges
3. Sub-pixel rendering varies across browsers/OS

The visual result: ████████████ shows hairline gaps between blocks.

## Solution 1: CSS text-shadow (Quick Fix)

```css
.glyphcss-pre {
  font-family: monospace;
  line-height: 1;
  letter-spacing: 0;
  /* Shadow bleeds into adjacent pixel gaps */
  text-shadow:
    0.5px 0 0 currentColor,
    -0.5px 0 0 currentColor,
    0 0.5px 0 currentColor,
    0 -0.5px 0 currentColor;
}
```

**Pros:** One line of CSS, works everywhere
**Cons:** Slightly fuzzy edges, only works for single-color blocks

## Solution 2: Canvas fillRect (Ghostty Approach)

Instead of rendering block characters as font glyphs, draw them as filled
rectangles on a canvas. This is what production terminals do:

```javascript
function renderBlockChar(ctx, codepoint, x, y, w, h) {
  switch (codepoint) {
    case 0x2588: // █ FULL BLOCK
      ctx.fillRect(x, y, w, h);
      return true;
    case 0x2580: // ▀ UPPER HALF BLOCK
      ctx.fillRect(x, y, w, h / 2);
      return true;
    case 0x2584: // ▄ LOWER HALF BLOCK
      ctx.fillRect(x, y + h/2, w, h / 2);
      return true;
    case 0x2590: // ▐ RIGHT HALF BLOCK
      ctx.fillRect(x + w/2, y, w/2, h);
      return true;
    case 0x258C: // ▌ LEFT HALF BLOCK
      ctx.fillRect(x, y, w/2, h);
      return true;
    // ... all U+2580-U+259F block elements
  }
  return false;
}
```

**Pros:** Pixel-perfect, no gaps
**Cons:** Requires canvas, loses text selection

## Solution 3: Braille Palette (Best for glyphcss)

Use `glyphPalette="braille"` instead of `blocks`:

```html
<glyph-scene mode="solid" glyph-palette="braille" cols="80" rows="24">
  <glyph-mesh src="/model.glb" />
</glyph-scene>
```

Braille characters (⣿ ⠿ ⠛ etc.) encode 8 dots per character cell,
giving 2× horizontal and 4× vertical resolution. No gap problem
because Braille characters naturally fill their cell bounds.

**Pros:** Highest resolution, no gaps, works in glyphcss as-is
**Cons:** Less "blocky" aesthetic than full blocks

## Solution 4: Custom Font with Oversized Metrics

Create a font where block characters extend 1-2 pixels beyond the
cell bounds on all sides. The overshoot fills the gap.

Tools:
- FontForge: https://fontforge.org
- Modify U+2588 glyph to extend beyond em square
- Set OS/2 metrics: sTypoLineGap=0, usWinAscent/Descent = cell height

**Pros:** Works everywhere, no CSS hacks
**Cons:** Custom font maintenance, may break other glyphs

## Solution 5: Background Color Trick

```css
.glyphcss-container {
  background: #000;
}
.glyphcss-pre {
  color: #000;  /* text color matches background */
}
/* Then use <span> elements for colored blocks */
```

Each block character gets a `<span style="background: red">█</span>`.
The background fills the gap because it extends to cell edges.

**Pros:** Works with any font
**Cons:** Requires DOM manipulation, not pure text output

## Solution 6: Hybrid (Recommended for glyphcss)

1. Use `useColors: true` to emit `<span>` color elements
2. Add CSS `text-shadow` bleed
3. Use `cellAspect: 1.0` for square cells
4. Set `line-height: 1` and `letter-spacing: -0.02em`

```html
<style>
  .glyphcss-output {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    line-height: 1;
    letter-spacing: -0.02em;
    text-shadow: 0.5px 0 0 currentColor;
    white-space: pre;
  }
</style>

<glyph-scene
  mode="solid"
  glyph-palette="blocks"
  use-colors="true"
  cell-aspect="1.0"
  cols="120"
  rows="40"
>
  <glyph-mesh src="/model.obj" />
</glyph-scene>
```

## Terminal-Specific Fixes

### iTerm2
- Preferences → Profiles → Text → Use font for non-ASCII
- Set line spacing to 0

### Ghostty
Already renders block characters as rects (built-in fix)

### Kitty
Already renders block characters as rects (built-in fix)

### Alacritty
Issue #5485 — special rect rendering planned but not yet implemented.
Workaround: use a font like JetBrains Mono with good block metrics.

### Windows Terminal
- Settings → Appearance → Line height: 1.0
- Use a Nerd Font with good block metrics

## For CodeWhale Integration

CodeWhale uses ratatui for TUI rendering. The block gap problem is
terminal-dependent, not agent-dependent. To display glyphcss output
in CodeWhale's context:

1. **Browser preview:** glyphcss renders in `<pre>` — works directly
2. **Terminal output:** Convert glyphcss grid to ANSI escape sequences:
   ```python
   def glyphcss_to_ansi(grid, colors):
       for row in grid:
           line = ""
           for i, cell in enumerate(row):
               r, g, b = colors[i]
               line += f"\033[48;2;{r};{g};{b}m "
           line += "\033[0m"
           print(line)
   ```
3. **Clipboard:** Copy glyphcss output as plain text → paste into terminal

## Summary

| Method | Quality | Effort | Works in glyphcss |
|--------|---------|--------|-------------------|
| CSS text-shadow | Good | Trivial | Yes |
| Canvas fillRect | Perfect | Medium | Needs override |
| Braille palette | Perfect | Trivial | Yes (built-in) |
| Custom font | Perfect | High | Yes |
| Background trick | Good | Low | Yes (with spans) |
| Hybrid CSS | Very Good | Low | Yes |
