// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {normalizeCueText, type AlignedCue} from '../synced/alignment';

/** Read the vocal clock, including pickups; never snap a sung word to a beat. */
export const wordEvent = (cue: Pick<AlignedCue, 'text' | 'words'>, fragment: string) => {
  const full = normalizeCueText(cue.text);
  const needle = normalizeCueText(fragment);
  const position = full.indexOf(needle);
  if (position < 0) throw new Error(`Missing sung fragment: ${fragment}`);
  const words = cue.words.filter((word) => word.char_start < position + needle.length &&
    word.char_end > position);
  if (!words.length) throw new Error(`Missing vocal timing: ${fragment}`);
  return {start: words[0].start_frame, end: words[words.length - 1].end_frame};
};

export const eventClock = (cue: Pick<AlignedCue, 'text' | 'words'>, text: string, songFrame: number) =>
  songFrame - wordEvent(cue, text).start;
