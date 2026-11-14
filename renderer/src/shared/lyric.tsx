// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {useContext, type CSSProperties} from 'react';
import {SyncedLyric, WordCueContext} from '../synced/word-cues';

type LyricProps = {
  readonly frame: number; readonly delay?: number;
  readonly text: string; readonly x: number; readonly y: number;
  readonly size: number; readonly color: string; readonly width?: number;
  readonly align?: CSSProperties['textAlign'];
};

/** Each display fragment follows the supplied original-song word clock. */
export const Lyric = ({frame: _frame, delay: _delay, align = 'left', ...props}: LyricProps) => {
  const context = useContext(WordCueContext);
  if (!context) throw new Error('Lyric requires an aligned word context.');
  return <SyncedLyric {...props} align={align} context={context} />;
};
