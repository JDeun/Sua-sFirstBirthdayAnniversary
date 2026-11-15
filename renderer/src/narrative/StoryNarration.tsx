// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {useCurrentFrame} from 'remotion';
import {NARRATIVE} from './edit';
import {FILM} from '../theme';
import {activeStoryCaption, storyCaptionLayout} from './story-captions';
import {verseEase} from './VerseMotion';
import type {StoryNarrationCue} from './runtime-types';

const NarrativeLine = ({cue, frame}: Readonly<{cue: StoryNarrationCue; frame: number}>) => {
  const box = storyCaptionLayout(cue);
  const {size, bottom} = box;
  const drawn = verseEase(frame - cue.start_frame, 20);
  return <div data-story-narration={cue.id} style={{position: 'absolute',
    left: box.x, top: box.y, width: box.width, fontFamily: FILM.font, color: FILM.colors.ink,
    textAlign: box.align, pointerEvents: 'none', boxSizing: 'border-box',
    padding: bottom ? '16px 28px 18px' : '0 12px', borderRadius: bottom ? 22 : 0,
    background: bottom ? 'rgba(255,248,240,0.94)' : undefined}}>
    {cue.label ? <div style={{fontSize: 27, fontWeight: 600, letterSpacing: 1,
      color: FILM.colors.lavenderInk, marginBottom: 12}}>
      {cue.label}{cue.date_label ? ` · ${cue.date_label}` : ''}</div> : null}
    <div style={{fontSize: size, fontWeight: 600, lineHeight: 1.42,
      letterSpacing: -size * 0.035, whiteSpace: 'pre-line'}}>{cue.text}</div>
    {!bottom ? <svg width={190} height={18} aria-hidden style={{marginTop: 15}}>
      <path d="M4 8 Q82 16 184 5" fill="none" stroke={FILM.colors.peachInk}
        strokeWidth={3} strokeLinecap="round" opacity={0.5} pathLength={1}
        strokeDasharray="1 1" strokeDashoffset={1 - drawn} />
    </svg> : null}
  </div>;
};

/** This clock outlives individual photo Sequences, so album cuts do not reset the sentence. */
export const StoryNarration = () => {
  const frame = useCurrentFrame();
  const cue = activeStoryCaption(NARRATIVE.story_captions, frame);
  return cue ? <NarrativeLine cue={cue} frame={frame} /> : null;
};
