// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {copyText} from '../copy';
import type {CSSProperties} from 'react';
import {FILM} from '../theme';

const W = 1920;
const H = 1080;
const SAFE = 24;
const clamp = (value: number, low: number, high: number) =>
  Math.max(low, Math.min(high, value));
const progress = (frame: number, end: number) =>
  end <= 0 ? 1 : 1 - Math.pow(1 - clamp(frame / end, 0, 1), 3);
const settleTime = (duration: number, maximum: number) =>
  Math.min(maximum, Math.max(0, Math.ceil(duration) - 1), Math.max(2, duration * 0.35));
const active = (frame: number, duration: number) => frame >= 0 && frame < duration;
const stage: CSSProperties = {position: 'absolute', left: 0, top: 0,
  width: W, height: H, overflow: 'hidden', pointerEvents: 'none'};

type Run = {readonly text: string; readonly size: number; readonly baseline?: number};

/** Explicit SVG advances keep both Hangul and fallback fonts inside the box. */
const advance = (text: string, size: number) => {
  const glyphs = Array.from(text);
  const ems = glyphs.reduce((total, glyph) => total + (/\s/.test(glyph) ? 0.34
    : /[.,!?;:'’]/u.test(glyph) ? 0.26
    : /[\u1100-\u11ff\u2e80-\ua4cf\uac00-\ud7af\uf900-\ufaff]/u.test(glyph) ? 1 : 0.68), 0);
  return Math.max(size * 0.2, size * (ems - Math.max(0, glyphs.length - 1) * 0.045));
};

const typeset = (runs: readonly Run[]) => {
  const size = Math.max(1, ...runs.map((run) => run.size));
  const gap = size * 0.035;
  const widths = runs.map((run) => advance(run.text, run.size));
  const placed = runs.map((run, index) => ({...run, width: widths[index],
    x: size * 0.16 + widths.slice(0, index).reduce((sum, width) => sum + width + gap, 0)}));
  return {runs: placed, size, width: widths.reduce((sum, width) => sum + width, 0)
    + Math.max(0, runs.length - 1) * gap + size * 0.32, height: size * 1.34};
};

type Typeset = ReturnType<typeof typeset>;

/** Maximum |cos| over the whole rotation interval, including interior extrema. */
const peakCos = (from: number, to: number, phase: number) => {
  const low = (Math.min(from, to) - phase) * Math.PI / 180;
  const high = (Math.max(from, to) - phase) * Math.PI / 180;
  return Math.ceil(low / Math.PI) <= Math.floor(high / Math.PI) ? 1
    : Math.max(Math.abs(Math.cos(low)), Math.abs(Math.cos(high)));
};

/** Reserve the complete 1.2x punch/rotation envelope, then clamp final x/y. */
const fit = (type: Typeset, x: number, y: number, tilt: number, width?: number) => {
  const cos = peakCos(tilt - 8, tilt, 0);
  const sin = peakCos(tilt - 8, tilt, 90);
  const boundW = 1.2 * (type.width * cos + type.height * sin);
  const boundH = 1.2 * (type.width * sin + type.height * cos);
  const ratio = Math.min(1, Math.max(1, width ?? type.width) / type.width,
    (W - SAFE * 2) / boundW, (H - SAFE * 2) / boundH);
  const w = type.width * ratio;
  const h = type.height * ratio;
  const padX = Math.max(0, (boundW * ratio - w) / 2);
  const padY = Math.max(0, (boundH * ratio - h) / 2);
  return {width: w, height: h, ratio,
    left: clamp(x, SAFE + padX, W - SAFE - w - padX),
    top: clamp(y, SAFE + padY, H - SAFE - h - padY)};
};

type UnifiedProps = {
  readonly type: Typeset;
  readonly frame: number;
  readonly duration: number;
  readonly x: number;
  readonly y: number;
  readonly width?: number;
  readonly color: string;
  readonly tilt: number;
  readonly outline?: boolean;
  readonly pickup?: boolean;
};

const GlyphSvg = ({type, color, outline}: Pick<UnifiedProps, 'type' | 'color' | 'outline'>) =>
  <svg width="100%" height="100%" viewBox={`0 0 ${type.width} ${type.height}`}
    style={{display: 'block'}} fill={outline ? 'none' : color} stroke={outline ? color : 'none'}
    strokeWidth={type.size * 0.007} strokeLinejoin="round">
    <text fontFamily={FILM.font} fontWeight={FILM.weight.lyric}>
      {type.runs.map((run, index) => <tspan key={index} x={run.x}
        y={run.baseline ?? type.size * 1.02} fontSize={run.size} textLength={run.width}
        lengthAdjust="spacingAndGlyphs">{run.text}</tspan>)}
    </text>
  </svg>;

/** One transform for the complete word; two masks stagger without a fade-in. */
const UnifiedType = ({type, frame, duration, x, y, width, color, tilt,
  outline = false, pickup = false}: UnifiedProps) => {
  const end = settleTime(duration, pickup ? 5 : 4);
  const remaining = 1 - progress(frame, end);
  const box = fit(type, x, y, tilt, width);
  return <div role="img" aria-label={type.runs.map((run) => run.text).join('')}
    style={{position: 'absolute', left: box.left, top: box.top,
      width: box.width, height: box.height, transformOrigin: '50% 50%',
      transform: `rotate(${tilt - remaining * 8}deg) scale(${1 + remaining * 0.2})`}}>
    {remaining === 0 ? <GlyphSvg {...{type, color, outline}} /> : [0, 1].map((half) => {
      const delay = end * half * 0.25;
      const split = 1 - progress(frame - delay, end - delay);
      const slide = split * type.size * box.ratio * (pickup ? 0.13 : 0.045);
      return <div key={half} aria-hidden style={{position: 'absolute', inset: 0,
        clipPath: half === 0 ? 'inset(0 0 50% 0)' : 'inset(50% 0 0 0)'}}>
        <div style={{width: '100%', height: '100%',
          transform: `translateX(${half === 0 ? -slide : slide}px)`}}>
          <GlyphSvg {...{type, color, outline}} />
        </div>
      </div>;
    })}
  </div>;
};

export type PickupCardProps = {
  readonly text: string;
  /** Local clock: zero is the actual pickup word's ASR onset. */
  readonly frame: number;
  readonly duration: number;
};

/** Text-only 1920x1080 cards: monumental left solo vs. broad right duet. */
export const PickupCard = ({text, frame, duration}: PickupCardProps) => {
  if (!active(frame, duration)) return null;
  const solo = text === copyText('performance.ChorusPerformance.033');
  return <div style={{...stage,
    backgroundColor: solo ? FILM.colors.cream : FILM.colors.blue}}>
    <UnifiedType type={typeset([{text, size: solo ? 650 : 510}])}
      frame={frame} duration={duration} x={solo ? 230 : 690} y={solo ? 150 : 210}
      color={solo ? FILM.colors.blueInk : FILM.colors.lavenderInk} tilt={0} pickup />
  </div>;
};

export type ImpactWordProps = {
  readonly text: string;
  readonly frame: number;
  readonly duration: number;
  /** Desired top-left of the settled SVG box; clamped for the entire punch. */
  readonly x: number;
  readonly y: number;
  readonly size: number;
  /** Maximum settled box width, preserving its aspect ratio. */
  readonly width?: number;
  readonly color?: string;
  readonly tilt?: number;
  readonly outline?: boolean;
};

/** Fully present on frame zero. Short cues settle by their last visible frame. */
export const ImpactWord = ({text, frame, duration, x, y, size, width,
  color = FILM.colors.cream, tilt = 0, outline = false}: ImpactWordProps) => {
  if (!active(frame, duration) || !text) return null;
  return <div style={stage}>
    <UnifiedType type={typeset([{text, size: Math.max(1, size)}])}
      {...{frame, duration, x, y, width, color, tilt, outline}} />
  </div>;
};

export type NounWithParticleProps = Omit<ImpactWordProps, 'text' | 'width' | 'outline'> & {
  readonly noun: string;
  readonly particle: string;
  readonly particleSize?: number;
};

/** Both runs share their ASR onset, baseline, split masks and bounded transform. */
export const NounWithParticle = ({noun, particle, frame, duration, x, y, size,
  particleSize = size * 0.32, color = FILM.colors.cream, tilt = 0}: NounWithParticleProps) => {
  if (!active(frame, duration) || !noun) return null;
  const runs = [{text: noun, size: Math.max(1, size)},
    ...(particle ? [{text: particle, size: clamp(particleSize, 1, Math.max(1, size * 0.55)),
      baseline: size * 0.78}] : [])];
  return <div style={stage}>
    <UnifiedType type={typeset(runs)} {...{frame, duration, x, y, color, tilt}} />
  </div>;
};
