import React from 'react';
import {Composition} from 'remotion';
import {BirthdayPreview} from './BirthdayPreview';

export const Root: React.FC = () => (
  <Composition
    id="BirthdayPreview"
    component={BirthdayPreview}
    durationInFrames={600}
    fps={30}
    width={1920}
    height={1080}
  />
);
