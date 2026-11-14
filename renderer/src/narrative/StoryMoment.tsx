// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {FILM} from '../theme';
import {NARRATIVE_ASSETS} from './edit';
import {getFrameLayout, getStoryAsset, type FrameLayout, type StoryShot} from './FrameLayout';
import {NarrativeMedia} from './NarrativeMedia';
import {StoryType} from './StoryType';
import {VerseBackdrop} from './VerseBackdrop';

const MemoryPaper = ({layout}: Readonly<{layout: FrameLayout}>) =>
  <AbsoluteFill aria-hidden="true" style={{background: `linear-gradient(112deg,
    ${FILM.colors[layout.shade]}, ${FILM.colors.cream} 86%)`}} />;

/** Photographs become prints, action becomes cinema; the child keeps the complete scene. */
export const StoryMoment = ({shot}: {readonly shot: StoryShot}) => {
  const frame = useCurrentFrame();
  const asset = getStoryAsset(shot, NARRATIVE_ASSETS[shot.id]);
  const layout = getFrameLayout(shot, asset);
  return <AbsoluteFill style={{background: FILM.colors.cream, overflow: 'hidden'}}>
    <MemoryPaper layout={layout} />
    <VerseBackdrop shot={shot} layout={layout} frame={frame} />
    <NarrativeMedia asset={asset} layout={layout} frame={frame} duration={shot.duration_in_frames}
      songFrame={shot.song_start_frame + frame} closing={shot.lyricOwned} />
    <StoryType shot={shot} songFrame={shot.song_start_frame + frame} layout={layout} />
  </AbsoluteFill>;
};
