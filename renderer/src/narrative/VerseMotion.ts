// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {NARRATIVE} from './edit';
import type {FrameLayout, Rect} from './FrameLayout';

export const clampVerse = (n: number, low = 0, high = 1): number => Math.max(low, Math.min(high, n));
export const verseEase = (age: number, span: number): number =>
  1 - (1 - clampVerse(age / Math.max(1, span))) ** 3;

const beats: readonly number[] = NARRATIVE.rhythm?.beat_frames ?? [];
const closingLine = NARRATIVE.outro_alignment?.lines.find((line) =>
  line.id === NARRATIVE.outro_alignment?.final_line_id);
export const VERSE_OUTRO_START = closingLine?.start_frame ?? NARRATIVE.main_duration_in_frames;
export const VERSE_FINAL_WORD = closingLine?.words.at(-1)?.start_frame ?? NARRATIVE.main_duration_in_frames;

/** Keep measured beat metadata for callers; verse visuals no longer pulse or sweep per beat. */
export const verseBeat = (songFrame: number) => {
  let low = 0, high = beats.length;
  while (low < high) {
    const mid = Math.floor((low + high) / 2);
    if (beats[mid] <= songFrame) low = mid + 1;
    else high = mid;
  }
  const index = low - 1;
  const age = index < 0 ? 1000 : songFrame - beats[index];
  return {index, age, pulse: 0, sweep: 0};
};

export const verseQuiet = (songFrame: number, closing: boolean): number => !closing ? 1 :
  (0.78 - 0.58 * verseEase(songFrame - VERSE_OUTRO_START + 18, 18)) *
    (1 - verseEase(songFrame - VERSE_FINAL_WORD, 18));

/** Ease velocity to zero after the final word, then hold the exact same pose. */
const closingClock = (songFrame: number): number => songFrame <= VERSE_FINAL_WORD ? songFrame :
  VERSE_FINAL_WORD + 4.5 * (1 - (1 - clampVerse((songFrame - VERSE_FINAL_WORD) / 18)) ** 4);

export const verseShotFrame = (frame: number, songFrame: number, closing = false): number =>
  Math.max(0, closing ? closingClock(songFrame) - closingClock(songFrame - frame) : frame);

/** One bounded trajectory per shot, independent of the beat grid. */
export const verseShotProgress = (frame: number, duration: number, songFrame: number,
  closing = false): number => {
  const progress = clampVerse(verseShotFrame(frame, songFrame, closing) / Math.max(1, duration - 1));
  return progress * progress * (3 - 2 * progress);
};

export type MediaMotion = Readonly<{x: number; y: number; scale: number; bounds: Rect}>;

/** Move the complete aperture/mat together. Source pixels, aspect and crop never animate. */
export const verseMediaMotion = (layout: FrameLayout, frame: number, duration: number,
  songFrame: number, photo: boolean, closing = false): MediaMotion => {
  const m = layout.media;
  const left = m.x - (closing ? 1036 : 0), right = 1920 - m.x - m.width;
  const top = m.y, bottom = 1080 - m.y - m.height;
  const progress = verseShotProgress(frame, duration, songFrame, closing);
  const restraint = closing ? 0.2 : 1;
  const room = Math.max(0, Math.min(left, right) * 2 / m.width);
  const verticalRoom = Math.max(0, Math.min(top, bottom) * 2 / m.height);
  const growth = Math.min(0.012, room, verticalRoom) * (photo ? 1 : 0.35) * restraint;
  const endPadX = m.width * growth / 2, endPadY = m.height * growth / 2;
  const directionX = m.x + m.width / 2 < 960 ? 1 : -1;
  const directionY = m.y + m.height / 2 < 540 ? 1 : -1;
  // Both endpoint rectangles fit; their interpolation stays inside the same bounds.
  const endX = clampVerse(directionX * (photo ? 8 : 3) * restraint,
    Math.max(-12, -left + endPadX), Math.min(12, right - endPadX));
  const endY = clampVerse(directionY * (photo ? 6 : 2) * restraint,
    Math.max(-12, -top + endPadY), Math.min(12, bottom - endPadY));
  const scale = 1 + growth * progress;
  const padX = m.width * (scale - 1) / 2, padY = m.height * (scale - 1) / 2;
  const x = endX * progress, y = endY * progress;
  return {x, y, scale, bounds: {x: m.x + x - padX, y: m.y + y - padY,
    width: m.width * scale, height: m.height * scale}};
};

/** One restrained caption entrance, then a fixed, fully drawn pose. */
export const verseWordMotion = (_text: string, songFrame: number, start: number, end: number) => {
  const age = songFrame - start;
  const span = Math.max(1, end - start);
  const y = (1 - verseEase(age, Math.min(20, span * 0.3))) * 8;
  return {scale: 1, rotation: 0, x: 0, y, fill: 1, underline: 1, contextY: y};
};
