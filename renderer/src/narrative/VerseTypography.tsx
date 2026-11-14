// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {copyText} from '../copy';
import {FILM} from '../theme';
import {textEm} from './EditorialTypography';
import type {FrameLayout} from './FrameLayout';
import {verseWordMotion} from './VerseMotion';

const KEYWORDS = [copyText('narrative.VerseTypography.020'), copyText('narrative.VerseTypography.021'), copyText('narrative.VerseTypography.022'), copyText('narrative.VerseTypography.023'), copyText('narrative.VerseTypography.024'), copyText('narrative.VerseTypography.025'), copyText('narrative.VerseTypography.026'), copyText('narrative.VerseTypography.027'), copyText('narrative.VerseTypography.028'), copyText('narrative.VerseTypography.029'), copyText('narrative.VerseTypography.030')].filter(Boolean);
export type VerseRun = Readonly<{text: string; size: number; weight: 600 | 800;
  x: number; y: number; width: number; height: number; emphasis: boolean}>;
export type VerseTypeset = Readonly<{runs: readonly VerseRun[]; width: number; height: number}>;

const splitCopy = (text: string) => {
  const clean = text.replace(/\s+/g, ' ').trim();
  const main = KEYWORDS.find((word) => clean.includes(word)) ?? clean;
  const at = clean.indexOf(main);
  return {main, before: clean.slice(0, at).trimEnd(), after: clean.slice(at + main.length).trimStart()};
};

const run = (text: string, size: number, x: number, y: number, emphasis: boolean): VerseRun =>
  ({text, size, x, y, emphasis, weight: emphasis ? 800 : 600,
    width: textEm(text) * size, height: size * 1.14});

/** Explicit text advances make the maximum punch/rotation envelope provable without Chrome. */
export const verseTypeset = (text: string, layout: FrameLayout, date = ''): VerseTypeset => {
  const {main, before, after} = splitCopy(text);
  const pattern = copyText('narrative.VerseTypography.031');
  const modular = Boolean(pattern) && new RegExp(pattern).test(main);
  const line = layout.captionFlow === 'line' || layout.family === 'cinema';
  const space = layout.words.width - 28;
  const headroom = layout.words.height - (date ? 64 : 0);
  const nominal = modular ? 176 : layout.typeSize;
  const emphasisEm = modular ? textEm(main.slice(0, -1)) + 0.36 : textEm(main);
  const contextEm = textEm(before + after);
  const size = Math.min(nominal, space / (1.17 * (emphasisEm + (line ? contextEm * 0.43 + 0.12 : 0))),
    headroom / (line || !before && !after ? 1.42 : 2.05));
  const contextSize = Math.min(60, size * 0.43);
  const context = before + (before && after ? ' ' : '') + after;
  const mainY = !line && context ? contextSize * 1.42 : 0;
  const contextWidth = textEm(context) * contextSize;
  const mainX = line && before ? textEm(before) * contextSize + size * 0.16 : 0;
  const lead = modular ? main.slice(0, -1) : main;
  const headline = run(lead, size, mainX, mainY, true);
  const suffix = modular ? [run(copyText('narrative.VerseTypography.032'), size * 0.34, headline.width + 12, size * 0.36, false)] : [];
  const contextRuns = !context ? [] : line ? [
    ...(before ? [run(before, contextSize, 0, size * 0.34, false)] : []),
    ...(after ? [run(after, contextSize, mainX + headline.width + 12, size * 0.34, false)] : []),
  ] : [run(context, contextSize, 0, 0, false)];
  const raw = [...contextRuns, headline, ...suffix];
  const width = Math.max(contextWidth, ...raw.map((item) => item.x + item.width));
  const height = Math.max(...raw.map((item) => item.y + item.height));
  const align = layout.align === 'center' ? (layout.words.width - width) / 2 :
    layout.align === 'right' ? layout.words.width - width - 14 : 14;
  return {runs: raw.map((item) => ({...item, x: item.x + align})), width: layout.words.width, height};
};

export const verseAccent = (layout: FrameLayout): string => layout.shade === 'blue' ? FILM.colors.blueInk :
  layout.shade === 'peach' || layout.shade === 'rose' ? FILM.colors.peachInk : FILM.colors.lavenderInk;

const VerseGlyph = ({item, motion, accent, id}: Readonly<{
  item: VerseRun; motion: ReturnType<typeof verseWordMotion>; accent: string; id: string;
}>) => {
  const {x, y, width, size, height, emphasis} = item;
  const transform = emphasis ? `translate(${motion.x} ${motion.y}) translate(${x + width / 2} ${y + height / 2})
    rotate(${motion.rotation}) scale(${motion.scale}) translate(${-x - width / 2} ${-y - height / 2})` :
    `translate(0 ${motion.contextY})`;
  const glyph = {x, y: y + size * 0.94, fontSize: size, fontWeight: item.weight,
    textLength: width, lengthAdjust: 'spacingAndGlyphs' as const};
  return <g transform={transform} data-verse-run={item.text} data-emphasis={emphasis}>
    {emphasis ? <>
      <defs><clipPath id={id}><rect x={x - 4} y={y - 4}
        width={(width + 8) * motion.fill} height={height + 12} /></clipPath></defs>
      <text {...glyph} fill="none" stroke={accent} strokeWidth={1.7} strokeLinejoin="round">{item.text}</text>
      <text {...glyph} fill={accent} clipPath={`url(#${id})`}>{item.text}</text>
      <path d={`M${x} ${y + size * 1.08} Q${x + width * 0.5} ${y + size * 1.14} ${x + width} ${y + size * 1.07}`}
        fill="none" stroke={accent} strokeWidth={Math.max(3, size * 0.032)} strokeLinecap="round"
        opacity={0.65} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - motion.underline} />
    </> : <text {...glyph} fill={FILM.colors.ink}>{item.text}</text>}
  </g>;
};

/** All lettering is already present at cue onset; only its internal fill/draw/pose changes. */
export const VerseTypography = ({text, layout, songFrame, start, end, date = ''}: Readonly<{
  text: string; layout: FrameLayout; songFrame: number; start: number; end: number; date?: string;
}>) => {
  const type = verseTypeset(text, layout, date);
  const motion = verseWordMotion(text, songFrame, start, end);
  return <>
    <svg width={type.width} height={type.height} viewBox={`0 0 ${type.width} ${type.height}`}
      role="img" aria-label={text} style={{overflow: 'visible', display: 'block', fontFamily: FILM.font}}>
      {type.runs.map((item, index) => <VerseGlyph key={`${index}-${item.text}`} item={item}
        motion={motion} accent={verseAccent(layout)} id={`verse-${start}-${index}`} />)}
    </svg>
    {date ? <div data-verse-date={date} style={{fontFamily: FILM.font, fontSize: 26,
      fontWeight: 600, color: FILM.colors.muted, letterSpacing: 0.8,
      marginTop: 26, paddingLeft: 14, lineHeight: 1.3}}>{date}</div> : null}
  </>;
};
