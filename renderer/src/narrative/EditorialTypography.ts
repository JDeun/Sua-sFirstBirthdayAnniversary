// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {interpolate} from 'remotion';
import {FILM} from '../theme';

export const EDITORIAL_FONT = {
  sans: FILM.font,
  serif: FILM.font,
} as const;

/** Only the lettering breathes in/out; a photograph or video is always present. */
export const cueOpacity = (frame: number, start: number, end: number): number => {
  if (frame < start || frame >= end) return 0;
  const span = Math.max(1, end - start);
  const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
  return interpolate(frame - start, [0, Math.min(8, span / 3)], [0, 1], clamp) *
    interpolate(end - frame, [0, Math.min(6, span / 3)], [0, 1], clamp);
};

/** Conservative em widths keep Korean short copy readable without measuring in a browser. */
export const textEm = (text: string): number => [...text].reduce((width, char) =>
  width + (/\s/.test(char) ? 0.32 : /[.,!?…·，]/.test(char) ? 0.4 : /[\x00-\x7F]/.test(char) ? 0.6 : 1), 0);

export const editorialLines = (text: string, width: number, nominal: number,
  singleLine = false): Readonly<{lines: readonly string[]; size: number}> => {
  const clean = text.replace(/\s+/g, ' ').trim();
  const supplied = text.split('\n').map((line) => line.trim()).filter(Boolean);
  const fits = (lines: readonly string[]) => Math.min(nominal,
    ...lines.map((line) => width / Math.max(1, textEm(line))));
  if (singleLine) return {lines: [clean], size: fits([clean])};
  if (supplied.length <= 2 && fits(supplied) >= Math.min(nominal, 60)) {
    return {lines: supplied, size: fits(supplied)};
  }
  const options = [...clean.matchAll(/\s/g)].map((match) =>
    [clean.slice(0, match.index), clean.slice(match.index! + 1)] as const);
  const best = options.reduce<readonly string[]>((current, lines) =>
    fits(lines) > fits(current) || (fits(lines) === fits(current) &&
      Math.abs(textEm(lines[0]) - textEm(lines[1])) <
      Math.abs(textEm(current[0]) - textEm(current[1] ?? ''))) ? lines : current, [clean]);
  return {lines: best, size: fits(best)};
};
