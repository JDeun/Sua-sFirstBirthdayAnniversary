// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import type {CaptionCue, FrameLayout, StoryShot} from './FrameLayout';
import {VerseTypography} from './VerseTypography';

const fallbackCue = (shot: StoryShot): readonly CaptionCue[] => shot.caption ? [{
  text: shot.caption, start_frame: shot.song_start_frame + 7,
  end_frame: shot.song_end_frame - 5, role: 'lead',
}] : [];

/** Song-absolute action intervals are never delayed, extended, or faded ahead of their end. */
export const StoryType = ({shot, songFrame, layout}: Readonly<{
  shot: StoryShot; songFrame: number; layout: FrameLayout;
}>) => {
  const event = shot.event;
  const eventActive = event && songFrame >= event.start_frame && songFrame < event.end_frame;
  const active = (shot.captionCues ?? (shot.lyricOwned ? [] : fallbackCue(shot))).filter((cue) =>
    songFrame >= cue.start_frame && songFrame < cue.end_frame);
  const cue = active.find((item) => item.role !== 'support') ?? active[0];
  if (!eventActive && !cue) return null;
  const item = eventActive ? event : cue!;
  const text = 'label' in item ? item.label : item.text;
  return <div style={{position: 'absolute', left: layout.words.x, top: layout.words.y,
    width: layout.words.width, textAlign: layout.align, pointerEvents: 'none'}}
    {...(eventActive ? {'data-story-event': text} : {'data-caption': text})}>
    <VerseTypography text={text} layout={layout} songFrame={songFrame}
      start={item.start_frame} end={item.end_frame} date={'date_label' in item ? item.date_label : ''} />
  </div>;
};
