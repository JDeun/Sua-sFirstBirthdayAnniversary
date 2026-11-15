// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
/** Original paths; frame-driven SVG, with no vendor animation code or runtime. */
export type StoryDoodleKind = 'arc' | 'constellation' | 'orbit';
export type DoodleRect = Readonly<{x: number; y: number; width: number; height: number}>;
type Placement = Readonly<{bounds: DoodleRect; vertical: boolean; scale: number}>;
type Node = Readonly<{x: number; y: number; at: number}>;
type Drawing = Readonly<{main: string; followers: readonly [string, string]; nodes: readonly Node[]}>;

export const STORY_DOODLE_FPS = 30;
const W = 480, H = 280, SAFE = 64, CLEARANCE = 32;
const clamp = (value: number): number => Math.max(0, Math.min(1, value));
const progress = (frame: number, start: number, seconds: number): number =>
  clamp((frame - start * STORY_DOODLE_FPS) / (seconds * STORY_DOODLE_FPS));
const easeInOut = (value: number): number => value < 0.5 ? 8 * value ** 4 : 1 - (-2 * value + 2) ** 4 / 2;

/** Unrounded card timings, all sampled on the same 30 fps source clock. Hold after f102. */
export const storyDoodleState = (frame: number) => ({
  main: progress(frame, 0.3, 1.85),
  followers: [progress(frame, 0.37, 1.91), progress(frame, 0.44, 1.97)] as const,
  settle: [0, 1, 2].map((part) => easeInOut(progress(frame, 0.25 + part * 0.07, 1.1 + part * 0.06))),
  highlight: progress(frame, 2.47, 0.9),
  highlightOpacity: frame > 2.47 * STORY_DOODLE_FPS && frame < 3.37 * STORY_DOODLE_FPS ? 1 : 0,
  complete: frame >= 3.37 * STORY_DOODLE_FPS,
});

const DRAWINGS: Readonly<Record<StoryDoodleKind, Drawing>> = {
  arc: {
    main: 'M32 222 C48 112 164 37 292 58 C367 70 418 105 446 155',
    followers: ['M43 241 C70 137 171 68 274 79', 'M328 51 Q409 54 455 119'],
    nodes: [{x: 32, y: 222, at: 0}, {x: 446, y: 155, at: 0.98}],
  },
  constellation: {
    main: 'M34 210 Q87 173 134 142 L214 177 L316 64 L438 104',
    followers: ['M38 231 Q130 247 219 222', 'M329 43 Q397 34 449 77'],
    nodes: [{x: 34, y: 210, at: 0}, {x: 134, y: 142, at: 0.24},
      {x: 214, y: 177, at: 0.42}, {x: 316, y: 64, at: 0.72}, {x: 438, y: 104, at: 0.98}],
  },
  orbit: {
    main: 'M38 187 C70 101 255 43 393 62 C465 76 459 134 390 182 C294 249 96 263 42 211 C26 194 33 164 59 143',
    followers: ['M71 220 C175 254 327 210 416 145', 'M168 64 Q287 23 389 45'],
    nodes: [{x: 38, y: 187, at: 0}, {x: 390, y: 182, at: 0.53}, {x: 59, y: 143, at: 0.98}],
  },
};

const expanded = (rect: DoodleRect, pad: number): DoodleRect => ({
  x: rect.x - pad, y: rect.y - pad, width: rect.width + pad * 2, height: rect.height + pad * 2,
});

/** Partition free paper around an obstacle; these rectangles never cross the image or words. */
const subtract = (space: DoodleRect, obstacle: DoodleRect): readonly DoodleRect[] => {
  const left = Math.max(space.x, obstacle.x), top = Math.max(space.y, obstacle.y);
  const right = Math.min(space.x + space.width, obstacle.x + obstacle.width);
  const bottom = Math.min(space.y + space.height, obstacle.y + obstacle.height);
  if (left >= right || top >= bottom) return [space];
  return [
    {x: space.x, y: space.y, width: left - space.x, height: space.height},
    {x: right, y: space.y, width: space.x + space.width - right, height: space.height},
    {x: left, y: space.y, width: right - left, height: top - space.y},
    {x: left, y: bottom, width: right - left, height: space.y + space.height - bottom},
  ].filter((rect) => rect.width > 0 && rect.height > 0);
};

