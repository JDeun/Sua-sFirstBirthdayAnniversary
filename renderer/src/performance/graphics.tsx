// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {FILM} from '../theme';

const clamp = (value: number, low: number, high: number) =>
  Math.max(low, Math.min(high, value));
const reveal = (frame: number, start: number, end: number) =>
  clamp((frame - start) / (end - start), 0, 1);
const easeOut = (value: number) => 1 - Math.pow(1 - value, 3);

const starPoints = (inner: number) => Array.from({length: 10}, (_, index) => {
  const angle = -Math.PI / 2 + index * Math.PI / 5;
  const radius = index % 2 === 0 ? 46 : inner;
  return `${50 + Math.cos(angle) * radius},${50 + Math.sin(angle) * radius}`;
}).join(' ');

export type StarBloomProps = {
  /** Local clock: zero is the vocal onset of the star word. Render before the cutout. */
  readonly frame: number;
  /** Center of the star in 1920x1080 composition pixels. */
  readonly x: number;
  readonly y: number;
  readonly size: number;
  readonly color?: string;
};

/** A single five-point star unfurls; the parent's subject stays untransformed. */
export const StarBloom = ({frame, x, y, size, color = FILM.colors.lavender}: StarBloomProps) => {
  if (frame < 0) return null;
  const open = easeOut(reveal(frame, 0, 8));
  const scale = 0.28 + open * 0.72 + Math.sin(reveal(frame, 0, 12) * Math.PI) * 0.08;
  const edge = clamp(size, 1, 1000);
  return <svg aria-hidden width={edge} height={edge} viewBox="0 0 100 100"
    style={{position: 'absolute', left: x - edge / 2, top: y - edge / 2,
      pointerEvents: 'none', overflow: 'visible', transformOrigin: '50% 50%',
      transform: `rotate(${-28 * (1 - open)}deg) scale(${scale})`}}>
    <polygon points={starPoints(8 + open * 13)} fill={color}
      stroke={FILM.colors.cream} strokeWidth={0.8} strokeLinejoin="round" />
  </svg>;
};

const TRAIL = [
  {x: 166, y: 942, size: 72, delay: 0, turn: -16, color: FILM.colors.lavender},
  {x: 346, y: 1000, size: 44, delay: 2, turn: 9, color: FILM.colors.cream},
  {x: 1512, y: 982, size: 56, delay: 3, turn: -8, color: FILM.colors.blue},
  {x: 1750, y: 922, size: 88, delay: 1, turn: 14, color: FILM.colors.lavender},
] as const;

/** Optional, sparse bottom-margin accompaniment; no stars cross face height. */
export const StarTrail = ({frame}: {readonly frame: number}) => {
  if (frame < 0) return null;
  return <svg aria-hidden width={1920} height={1080} viewBox="0 0 1920 1080"
    style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>
    {TRAIL.map((star, index) => {
      const open = easeOut(reveal(frame, star.delay, star.delay + 6));
      const scale = star.size / 100 * open;
      return <g key={index} opacity={open * 0.85}
        transform={`translate(${star.x} ${star.y + (1 - open) * 30}) rotate(${star.turn * open}) scale(${scale})`}>
        <polygon points={starPoints(21)} transform="translate(-50 -50)" fill={star.color} />
      </g>;
    })}
  </svg>;
};

export type DrawnCrownProps = {
  /** Zero at the princess word's vocal onset; parent may retime this clock to the beat. */
  readonly frame: number;
  /** Top-left of the unrotated crown canvas, in composition pixels. */
  readonly x: number;
  readonly y: number;
  readonly width: number;
  /** Degrees, rotating around the bottom center so it sits on the head. */
  readonly rotation?: number;
};

const CROWN_STROKES = [
  {d: 'M27 68 Q25 53 18 17 Q35 27 54 42', start: 0, end: 3},
  {d: 'M54 42 Q67 25 81 6 Q94 24 108 40', start: 1.5, end: 5},
  {d: 'M108 40 Q127 28 143 16 Q138 44 134 66', start: 3, end: 6.5},
  {d: 'M27 68 Q78 74 134 66 M30 77 Q81 83 131 75', start: 5, end: 8},
] as const;

/** Four hand-drawn strokes, three peaks, one lavender jewel; complete at f8. */
export const DrawnCrown = ({frame, x, y, width, rotation = 0}: DrawnCrownProps) => {
  if (frame < 0 || width <= 0) return null;
  return <svg aria-hidden width={width} height={width * 0.55} viewBox="0 0 160 88"
    style={{position: 'absolute', left: x, top: y, overflow: 'visible',
      pointerEvents: 'none', transformOrigin: '50% 100%', transform: `rotate(${rotation}deg)`}}
    fill="none" strokeLinecap="round" strokeLinejoin="round">
    {CROWN_STROKES.map((stroke, index) => {
      const drawn = reveal(frame, stroke.start, stroke.end);
      return <path key={index} d={stroke.d} pathLength={1}
        stroke={FILM.colors.lavenderInk}
        strokeWidth={index === 3 ? 3 : 4} strokeDasharray="1 1"
        strokeDashoffset={1 - drawn} opacity={drawn > 0 ? 1 : 0} />;
    })}
    <path d="M80 49 L86 55 L80 61 L74 55 Z" pathLength={1}
      stroke={FILM.colors.lavenderInk} strokeWidth={2.8} strokeDasharray="1 1"
      strokeDashoffset={1 - reveal(frame, 6, 8)} opacity={frame > 6 ? 1 : 0} />
  </svg>;
};
