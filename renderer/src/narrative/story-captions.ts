// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {textEm} from './EditorialTypography';
import type {StoryNarrationCue} from './runtime-types';

const boxes = {
  bottom: {x: 128, y: 904, width: 1664, maxSize: 62, align: 'center'},
  left: {x: 128, y: 348, width: 770, maxSize: 78, align: 'left'},
  right: {x: 1032, y: 348, width: 760, maxSize: 78, align: 'left'},
} as const;

export const activeStoryCaption = (cues: readonly StoryNarrationCue[] | undefined, frame: number) =>
  cues?.find(cue => cue.start_frame <= frame && frame < cue.end_frame);

export const storyCaptionLayout = (cue: StoryNarrationCue) => {
  const box = boxes[cue.placement ?? 'bottom'], lines = cue.text.split('\n');
  const ems = Math.max(...lines.map(line => textEm(line)), 1);
  const size = Math.min(cue.size ?? box.maxSize, box.maxSize, (box.width - 80) / ems);
  const bottom = cue.placement === 'bottom' || !cue.placement;
  const width = bottom ? Math.min(box.width, Math.max(300, ems * size + 80)) : box.width;
  const height = lines.length * size * 1.42 + (cue.label ? 49 : 0) + (bottom ? 34 : 33);
  return {x: bottom ? (1920 - width) / 2 : box.x, y: bottom ? 1080 - 32 - height : box.y,
    width, height, size, bottom, align: box.align};
};

export const validateStoryCaptions = (cues: readonly StoryNarrationCue[] | undefined,
  duration: number, choruses: readonly Readonly<{start_frame: number; end_frame: number}>[],
  outroStart = duration) => {
  if (!cues) return;
  if (!Array.isArray(cues)) throw new Error('Story captions must be an array.');
  const ids = new Set<string>();
  let previous = 0;
  for (const cue of cues) {
    if (typeof cue.id !== 'string' || !cue.id.trim() || ids.has(cue.id) ||
      typeof cue.text !== 'string' || !cue.text.trim() || cue.text.split('\n').length > 2 ||
      cue.text.split('\n').some((line: string) => !line.trim())) {
      throw new Error('Story captions need unique ids and one or two nonempty lines.');
    }
    if (![cue.start_frame, cue.end_frame].every(Number.isSafeInteger) ||
      cue.start_frame < previous || cue.end_frame <= cue.start_frame || cue.end_frame > Math.min(duration, outroStart)) {
      throw new Error('Story captions must be ordered and stay before the synced outro.');
    }
    if (choruses.some(window => cue.start_frame < window.end_frame && cue.end_frame > window.start_frame)) {
      throw new Error('Story captions cannot cover a chorus.');
    }
    if (cue.placement !== undefined && !['bottom', 'left', 'right'].includes(cue.placement) ||
      cue.size !== undefined && (!Number.isFinite(cue.size) || cue.size <= 0) ||
      [cue.label, cue.date_label].some(value => value !== undefined && typeof value !== 'string')) {
      throw new Error('Invalid story caption placement or size.');
    }
    const bounds = storyCaptionLayout(cue);
    if (bounds.x < 0 || bounds.y < 0 || bounds.x + bounds.width > 1920 || bounds.y + bounds.height > 1080) {
      throw new Error('Story caption leaves the canvas.');
    }
    ids.add(cue.id);
    previous = cue.end_frame;
  }
};
