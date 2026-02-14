# UI Redesign: Production Bible

## Direction
Transform from generic dashboard to typeset production document. A producer should look at this and feel like they're reading a meticulously assembled production bible — not a SaaS analytics dashboard.

## Layout
Single vertically scrolling document. No sidebar. No tabs. Sections flow top to bottom:

1. **Title Block** — centered, cover-page feel
2. **Executive Summary Strip** — single data row, thin rules
3. **Risk Timeline** — horizontal scene risk heatmap strip
4. **Scene Breakdowns** — full-width sheets, one per scene, flowing vertically
5. **Hidden Cost Radar** — block-quote callouts with severity
6. **Key Questions** — grouped by department
7. **Sticky mini-nav** — slim top bar with anchor links, not tabs

## Color
- Warm dark palette: `#0f0e0d` base, warm grays instead of cool blues
- Risk spectrum stays (5 stops, green→red)
- Strip all decorative color — color only carries meaning (risk, severity)
- VFX category pills: muted, desaturated versions

## Typography
- Serif headings (document authority)
- Monospaced scene numbers and data values
- Sans-serif body text
- Generous margins (page-gutter feel)

## Scene Cards → Breakdown Sheets
- Header bar: scene # | slugline | INT/EXT | DAY/NIGHT | pages | risk badges
- Two-column body: left (summary, characters, VFX, shots) / right (risks, capture, notes)
- Production flags as compact bottom row
- Thin rules between scenes (like page breaks)

## Interactions
- Smooth scroll to sections via nav links
- Scene hover: subtle lift, no color change
- Risk badges: color only element on scene headers
- Print-friendly (media query for clean printing)
