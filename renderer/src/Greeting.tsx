// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {copyText} from './copy';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {FILM} from './theme';

export const Greeting = ({fontFamily = FILM.font}: {readonly fontFamily?: string}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const opacity = interpolate(frame, [0, 0.9 * fps, 3.2 * fps, 4 * fps], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill style={{background: FILM.colors.black, justifyContent: 'center', alignItems: 'center'}}>
      <div style={{color: FILM.colors.cream, fontFamily,
        fontWeight: FILM.weight.body, fontSize: 76, letterSpacing: 2, opacity}}>
        {copyText('Greeting.003')}</div>
    </AbsoluteFill>
  );
};
