# glyphcss Research Dump

## What is glyphcss

ASCII polygon-mesh renderer for the DOM — projects 3D meshes into a monospace
character grid in a single `<pre>`. No WebGL, no canvas, no per-polygon DOM.

**Repo:** https://github.com/apresmoi/glyphcss
**Forked from:** polycss (https://github.com/LayoutitStudio/polycss)

## Core Architecture

- Rasterizer walks all polygons, fills a `cols × rows` character grid, writes
  a single string to `.textContent` per render
- No per-polygon DOM elements, no CSS `matrix3d`
- Single `<pre>` element output — one `textContent` assignment per frame

## Render Modes

| Mode | How cells are filled |
|------|---------------------|
| `wireframe` | Polygon edges rasterised as ASCII rules; glyph weight scales with edge prominence |
| `solid` | Filled polygons; glyph picked from the palette's solid ramp by Lambert-shaded intensity |
| `voxel` | Cube-aligned geometry; face normals drive glyph selection |

## Built-in Glyph Palettes

`default`, `ascii`, `dots`, `lines`, `blocks`, `stars`, `arrows`, `braille`,
`runes`, `math`, `binary`, `hex`

## Key Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `mode` | `"wireframe" \| "solid" \| "voxel"` | `"solid"` | Render mode |
| `glyphPalette` | `string` | `"default"` | Named glyph character set |
| `useColors` | `boolean` | `true` | Emit `<span>` color elements inside the `<pre>` |
| `cols` | `number` | `80` | Character grid width |
| `rows` | `number` | `24` | Character grid height |
| `cellAspect` | `number` | `2.0` | Cell height / width ratio |
| `smoothShading` | `boolean` | `false` | Gouraud shading |
| `autoSize` | `boolean` | `false` | Auto-measure host element via ResizeObserver |
| `shadow` | `GlyphShadowOptions` | `undefined` | Shadow mapping |

## Supported Formats

OBJ + MTL (with map_Kd textures), glTF, GLB, MagicaVoxel `.vox`, STL

## Packages

| Package | npm name | Description |
|---------|----------|-------------|
| `@glyphcss/core` | `@glyphcss/core` | Pure math: Vec3, Polygon, scene, camera, mesh ops, parsers. Zero browser globals. |
| `glyphcss` | `glyphcss` | ASCII rasteriser + vanilla custom elements + imperative `createGlyphScene` API. |
| `@glyphcss/react` | `@glyphcss/react` | React components, hooks, and controls. |
| `@glyphcss/vue` | `@glyphcss/vue` | Vue 3 mirror of the React package. |

## Render Pipeline

1. All mounted meshes walked in scene order
2. Polygon vertices transformed through camera matrix to 2D projected positions
3. `cols × rows` character grid filled: polygons depth-tested, each cell picks glyph
4. All cells joined and written to `.textContent` (or `.innerHTML` for color mode) **once**

## Performance (PR #10)

~40% faster heavy-mesh drag via:
- Cross-frame shading cache (Lambert intensities depend only on world normal + light)
- Hoisted backface cull (skip shading on ~half of faces culled)
- Projection dedup (project each unique vertex once)

Output verified **bit-identical** to recompute. 1321 tests pass.

## Fonts / WordArt (PR #13)

`@glyphcss/fonts` — ports `@layoutit/polycss-fonts` → fonts/text to extruded 3D `Polygon[]`.
Extrude any Google font to 3D ASCII in one `<pre>` — depth/profile/bevel, per-face
colors+textures, gradients, warps, presets.

## Per-Cell Texture Sampling (PR #13)

Solid rasterizer now samples polygon texture **per cell** (UV-mapped, glyph resolution)
and folds texel luminance into glyph + color into span — instead of baking each face
to one flat color.

## Shadows (PR #7)

- Opt-in `castShadow` / `receiveShadow` on meshes
- Implemented as shadow map (light-space depth pass + per-cell occlusion darkening)
- Self-shadow when both flags set

## Full Block Character Rendering Problem

**The core issue:** Unicode block characters (U+2580-U+259F) rendered via font
glyphs leave tiny gaps between cells because fonts don't perfectly fill the cell
height. This is a known problem across browsers and terminals.

### Solutions Found

1. **CSS text-shadow hack:**
   ```css
   .ascii-art {
     text-shadow: 1px 0px 0px rgba(0,0,0,1);
   }
   ```

2. **Letter-spacing squash (Chromium):**
   ```css
   .ascii-art {
     letter-spacing: -0.1em;
     line-height: 1.2em;
     transform: scale(1.2, 1) translateX(8%);
   }
   ```

3. **Background color matching:**
   ```css
   .ascii-art {
     background: black;
     color: black;
   }
   ```

4. **Canvas rect rendering (Ghostty approach):**
   Render block characters as `fillRect()` instead of font glyphs.
   This is what terminals like Kitty, GNOME VTE, and Konsole do.

5. **glyphcss approach:**
   Uses `innerHTML` with `<span>` color elements + Bayer ordered dithering.
   The `blocks` palette uses Unicode block elements. With `useColors: true`,
   each cell gets a `<span style="color:...">` wrapper.

## How to Make glyphcss Render Full Blocks

For gap-free block rendering in glyphcss:

### Option A: CSS Fix (simplest)
```css
pre.glyphcss-render {
  font-family: 'Courier New', monospace;
  line-height: 1;
  letter-spacing: 0;
  text-shadow: 0.5px 0 0 currentColor, 0 0.5px 0 currentColor;
}
```

### Option B: Canvas Override
Override the render output by intercepting the `<pre>` element and drawing
to a `<canvas>` instead, using `fillRect()` for block characters (like Ghostty).

### Option C: Braille Palette (highest resolution)
Use `glyphPalette="braille"` instead of `blocks` — Braille patterns encode
8 dots per character, giving 2× horizontal and 4× vertical resolution
within the same cell grid. No gap problem because Braille characters
naturally fill their cells.

### Option D: Custom Palette with Overlap
Define a custom glyph palette where block characters are slightly oversized
(in the font itself) to overlap adjacent cells. Requires a custom font.

## Relation to Terminals

The same gap problem exists in every terminal emulator:
- **Alacritty:** Issue #5485 — planned but not yet implemented
- **Kitty:** Solved with special rect rendering
- **GNOME VTE:** Solved with special rect rendering
- **Ghostty:** Solved with `renderBlockChar()` using `fillRect()`
- **Konsole:** Special treatment enabled by default

---

## CodeWhale / Whale Research Dump

## What is CodeWhale

Terminal-native coding agent for DeepSeek V4. MIT licensed.

**Repo:** https://github.com/Hmbown/CodeWhale (Rust, 130+ contributors)
**Also:** https://github.com/usewhale/Whale (Go, 668 stars)

## Key Properties

- ~98% prompt cache hit rate
- 1M context window
- DeepSeek V4 first-class (also OpenRouter, NVIDIA NIM, MiMo, Ollama, etc.)
- Dynamic Workflows (JS scripts orchestrating sub-agents)
- MCP tools integration
- Skills + plugins system
- Claude Code compatible workflows

## Interfaces

| Interface | When to use |
|-----------|-------------|
| `whale` (TUI) | Interactive coding sessions |
| `whale ask "..."` (CLI) | One-shot questions |
| `whale --headless` | CI/CD, automated tasks |

## Modes

| Mode | Behavior |
|------|----------|
| Plan | Read-only investigation |
| Agent | Default interactive, approval gates |
| YOLO | Auto-approve all tools |

## Architecture

```
codewhale (dispatcher CLI)
  → codewhale-tui (companion binary)
    → ratatui interface
      ↔ async engine
        ↔ OpenAI-compatible streaming client
```

Tool calls route through typed registry (shell, file ops, git, web, sub-agents, MCP, RLM).

## ASCII Art Rendering in Terminals

CodeWhale/Whale renders in terminal via ratatui. The block character gap problem
is terminal-dependent, not agent-dependent. Solutions:

1. Use a terminal that does special rect rendering (Kitty, Ghostty, GNOME VTE)
2. Use a font designed for terminal use (JetBrains Mono, Fira Code, etc.)
3. Set `line-height: 1` in terminal config
4. For browser output, use CSS hacks or canvas rect rendering

## glyph-arts (Related Project)

Terminal-visible chart toolkit — 29 chart types rendered directly in CLI.
Works with Claude Code, Codex, Gemini CLI.

**Repo:** https://github.com/2233admin/glyph-arts

Includes Claude Code terminal compatibility flags for statuslines, themes,
hyperlinks, and markdown rendering. Uses chafa + ffmpeg for image/video
chart types.

## Glyph (Another Related Project)

Deterministic SVG charts for AI agents. 53 MCP verbs, DuckDB inside.
Same JSON spec → same SVG bytes, every platform, every run.

**Repo:** https://github.com/seanhanca/glyph

## Integration Possibilities

### glyphcss + CodeWhale
- glyphcss renders 3D meshes as ASCII in browser `<pre>` elements
- CodeWhale runs in terminal via ratatui
- Connection: both solve "how to render visual content as text"
- Could use glyphcss output in CodeWhale's web preview or browser-based tools

### Making It Work
1. glyphcss output → copy as plain text → paste into terminal
2. glyphcss output → copy as rich HTML → paste into tools that support it
3. Build a glyphcss-to-ANSI converter for terminal rendering
4. Use glyphcss `image → glyph` example for agent visual understanding

## Key Insight

The "full glyphcss render" problem is about **gap-free block character rendering**.
The solution space:

1. **Font-level:** Use a font with perfect block metrics (hard to find)
2. **CSS-level:** text-shadow, letter-spacing, line-height hacks
3. **Canvas-level:** Render as rectangles instead of font glyphs (Ghostty approach)
4. **Palette-level:** Use braille (8 dots/cell) or custom palettes instead of blocks
5. **Architecture-level:** Accept the gaps and use color contrast to mask them
