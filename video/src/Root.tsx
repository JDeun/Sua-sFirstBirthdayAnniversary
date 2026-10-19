import React from 'react';
import {Composition} from 'remotion';
import {BirthdayPreview} from './BirthdayPreview';
import {TemplateShowcase} from './templates/TemplateShowcase';
import {DEMO_DURATION_FRAMES, type TemplateId} from './templates/presets';
import {OpeningSequence, type OpeningSequenceProps} from './opening/OpeningSequence';
import {OPENING_DURATION_FRAMES, OPENING_FPS} from './opening/timing';

const VARIANTS: {id: TemplateId; compositionId: string}[] = [
  {id: 'cinematic', compositionId: 'CinematicPreview'},
  {id: 'scrapbook', compositionId: 'ScrapbookPreview'},
  {id: 'variety', compositionId: 'VarietyPreview'},
];

const defaultOpeningProps: OpeningSequenceProps = {
  imagePaths: [],
  musicPath: '',
};

export const Root: React.FC = () => (
  <>
    <Composition
      id="OpeningSequence"
      component={OpeningSequence}
      defaultProps={defaultOpeningProps}
      durationInFrames={OPENING_DURATION_FRAMES}
      fps={OPENING_FPS}
      width={1920}
      height={1080}
    />
    <Composition
      id="BirthdayPreview"
      component={BirthdayPreview}
      durationInFrames={600}
      fps={30}
      width={1920}
      height={1080}
    />
    {VARIANTS.map(({id, compositionId}) => (
      <Composition
        key={id}
        id={compositionId}
        component={TemplateShowcase}
        defaultProps={{variant: id}}
        durationInFrames={DEMO_DURATION_FRAMES}
        fps={30}
        width={1920}
        height={1080}
      />
    ))}
  </>
);
