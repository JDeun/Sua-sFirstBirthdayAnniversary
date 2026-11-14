// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {copyText} from '../copy';
import alignmentJson from '../generated/chorus-alignment.json';
import {getSyncedChorusTiming, normalizeCueText, type AlignedCue} from '../synced/alignment';

const EXPECTED = [
  ['star', copyText('performance.full-timing.045')], ['princess', copyText('performance.full-timing.046')],
  ['universe', copyText('performance.full-timing.047')], ['tremor', copyText('performance.full-timing.048')],
  ['shelter', copyText('performance.full-timing.049')],
  ['star-repeat', copyText('performance.full-timing.045')], ['princess-repeat', copyText('performance.full-timing.046')],
  ['gift', copyText('performance.full-timing.050')], ['love', copyText('performance.full-timing.051')],
  ['prayer', copyText('performance.full-timing.052')],
] as const;

export type PerformanceCue = Omit<AlignedCue, 'id'> & {readonly id: (typeof EXPECTED)[number][0]};
const validFrame = (value: unknown): value is number =>
  typeof value === 'number' && Number.isSafeInteger(value) && value >= 0;

const parseFullCue = (value: unknown, index: number): PerformanceCue => {
  const cue = value as PerformanceCue;
  const expected = EXPECTED[index];
  if (!cue || cue.id !== expected[0] || typeof cue.text !== 'string' ||
    normalizeCueText(cue.text) !== normalizeCueText(expected[1]) ||
    !validFrame(cue.start_frame) || !validFrame(cue.end_frame) ||
    cue.end_frame <= cue.start_frame || !Array.isArray(cue.words) || !cue.words.length) {
    throw new Error(`Complete chorus has an invalid ${expected[0]} phrase.`);
  }
  const normalized = normalizeCueText(cue.text);
  let offset = 0;
  let previousStart = cue.start_frame;
  for (const word of cue.words) {
    if (!word || !validFrame(word.start_frame) || !validFrame(word.end_frame) ||
      word.end_frame <= word.start_frame || word.start_frame < previousStart ||
      word.end_frame > cue.end_frame || word.char_start !== offset ||
      !validFrame(word.char_end) || word.char_end <= offset ||
      normalizeCueText(word.text) !== normalized.slice(offset, word.char_end)) {
      throw new Error(`Complete chorus word coverage/timing is invalid in ${expected[0]}.`);
    }
    offset = word.char_end;
    previousStart = word.start_frame;
  }
  if (offset !== normalized.length) throw new Error('Complete chorus omitted lyric characters.');
  return cue;
};

export const getPerformanceTiming = (occurrenceIndex = 0) => {
  const core = getSyncedChorusTiming(occurrenceIndex);
  const source = (alignmentJson as unknown as {occurrences: {
    full_cues?: unknown[]; full_lyric_lines?: string[];
  }[]}).occurrences[occurrenceIndex];
  if (!source?.full_cues || source.full_cues.length !== 10 || source.full_lyric_lines?.length !== 8) {
    throw new Error('ChorusPerformance requires all eight lyric lines, including the second half.');
  }
  const cues = source.full_cues.map(parseFullCue);
  if (cues.some((cue, index) => index > 0 && cue.start_frame < cues[index - 1].end_frame)) {
    throw new Error('Complete chorus phrases overlap.');
  }
  const startFrame = Math.max(0, cues[0].start_frame - 12);
  const endFrame = cues[cues.length - 1].end_frame + 18;
  return {...core, occurrence: {...core.occurrence, cues}, startFrame, endFrame,
    durationInFrames: endFrame - startFrame};
};


export type PerformanceProps = {readonly occurrenceIndex?: number};
