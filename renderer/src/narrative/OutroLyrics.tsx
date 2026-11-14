// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {interpolate, useCurrentFrame} from 'remotion';
import timing from '../generated/outro-alignment.json';
import type {OutroAlignment} from './runtime-types';
import {FILM} from '../theme';
import {NARRATIVE_FONT} from './NarrativeFonts';

const outro = timing as unknown as OutroAlignment;
const line = outro.lines.find((item) => item.id === outro.final_line_id);
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** Word appearances use the song clock, independent of every photograph change. */
export const OutroLyrics = () => {
  const frame = useCurrentFrame();
  if (!line || frame < line.start_frame) return null;
  return <div style={{position: 'absolute', left: 148, top: 294, width: 770,
    fontFamily: NARRATIVE_FONT, color: FILM.colors.ink, pointerEvents: 'none'}}>
    {line.words.map((word, index) => {
      const age = frame - word.start_frame;
      if (age < 0) return null;
      const rise = interpolate(age, [0, 9], [14, 0], clamp);
      const size = index === 1 ? 142 : index === 0 ? 86 : 76;
      return <div key={word.text} data-outro-word={word.text}
        style={{fontSize: size, lineHeight: 1.4, fontWeight: index === 1 ? 600 : 400,
          letterSpacing: index === 1 ? -5 : index === 0 ? -2 : 1,
          color: index === 1 ? FILM.colors.lavenderInk : FILM.colors.ink,
          marginTop: index === 2 ? 35 : 8, transform: `translateY(${rise}px)`}}>
        {word.text}{index === 0 ? ',' : ''}
        {index === 1 ? <div style={{height: 2, width: interpolate(age, [0, 18], [0, 386], clamp),
          background: FILM.colors.lavenderInk, opacity: 0.3, marginTop: 12}} /> : null}
      </div>;
    })}
  </div>;
};
