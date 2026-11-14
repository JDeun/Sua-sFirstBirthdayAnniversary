// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {AbsoluteFill, CanvasImage, Sequence, staticFile, useVideoConfig} from 'remotion';
import {createMatchcutPlan} from './timeline';
import {FaceMatchcutGuide} from './Guide';
import type {MatchcutGuide, MatchcutPhoto, MatchcutTiming} from './types';

export type FaceMatchcutProps = Omit<MatchcutTiming, 'fps'> & Readonly<{
  photos: readonly MatchcutPhoto[]; guide?: boolean | MatchcutGuide;
  background?: string; resolveAsset?: (asset: string) => string;
}>;

/** Accepts already aligned pixels; it never reads a project manifest or detects faces. */
export const FaceMatchcut = ({photos, guide = false, background = '#000',
  resolveAsset = staticFile, ...timing}: FaceMatchcutProps) => {
  const {fps, width, height} = useVideoConfig();
  const plan = createMatchcutPlan(photos, {...timing, fps});
  return <AbsoluteFill style={{background}}>
    {plan.cuts.map(cut => <Sequence key={cut.photo.id} name={cut.photo.label ?? cut.photo.id}
      from={cut.from} durationInFrames={cut.durationInFrames}>
      <CanvasImage src={resolveAsset(cut.photo.asset)} width={width} height={height} fit="fill" />
    </Sequence>)}
    {guide ? <FaceMatchcutGuide width={width} height={height}
      {...(typeof guide === 'object' ? guide : {})} /> : null}
  </AbsoluteFill>;
};
