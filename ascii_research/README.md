# ASCII Research Dump

Research on glyphcss, CodeWhale/Whale, and full block character rendering.

## Files

- `glyphcss.md` — Full research on glyphcss architecture, palettes, render pipeline,
  performance optimizations, fonts/WordArt, texture sampling, shadows, and the
  block character gap problem with solutions.

- `full_render_howto.md` — Specific guide on how to achieve gap-free full block
  rendering in glyphcss and terminals. Covers CSS hacks, canvas rect rendering,
  braille palette, custom fonts, and terminal-specific fixes.

## Key Findings

### glyphcss
- ASCII polygon-mesh renderer for DOM — single `<pre>` output
- 12 built-in palettes including `blocks`, `braille`, `ascii`
- 40% performance improvement via cross-frame shading cache
- Per-cell UV texture sampling (PR #13)
- Fonts/WordArt support (extrude Google fonts to 3D ASCII)

### CodeWhale / Whale
- Terminal coding agent for DeepSeek V4
- ~98% prompt cache hit, 1M context, MCP tools
- Rust binary pair (codewhale + codewhale-tui)
- Claude Code compatible workflows
- Block character rendering is terminal-dependent, not agent-dependent

### Full Block Rendering
The gap between block characters is a font/CSS/browser issue, not glyphcss-specific.
Solutions ranked by effort:
1. **Braille palette** — trivial, built-in, highest resolution
2. **CSS text-shadow** — trivial, works everywhere
3. **Canvas fillRect** — perfect, needs render override (Ghostty approach)
4. **Custom font** — perfect, high maintenance

### Integration
- glyphcss → browser `<pre>` → copy/paste to terminal
- glyphcss → ANSI converter for terminal output
- Both solve "visual content as text" from different angles
