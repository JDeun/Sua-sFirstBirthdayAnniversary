// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {SONG_ASSET, copyText} from './copy';
import {Audio} from '@remotion/media';
import {AbsoluteFill, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {ChorusPerformance} from './performance/ChorusPerformance';
import {NARRATIVE, NARRATIVE_SHOTS, narrativeAssignments} from './narrative/edit';
import {NarrativeOpening} from './narrative/NarrativeOpening';
import {StoryMoment} from './narrative/StoryMoment';
import {OutroLyrics} from './narrative/OutroLyrics';
import {NarrativeFonts} from './narrative/NarrativeFonts';
import {MemorySound} from './narrative/MemorySound';
import {StoryNarration} from './narrative/StoryNarration';

export const NARRATIVE_FILM_FRAMES = NARRATIVE.total_frames;
const baselines = NARRATIVE_SHOTS.filter((shot) => shot.usage === 'baseline');
const choruses = NARRATIVE.choruses.map((window) => ({window,
  sources: narrativeAssignments(window.occurrenceIndex)}));

const FamilyStory = () => {
  const frame = useCurrentFrame();
  const end = NARRATIVE.main_duration_in_frames;
  const opacity = interpolate(frame, [end - 30, end - 1], [1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <>
    {SONG_ASSET ? <Audio src={staticFile(SONG_ASSET)} durationInFrames={end} volume={1} /> : null}
    <MemorySound />
    <AbsoluteFill style={{opacity}}>
      {baselines.map((shot) => <Sequence key={shot.id}
        name={shot.pending_media ? copyText('NarrativeFilmDraft.004') : shot.caption || shot.event?.label || shot.id}
        from={shot.song_start_frame} durationInFrames={shot.duration_in_frames}>
        <StoryMoment shot={shot} />
      </Sequence>)}
      {choruses.map(({window, sources}) => <Sequence key={window.occurrenceIndex}
        name={copyText('NarrativeFilmDraft.005', {value0: window.occurrenceIndex + 1})}
        from={window.start_frame} durationInFrames={window.end_frame - window.start_frame}>
        <ChorusPerformance occurrenceIndex={window.occurrenceIndex} includeAudio={false}
          sourceAssignments={sources} window={{startFrame: window.start_frame, endFrame: window.end_frame}} />
      </Sequence>)}
      <StoryNarration />
      <OutroLyrics />
    </AbsoluteFill>
  </>;
};

export const FamilyFilm = () => <AbsoluteFill style={{background: '#000'}}>
  <NarrativeFonts />
  {NARRATIVE.opening.duration_in_frames > 0 ? <Sequence durationInFrames={NARRATIVE.opening.duration_in_frames} name={copyText('NarrativeFilmDraft.006')}>
    <NarrativeOpening />
  </Sequence> : null}
  <Sequence from={NARRATIVE.opening.duration_in_frames} durationInFrames={NARRATIVE.main_duration_in_frames}
    name={copyText('NarrativeFilmDraft.007')}><FamilyStory /></Sequence>
</AbsoluteFill>;
