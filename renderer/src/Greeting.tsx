// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {copyText} from './copy';
import {AbsoluteFill, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Video} from '@remotion/media';
import {COPY} from './copy';
import {FILM} from './theme';

export const Greeting = ({fontFamily = FILM.font, durationInFrames}: Readonly<{
  fontFamily?: string; durationInFrames?: number;
}>) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const duration = durationInFrames ?? Math.round(4 * fps);
  if (duration < 1) return null;
  if (COPY.assets.greeting) {
    const fadeIn = Math.min(3, duration / 4);
    const holdEnd = Math.max(fadeIn, duration - Math.min(12, duration / 4));
    const opacity = interpolate(frame, [0, fadeIn, holdEnd, duration], [0, 1, 1, 0],
      {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    return <AbsoluteFill style={{background: FILM.colors.black}}>
      <Video src={staticFile(COPY.assets.greeting)} muted durationInFrames={duration}
        objectFit="contain" style={{width: '100%', height: '100%', opacity}} />
    </AbsoluteFill>;
  }
  const opacity = interpolate(frame, [0, 0.9 * fps, 3.2 * fps, 4 * fps], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill style={{background: FILM.colors.black, justifyContent: 'center', alignItems: 'center'}}>
      <div style={{color: FILM.colors.cream, fontFamily,
        fontWeight: FILM.weight.body, fontSize: 164, letterSpacing: 0, opacity}}>
        {copyText('Greeting.003')}</div>
    </AbsoluteFill>
  );
};
