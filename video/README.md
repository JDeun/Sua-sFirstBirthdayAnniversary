# Remotion template previews

Three original, synthetic (no personal images) motion-graphic directions are available:

- `CinematicPreview` — 24s (cinematic editorial style)
- `ScrapbookPreview` — 24s (playful paper-photo collage)
- `VarietyPreview` — 24s (energetic TV-style typography)

Run:

~~~bash
npm install
npm run dev
npm run typecheck
npx remotion render src/index.ts CinematicPreview out/cinematic-demo.mp4
~~~

Composition source: `src/templates/TemplateShowcase.tsx`, palette tokens: `src/templates/presets.ts`.

These previews do **not** use family media or clone commercial templates. They also do **not** constitute the 4-minute finished video. The target editable story structure is described in [TEMPLATE_SPEC.md](../docs/TEMPLATE_SPEC.md).
