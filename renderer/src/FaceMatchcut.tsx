// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {copyText} from './copy';
import {AbsoluteFill, CanvasImage, staticFile, Track, useVideoConfig} from 'remotion';
import {OPENING_PHOTOS as activePhotos} from './opening-media';

export const MATCHCUT_PHOTO_COUNT = activePhotos.length;
export const matchcutDuration = (rate = 15, fps = 30) => {
  if (!Number.isFinite(rate) || rate <= 0 || rate > fps) throw new Error('Matchcut rate must be positive and at most fps.');
  return Math.round(activePhotos.length * fps / rate);
};

export const FaceMatchcut = ({guide = false, rate = 15}: {
  readonly guide?: boolean;
  readonly rate?: number;
}) => {
  const {fps} = useVideoConfig();
  return (
  <AbsoluteFill style={{background: '#000'}}>
    <Track name={copyText('FaceMatchcut.001')}>
      {activePhotos.map((photo, index) => (
        <CanvasImage key={photo.stem} name={copyText('FaceMatchcut.002', {value0: photo.captured_at?.slice(0, 10) ?? '', value1: photo.stem})}
          src={staticFile(photo.asset)} from={Math.round(index * fps / rate)}
          durationInFrames={Math.round((index + 1) * fps / rate) - Math.round(index * fps / rate)}
          width={1920} height={1080} fit="fill" />
      ))}
    </Track>
    {guide ? (
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <ellipse cx={960} cy={420} rx={420} ry={400} fill="none" stroke="#47ffcf" strokeWidth={3} />
        <path d="M600 430H1320 M960 90V860" fill="none" stroke="#47ffcf" strokeWidth={2} />
        <circle cx={850} cy={430} r={12} fill="none" stroke="#ffdf5c" strokeWidth={4} />
        <circle cx={1070} cy={430} r={12} fill="none" stroke="#ffdf5c" strokeWidth={4} />
      </svg>
    ) : null}
  </AbsoluteFill>
  );
};