/** Fit one readable drawing to a margin, or omit it instead of shrinking it into a busy speck. */
export const storyDoodlePlacement = (media: DoodleRect, words?: DoodleRect,
  reserveLyrics = false, preferRight = false): Placement | null => {
  const left = reserveLyrics ? 1020 : SAFE;
  const paper = {x: left, y: SAFE, width: 1920 - SAFE - left, height: 1080 - SAFE * 2};
  const obstacles = [expanded(media, CLEARANCE), ...(words ? [expanded(words, 24)] : [])];
  const spaces = obstacles.reduce<readonly DoodleRect[]>((free, obstacle) =>
    free.flatMap((space) => subtract(space, obstacle)), [paper]);
  const choices = spaces.flatMap((space) => [false, true].map((vertical) => {
    const width = vertical ? H : W, height = vertical ? W : H;
    const scale = Math.min(1, space.width / width, space.height / height);
    const right = space.x + space.width / 2 > 960;
    const x = right ? space.x + space.width - width * scale : space.x;
    return {bounds: {x, y: space.y, width: width * scale, height: height * scale},
      vertical, scale, score: scale + (right === preferRight ? 0.04 : 0)};
  }));
  const best = choices.reduce<(Placement & {score: number}) | null>((found, choice) =>
    !found || choice.score > found.score ? choice : found, null);
  return best && best.scale >= 0.4 ? best : null;
};

type StrokeProps = Readonly<{d: string; drawn: number; settle: number; width: number}>;
const DrawnStroke = ({d, drawn, settle, width}: StrokeProps) =>
  <path d={d} pathLength={1} strokeWidth={width} strokeDasharray="1 1"
    strokeDashoffset={1 - drawn} opacity={drawn > 0 ? 1 : 0}
    transform={`translate(${(1 - settle) * -12} ${(1 - settle) * 8})`} />;

const DoodleNodes = ({nodes, drawn}: Readonly<{nodes: readonly Node[]; drawn: number}>) =>
  <g strokeWidth={3}>
    {nodes.map((node, index) => <g key={index} transform={`translate(${node.x} ${node.y})`}
      opacity={clamp((drawn - node.at) / 0.02)}>
      {index === nodes.length - 1 ? <path d="M0 -10 Q2 -2 10 0 Q2 2 0 10 Q-2 2 -10 0 Q-2 -2 0 -10Z" /> :
        <circle r={index === 0 ? 5 : 7} />}
    </g>)}
  </g>;

export type StoryDoodlesProps = Readonly<{
  kind: StoryDoodleKind; frame: number; placement: Placement; color: string; highlightColor: string;
}>;

/** One connected figure and two following strokes; a single highlight passes, then all motion stops. */
export const StoryDoodles = ({kind, frame, placement, color, highlightColor}: StoryDoodlesProps) => {
  const state = storyDoodleState(frame), drawing = DRAWINGS[kind];
  const {bounds, vertical, scale} = placement;
  const orientation = vertical ? `translate(${H * scale} 0) rotate(90) scale(${scale})` : `scale(${scale})`;
  return <svg aria-hidden width={bounds.width} height={bounds.height}
    data-story-doodle={kind} data-doodle-complete={state.complete}
    style={{position: 'absolute', left: bounds.x, top: bounds.y, overflow: 'hidden', pointerEvents: 'none'}}>
    <g transform={orientation} fill="none" stroke={color} strokeLinecap="round" strokeLinejoin="round">
      <DrawnStroke d={drawing.main} drawn={state.main} settle={state.settle[0]} width={5} />
      <g opacity={0.48}>
        {drawing.followers.map((d, index) => <DrawnStroke key={index} d={d}
          drawn={state.followers[index]} settle={state.settle[index + 1]} width={3} />)}
      </g>
      <DoodleNodes nodes={drawing.nodes} drawn={state.main} />
      <path d={drawing.main} pathLength={1} stroke={highlightColor} strokeWidth={2.8}
        strokeDasharray="0.15 1" strokeDashoffset={0.15 - 1.15 * state.highlight}
        opacity={state.highlightOpacity} />
    </g>
  </svg>;
};
