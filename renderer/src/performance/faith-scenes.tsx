// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {copyText} from '../copy';
import {AbsoluteFill} from 'remotion';
import type {AlignedCue} from '../synced/alignment';
import {Lyric} from '../shared/lyric';
import {Halo, QuietStars} from '../assets/space';
import {tween} from '../shared/motion';
import {FILM} from '../theme';
import {FaithArchVideo} from './faith-graphics';
import {GiftBoxBack, GiftBoxFront, GiftBoxLid, HeartHalo} from '../assets/gift';
import {PerformancePortrait} from './portrait';
import {usePerformanceAsset} from './production-media';
import {eventClock, wordEvent} from './timing';
import {ImpactWord} from './type';

type Props = {
  readonly cue: Omit<AlignedCue, 'id'> & {readonly id: string};
  readonly songFrame: number;
  readonly endFrame: number;
};

const {colors} = FILM;
export const GIFT_POSE = {faceX: 1250, faceY: 500, height: 1000} as const;

/** Parent supplies WordCueContext; every entrance follows the actual vocal word. */
export const PerformanceGift = ({cue, songFrame, endFrame}: Props) => {
  const subjectScale = usePerformanceAsset()?.subjectScale ?? 1;
  const event = wordEvent(cue, copyText('performance.faith-scenes.038'));
  const clock = eventClock(cue, copyText('performance.faith-scenes.038'), songFrame);
  const rise = tween(clock, [0, 8, 10], [780, -12, 0]);
  return <AbsoluteFill style={{background: colors.cream}}>
    <Halo frame={Math.max(0, clock)} x={1260} y={620} radius={450}
      color={colors.rose} filled />
    <QuietStars frame={songFrame - cue.start_frame} color={colors.lavenderInk} />
    <Lyric frame={songFrame - cue.start_frame} text={copyText('performance.faith-scenes.039')}
      x={110} y={175} size={84} width={790} color={colors.ink} />
    <ImpactWord text={copyText('performance.faith-scenes.038')} frame={clock} duration={endFrame - event.start}
      x={100} y={350} size={330} width={760} color={colors.lavenderInk} tilt={-4} />
    <GiftBoxBack />
    <GiftBoxLid frame={clock} />
    {clock >= 0 ? <div style={{position: 'absolute', inset: 0, overflow: 'hidden',
      clipPath: 'polygon(0 0, 100% 0, 100% 620px, 1640px 620px, 1640px 1010px, 880px 1010px, 880px 620px, 0 620px)'}}>
      <div style={{position: 'absolute', inset: 0, transform: `translateY(${rise}px)`}}>
        <div style={{position: 'absolute', inset: 0,
          transformOrigin: `${GIFT_POSE.faceX}px ${GIFT_POSE.faceY}px`,
          transform: `scale(${subjectScale})`}}>
          {/* Hold the settle clock; subject scale stays inside the unchanged rise. */}
          <PerformancePortrait pose={GIFT_POSE} frame={10} />
        </div>
      </div>
    </div> : null}
    <GiftBoxFront frame={clock} />
  </AbsoluteFill>;
};

export const PerformanceLove = ({cue, songFrame, endFrame}: Props) => {
  const event = wordEvent(cue, copyText('performance.faith-scenes.040'));
  const clock = eventClock(cue, copyText('performance.faith-scenes.040'), songFrame);
  const local = songFrame - cue.start_frame;
  return <AbsoluteFill style={{background: colors.rose}}>
    <HeartHalo frame={clock} />
    <Halo frame={local} x={500} y={580} radius={434} color={colors.peach} filled />
    <FaithArchVideo source="love" side="left" />
    <Lyric frame={local} text={copyText('performance.faith-scenes.041')} x={1000} y={175} size={112} color={colors.ink} />
    <ImpactWord text={copyText('performance.faith-scenes.040')} frame={clock} duration={endFrame - event.start}
      x={950} y={340} size={360} width={850} color={colors.peachInk} tilt={4} />
    <Lyric frame={local} text={copyText('performance.faith-scenes.042')} x={1000} y={850}
      size={110} width={800} color={colors.ink} />
  </AbsoluteFill>;
};

export const PerformancePrayer = ({cue, songFrame, endFrame}: Props) => {
  const event = wordEvent(cue, copyText('performance.faith-scenes.043'));
  const clock = eventClock(cue, copyText('performance.faith-scenes.043'), songFrame);
  const local = songFrame - cue.start_frame;
  return <AbsoluteFill style={{background: colors.peach}}>
    <QuietStars frame={local} color={colors.lavenderInk} />
    <Halo frame={local} x={1490} y={570} radius={440} color={colors.rose} filled />
    <Halo frame={local} x={1490} y={570} radius={470} color={colors.peachInk} />
    <FaithArchVideo source="prayer" side="right" />
    <Lyric frame={local} text={copyText('performance.faith-scenes.044')} x={110} y={190}
      size={104} width={960} color={colors.ink} />
    <ImpactWord text={copyText('performance.faith-scenes.043')} frame={clock} duration={endFrame - event.start}
      x={80} y={390} size={295} width={1040} color={colors.lavenderInk} tilt={-3} />
  </AbsoluteFill>;
};
