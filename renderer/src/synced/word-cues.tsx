// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {createContext, type CSSProperties} from 'react';
import {FILM} from '../theme';
import {normalizeCueText, type AlignedCue, type AlignedWord} from './alignment';

export type WordCueContextValue = {
  readonly cue: Omit<AlignedCue, 'id'> & {readonly id: string};
  /** Absolute original-song frame, independent of the scene's decorative clock. */
  readonly songFrame: number;
};

/** Each active performance scene supplies its original-song clock. */
export const WordCueContext = createContext<WordCueContextValue | null>(null);

/** A display fragment can contain multiple source words. */
const getWordFragments = (cue: WordCueContextValue['cue'], fragment: string) => {
  const fullText = normalizeCueText(cue.text);
  const normalized = normalizeCueText(fragment);
  const start = fullText.indexOf(normalized);
  if (!normalized || start < 0 || fullText.indexOf(normalized, start + 1) !== -1) {
    throw new Error(`SyncedChorus: lyric fragment "${fragment}" must match exactly once in "${cue.text}".`);
  }
  const characters = Array.from(fragment.normalize('NFC'));
  // Spaces and punctuation follow the preceding glyph's word; they never advance
  // the normalized offset or shift a later word's actual entrance.
  const positioned = characters.map((character, index) => ({
    character,
    offset: start + Math.max(0, normalizeCueText(characters.slice(0, index + 1).join('')).length - 1),
  }));
  return cue.words.flatMap((word) => {
    const text = positioned.filter(({offset}) => offset >= word.char_start && offset < word.char_end)
      .map(({character}) => character).join('');
    return text ? [{word, text}] : [];
  });
};

const pulse = (songFrame: number, eventFrame: number): number => {
  const elapsed = songFrame - eventFrame;
  return elapsed >= 0 && elapsed < 6 ? 1 - elapsed / 6 : 0;
};

const wordStyle = (word: AlignedWord, {cue, songFrame}: WordCueContextValue): CSSProperties => {
  const visible = songFrame >= word.start_frame;
  const beatPulse = Math.max(0, ...cue.accent_beat_frames
    .filter((beat) => beat >= word.start_frame && beat < word.end_frame)
    .map((beat) => pulse(songFrame, beat)));
  const emphasis = Math.max(pulse(songFrame, word.start_frame) * 0.025, beatPulse * 0.018);
  return {
    display: 'inline-block', visibility: visible ? 'visible' : 'hidden',
    // No entrance tween or opacity ramp: the word is readable at its first frame.
    // Holding its allocated width also prevents later words from moving the line.
    transform: `scale(${1 + emphasis})`, transformOrigin: '50% 50%',
  };
};

export type SyncedLyricProps = {
  readonly context: WordCueContextValue;
  readonly text: string;
  readonly x: number;
  readonly y: number;
  readonly size: number;
  readonly color: string;
  readonly width?: number;
  readonly align?: CSSProperties['textAlign'];
};

export const SyncedLyric = ({context, text, x, y, size, color, width,
  align = 'left'}: SyncedLyricProps) => (
  <div style={{position: 'absolute', left: x, top: y, width, fontSize: size, color,
    fontFamily: FILM.font, fontWeight: FILM.weight.lyric, lineHeight: 1.1,
    letterSpacing: '-0.045em', whiteSpace: 'pre', textAlign: align, fontKerning: 'normal'}}>
    {getWordFragments(context.cue, text).map(({word, text: wordText}) =>
      <span key={`${word.char_start}-${word.char_end}`} style={wordStyle(word, context)}
        aria-hidden={context.songFrame < word.start_frame}>{wordText}</span>)}
  </div>
);
