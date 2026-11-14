// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {copyText} from '../copy';
import {Audio} from '@remotion/media';
import {interpolate, Sequence, staticFile} from 'remotion';
import {NARRATIVE, NARRATIVE_SHOTS} from './edit';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export const laughterVolume = (frame: number) => {
  const sound = NARRATIVE.memory_audio;
  if (!sound || sound.enabled === false) return 0;
  const [start, end] = sound.source_window_frames;
  if (frame < start || frame >= end) return 0;
  const fade = Math.min(sound.source_fade_frames, (end - start) / 2);
  if (fade <= 0) return sound.source_gain;
  if (frame < start + fade) return interpolate(frame, [start, start + fade], [0, sound.source_gain], clamp);
  return interpolate(frame, [end - fade, end], [sound.source_gain, 0], clamp);
};

export const MemorySound = () => {
  const sound = NARRATIVE.memory_audio;
  if (!sound || sound.enabled === false) return null;
  const shot = NARRATIVE_SHOTS.find((item) => item.id === sound.shot_id);
  if (!shot || !sound.asset) throw new Error('Enabled memory audio requires its source shot and asset.');
  return <Sequence from={shot.song_start_frame} durationInFrames={shot.duration_in_frames}
    name={copyText('narrative.MemorySound.008')}>
    <Audio src={staticFile(sound.asset)} volume={laughterVolume} />
  </Sequence>;
};
