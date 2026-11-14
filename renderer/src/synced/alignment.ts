// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import alignmentJson from '../generated/chorus-alignment.json';

export type AlignedWord = {
  readonly text: string;
  readonly start_frame: number;
  readonly end_frame: number;
  readonly char_start: number;
  readonly char_end: number;
};

export type AlignedCue = {
  readonly id: string;
  readonly text: string;
  readonly start_frame: number;
  readonly end_frame: number;
  readonly words: readonly AlignedWord[];
  readonly accent_beat_frames: readonly number[];
};

export type ChorusOccurrence = {
  readonly id: string;
  readonly song_start_frame: number;
  readonly song_end_frame: number;
  readonly cues: readonly AlignedCue[];
};

export type ChorusAlignment = {
  readonly status: string;
  readonly review_status: string;
  readonly song_asset: string | null;
  readonly fps: number;
  readonly occurrences: readonly ChorusOccurrence[];
};

/** This is also the coordinate system used by word char_start / char_end. */
export const normalizeCueText = (text: string): string =>
  text.normalize('NFC').replace(/[^\uac00-\ud7a3A-Za-z0-9]/g, '');

const fail = (message: string): never => {
  throw new Error(`SyncedChorus: generated/chorus-alignment.json ${message}`);
};

const record = (value: unknown, path: string): Record<string, unknown> => {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) {
    return fail(`${path} must be an object.`);
  }
  return value as Record<string, unknown>;
};

const array = (value: unknown, path: string): readonly unknown[] => {
  if (!Array.isArray(value)) return fail(`${path} must be an array.`);
  return value;
};

const text = (value: unknown, path: string): string => {
  if (typeof value !== 'string' || !value.trim()) return fail(`${path} is missing text.`);
  return value;
};

const frame = (value: unknown, path: string): number => {
  if (typeof value !== 'number' || !Number.isSafeInteger(value) || value < 0) {
    return fail(`${path} must be a non-negative integer at original-song 30fps.`);
  }
  return value;
};

const parseWord = (value: unknown, path: string): AlignedWord => {
  const word = record(value, path);
  const result = {
    text: text(word.text, `${path}.text`),
    start_frame: frame(word.start_frame, `${path}.start_frame`),
    end_frame: frame(word.end_frame, `${path}.end_frame`),
    char_start: frame(word.char_start, `${path}.char_start`),
    char_end: frame(word.char_end, `${path}.char_end`),
  };
  if (result.end_frame <= result.start_frame || result.char_end <= result.char_start) {
    return fail(`${path} must have positive time and character ranges.`);
  }
  return result;
};

const checkWords = (cue: AlignedCue, path: string): void => {
  const normalized = normalizeCueText(cue.text);
  if (!cue.words.length) fail(`${path}.words is empty; no guessed word timing is available.`);
  cue.words.forEach((word, index) => {
    const previous = cue.words[index - 1];
    if (word.start_frame < cue.start_frame || word.end_frame > cue.end_frame ||
      (previous && word.start_frame < previous.start_frame)) {
      fail(`${path}.words[${index}] is outside its cue or out of chronological order.`);
    }
    if (word.char_start !== (previous?.char_end ?? 0) ||
      normalizeCueText(word.text) !== normalized.slice(word.char_start, word.char_end)) {
      fail(`${path}.words[${index}] does not match normalized full-cue character offsets.`);
    }
  });
  if (cue.words[cue.words.length - 1].char_end !== normalized.length) {
    fail(`${path}.words must cover every normalized character of the full cue.`);
  }
};

const parseCue = (value: unknown, path: string): AlignedCue => {
  const source = record(value, path);
  const cue: AlignedCue = {
    id: text(source.id, `${path}.id`),
    text: text(source.text, `${path}.text`),
    start_frame: frame(source.start_frame, `${path}.start_frame`),
    end_frame: frame(source.end_frame, `${path}.end_frame`),
    words: array(source.words, `${path}.words`).map((word, wordIndex) =>
      parseWord(word, `${path}.words[${wordIndex}]`)),
    accent_beat_frames: array(source.accent_beat_frames, `${path}.accent_beat_frames`)
      .map((beat, beatIndex) => frame(beat, `${path}.accent_beat_frames[${beatIndex}]`)),
  };
  if (cue.end_frame <= cue.start_frame || cue.accent_beat_frames.some((beat) =>
    beat < cue.start_frame || beat >= cue.end_frame)) {
    return fail(`${path} has an invalid cue range or a strong beat outside that range.`);
  }
  checkWords(cue, path);
  return cue;
};

const parseOccurrence = (value: unknown, index: number): ChorusOccurrence => {
  const path = `occurrences[${index}]`;
  const source = record(value, path);
  const cues = array(source.full_cues ?? source.cues, `${path}.cues`);
  if (!cues.length) return fail(`${path} requires word-aligned phrases.`);
  const occurrence: ChorusOccurrence = {
    id: text(source.id, `${path}.id`),
    song_start_frame: frame(source.song_start_frame, `${path}.song_start_frame`),
    song_end_frame: frame(source.full_end_frame ?? source.song_end_frame, `${path}.song_end_frame`),
    cues: cues.map((cue, cueIndex) => parseCue(cue, `${path}.cues[${cueIndex}]`)),
  };
  if (occurrence.song_end_frame <= occurrence.song_start_frame) {
    return fail(`${path} has an invalid original-song range.`);
  }
  occurrence.cues.forEach((cue, cueIndex) => {
    const previous = occurrence.cues[cueIndex - 1];
    if (cue.start_frame < occurrence.song_start_frame ||
      cue.end_frame > occurrence.song_end_frame ||
      (previous && cue.start_frame < previous.end_frame)) {
      fail(`${path}.cues[${cueIndex}] overlaps the previous phrase or leaves the song range.`);
    }
  });
  return occurrence;
};

export const parseChorusAlignment = (value: unknown): ChorusAlignment => {
  const source = record(value, 'root');
  const occurrences = array(source.occurrences, 'occurrences');
  if (typeof source.status !== 'string' || typeof source.review_status !== 'string' ||
    !(source.song_asset === null || typeof source.song_asset === 'string') ||
    typeof source.fps !== 'number' || !Number.isInteger(source.fps) || source.fps <= 0) {
    return fail('requires status, review_status, a configurable song_asset and positive fps.');
  }
  return {
    status: source.status, review_status: source.review_status,
    song_asset: source.song_asset, fps: source.fps,
    occurrences: occurrences.map(parseOccurrence),
  };
};

/** Timing always comes from the supplied soundtrack alignment. */
export const getSyncedChorusTiming = (occurrenceIndex = 0) => {
  const alignment = parseChorusAlignment(alignmentJson);
  if (!Number.isSafeInteger(occurrenceIndex) || occurrenceIndex < 0 ||
    occurrenceIndex >= alignment.occurrences.length) {
    return fail(`occurrenceIndex ${occurrenceIndex} is unavailable.`);
  }
  const occurrence = alignment.occurrences[occurrenceIndex];
  const startFrame = Math.max(0, occurrence.cues[0].start_frame - 12);
  const endFrame = occurrence.cues[occurrence.cues.length - 1].end_frame + 18;
  return {alignment, occurrence, startFrame, endFrame, durationInFrames: endFrame - startFrame};
};
