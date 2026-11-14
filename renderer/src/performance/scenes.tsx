// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {copyText} from '../copy';
import {AbsoluteFill} from 'remotion';
import type {PerformanceCue} from './full-timing';
import {Lyric} from '../shared/lyric';
import {Halo, QuietStars, ShelterArcs, SubjectOrbits} from '../assets/space';
import {FILM} from '../theme';
import {DrawnCrown, StarBloom, StarTrail} from '../assets/stars-and-crown';
import {ImpactWord, NounWithParticle} from './type';
import {FramedPerformancePhoto, PerformancePortrait, framedHead, portraitGeometry, type PortraitPose} from './portrait';
import {usePerformanceAsset} from './production-media';
import {eventClock, wordEvent} from './timing';

type Props = {readonly cue: PerformanceCue; readonly songFrame: number; readonly endFrame: number};
const {colors} = FILM;
const POSES = {
  star: {faceX: 700, faceY: 300, height: 1098},
  universe: {faceX: 1425, faceY: 280, height: 1080},
  tremor: {faceX: 1380, faceY: 485, height: 1116},
  shelter: {faceX: 540, faceY: 336, height: 1080},
} as const satisfies Record<'star' | 'universe' | 'tremor' | 'shelter', PortraitPose>;

export const PerformanceStar = ({cue, songFrame, endFrame}: Props) => {
  const event = wordEvent(cue, copyText('performance.ChorusPerformance.035'));
  const clock = songFrame - event.start;
  return <AbsoluteFill style={{background: colors.blue}}>
    <QuietStars frame={clock} color={colors.blueInk} />
    <StarBloom frame={clock} x={700} y={610} size={930} color={colors.cream} />
    <StarTrail frame={clock} />
    <ImpactWord text={copyText('performance.scenes.055')} frame={clock} duration={endFrame - event.start}
      x={1070} y={205} size={650} width={800} color={colors.blueInk} tilt={-7} />
    {cue.id === 'star-repeat' ? <FramedPerformancePhoto />
      : <PerformancePortrait pose={POSES.star} frame={clock} />}
  </AbsoluteFill>;
};

export const PerformancePrincess = ({cue, songFrame, endFrame}: Props) => {
  const event = wordEvent(cue, copyText('performance.scenes.056'));
  const clock = songFrame - event.start;
  const asset = usePerformanceAsset();
  const pose: PortraitPose = {faceX: 560, faceY: 430, height: 1040, headroom: 160};
  if (!asset) throw new Error('Performance media assignment is required.');
  const head = asset.framing === 'cutout' ? portraitGeometry(pose, asset) : framedHead(asset);
  return <AbsoluteFill style={{background: colors.peach}}>
    <Halo frame={songFrame - cue.start_frame} x={540} y={580} radius={455}
      color={colors.cream} filled />
    <Lyric frame={0} text={copyText('performance.ChorusPerformance.034')} x={1070} y={130} size={120} color={colors.ink} />
    {clock >= 0 ? <ImpactWord text={copyText('performance.scenes.056')} frame={clock} duration={endFrame - event.start}
      x={930} y={330} size={440} width={940} color={colors.lavenderInk} tilt={7} /> : null}
    {asset?.framing === 'cutout' ? <PerformancePortrait pose={pose} frame={songFrame - cue.start_frame} />
      : <FramedPerformancePhoto />}
    {clock >= 0 ? <DrawnCrown frame={clock} x={head.headX - 125} y={head.headY - 125}
      width={250} rotation={-5} /> : null}
  </AbsoluteFill>;
};

export const PerformanceUniverse = ({cue, songFrame, endFrame}: Props) => {
  const event = wordEvent(cue, copyText('performance.scenes.057'));
  const clock = songFrame - event.start;
  return <AbsoluteFill style={{background: colors.lavender}}>
    <QuietStars frame={songFrame} color={colors.lavenderInk} />
    <SubjectOrbits frame={Math.max(0, clock)} x={1400} y={600} color={colors.lavenderInk} />
    <Lyric frame={0} text={copyText('performance.scenes.058')} x={120} y={100} size={104} color={colors.ink} />
    {clock >= 0 ? <NounWithParticle noun={copyText('performance.scenes.059')} particle={copyText('performance.scenes.060')} frame={clock}
      duration={endFrame - event.start} x={90} y={300} size={430}
      particleSize={118} color={colors.lavenderInk} tilt={-8} /> : null}
    <Lyric frame={0} text={copyText('performance.scenes.061')} x={160} y={830} size={112} color={colors.ink} />
    <PerformancePortrait pose={POSES.universe} frame={songFrame - cue.start_frame} />
  </AbsoluteFill>;
};

export const PerformanceTremor = ({cue, songFrame, endFrame}: Props) => {
  const event = wordEvent(cue, copyText('performance.scenes.062'));
  const clock = songFrame - event.start;
  const shaking = eventClock(cue, copyText('performance.scenes.063'), songFrame);
  const angle = shaking >= 0 && shaking < 10 ? Math.sin(shaking * 1.3) * 3 : 0;
  return <AbsoluteFill style={{background: colors.rose}}>
    <Halo frame={clock} x={1390} y={580} radius={465} color={colors.cream} filled />
    <NounWithParticle noun={copyText('performance.scenes.064')} particle={copyText('performance.scenes.065')} frame={clock} duration={endFrame - event.start}
      x={70} y={180} size={425} particleSize={112} color={colors.ink} tilt={5} />
    <Lyric frame={0} text={copyText('performance.scenes.066')} x={130} y={710} size={110} color={colors.ink} />
    <div style={{position: 'absolute', inset: 0, transform: `rotate(${angle}deg)`,
      transformOrigin: '580px 800px'}}>
      <Lyric frame={0} text={copyText('performance.scenes.063')} x={320} y={670} size={174} color={colors.peachInk} />
    </div>
    <Lyric frame={0} text={copyText('performance.scenes.067')} x={560} y={890} size={100} color={colors.ink} />
    <PerformancePortrait pose={POSES.tremor} frame={clock} />
  </AbsoluteFill>;
};

export const PerformanceShelter = ({cue, songFrame, endFrame}: Props) => {
  const event = wordEvent(cue, copyText('performance.scenes.068'));
  const clock = songFrame - event.start;
  return <AbsoluteFill style={{background: colors.cream}}>
    <Halo frame={Math.max(0, clock)} x={520} y={570} radius={450} color={colors.blue} filled />
    {clock >= 0 ? <ShelterArcs frame={clock * 3} color={colors.blueInk} /> : null}
    <Lyric frame={0} text={copyText('performance.scenes.069')} x={1100} y={120} size={112} color={colors.ink} />
    {clock >= 0 ? <NounWithParticle noun={copyText('performance.scenes.070')} particle={copyText('performance.scenes.065')} frame={clock}
      duration={endFrame - event.start} x={1100} y={290} size={510}
      particleSize={125} color={colors.blueInk} tilt={-6} /> : null}
    <Lyric frame={0} text={copyText('performance.scenes.061')} x={1100} y={870} size={112} color={colors.lavenderInk} />
    <PerformancePortrait pose={POSES.shelter} frame={songFrame - cue.start_frame} />
  </AbsoluteFill>;
};
