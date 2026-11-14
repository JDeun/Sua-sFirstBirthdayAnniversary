// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {SONG_ASSET, copyText} from '../copy';
import {Audio} from '@remotion/media';
import {AbsoluteFill, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {getPerformanceTiming, type PerformanceCue} from './full-timing';
import {WordCueContext} from '../synced/word-cues';
import type {PerformanceProps} from './full-timing';
import {FILM} from '../theme';
import {PerformancePrincess, PerformanceShelter, PerformanceStar,
  PerformanceTremor, PerformanceUniverse} from './scenes';
import {wordEvent} from './timing';
import {PickupCard} from './type';
import {PerformanceGift, PerformanceLove, PerformancePrayer} from './faith-scenes';
import {PerformanceMedia, type PerformanceAsset, type PerformanceAssignments} from './production-media';

const SCENES = {star: PerformanceStar, princess: PerformancePrincess,
  universe: PerformanceUniverse, tremor: PerformanceTremor, shelter: PerformanceShelter,
  'star-repeat': PerformanceStar, 'princess-repeat': PerformancePrincess,
  gift: PerformanceGift, love: PerformanceLove, prayer: PerformancePrayer} as const;

const PerformanceWindow = ({cue, sourceStart, sourceEnd, asset}: {
  readonly cue: PerformanceCue;
  readonly sourceStart: number;
  readonly sourceEnd: number;
  readonly asset?: PerformanceAsset;
}) => {
  const frame = useCurrentFrame();
  const songFrame = sourceStart + frame;
  if (cue.id === 'star' || cue.id === 'star-repeat') {
    const first = wordEvent(cue, copyText('performance.ChorusPerformance.033'));
    const modifier = wordEvent(cue, copyText('performance.ChorusPerformance.034'));
    const star = wordEvent(cue, copyText('performance.ChorusPerformance.035'));
    if (songFrame < first.start) return <AbsoluteFill style={{background: FILM.colors.cream}} />;
    if (songFrame < modifier.start) return <PickupCard text={copyText('performance.ChorusPerformance.033')} frame={songFrame - first.start}
      duration={modifier.start - first.start} />;
    if (songFrame < star.start) return <PickupCard text={copyText('performance.ChorusPerformance.034')} frame={songFrame - modifier.start}
      duration={star.start - modifier.start} />;
  }
  const Scene = SCENES[cue.id];
  return <PerformanceMedia.Provider value={asset ?? null}>
    <WordCueContext.Provider value={{cue, songFrame}}>
      <Scene cue={cue} songFrame={songFrame} endFrame={sourceEnd} />
    </WordCueContext.Provider>
  </PerformanceMedia.Provider>;
};

/** All eight chorus lines, including the repeated hook, gift, love and prayer. */
export const ChorusPerformance = ({occurrenceIndex = 0, includeAudio = true, sourceAssignments, window}: PerformanceProps & {
  readonly includeAudio?: boolean;
  readonly sourceAssignments?: PerformanceAssignments;
  readonly window?: {readonly startFrame: number; readonly endFrame: number};
}) => {
  const {fps, durationInFrames, width, height} = useVideoConfig();
  const timing = getPerformanceTiming(occurrenceIndex);
  const startFrame = window?.startFrame ?? timing.startFrame;
  const endFrame = window?.endFrame ?? timing.endFrame;
  if (!Number.isSafeInteger(startFrame) || !Number.isSafeInteger(endFrame) ||
    startFrame < timing.startFrame || startFrame > timing.occurrence.cues[0].start_frame ||
    endFrame < timing.occurrence.cues.at(-1)!.end_frame || endFrame > timing.endFrame) {
    throw new Error('Chorus window must retain every sung word.');
  }
  if (fps !== timing.alignment.fps || durationInFrames !== endFrame - startFrame) {
    throw new Error('ChorusPerformance requires the aligned composition metadata.');
  }
  const scale = Math.min(width / 1920, height / 1080);
  return <>
    {includeAudio && SONG_ASSET ? <Audio src={staticFile(SONG_ASSET)} trimBefore={startFrame}
      durationInFrames={endFrame - startFrame} /> : null}
    <AbsoluteFill style={{background: FILM.colors.cream, overflow: 'hidden'}}>
      <div style={{position: 'absolute', width: 1920, height: 1080,
        transform: `scale(${scale})`, transformOrigin: 'top left',
        left: (width - 1920 * scale) / 2, top: (height - 1080 * scale) / 2}}>
        {timing.occurrence.cues.map((cue, index, cues) => {
          if (sourceAssignments && !sourceAssignments[cue.id]) throw new Error(`Missing production source: ${cue.id}`);
          const sourceStart = index === 0 ? startFrame : cue.start_frame;
          const sourceEnd = cues[index + 1]?.start_frame ?? endFrame;
          return <Sequence key={cue.id} from={sourceStart - startFrame}
            durationInFrames={sourceEnd - sourceStart} name={cue.text}>
            <PerformanceWindow cue={cue} sourceStart={sourceStart} sourceEnd={sourceEnd}
              asset={sourceAssignments?.[cue.id]} />
          </Sequence>;
        })}
      </div>
    </AbsoluteFill>
  </>;
};
