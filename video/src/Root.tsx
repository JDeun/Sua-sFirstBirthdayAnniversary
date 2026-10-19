import React from 'react';
import {Composition} from 'remotion';
import {BirthdayPreview} from './BirthdayPreview';
import {TemplateShowcase} from './templates/TemplateShowcase';
import {DEMO_DURATION_FRAMES, TEMPLATE_PRESETS, type TemplateId} from './templates/presets';

const VARIANTS: {id: TemplateId; compositionId: string}[] = [
  {id: 'cinematic', compositionId: 'CinematicPreview'},
  {id: 'scrapbook', compositionId: 'ScrapbookPreview'},
  {id: 'variety', compositionId: 'VarietyPreview'},
];

export const Root: React.FC = () => (
  <>
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

// Keep this import evaluated so nonexistent preset keys are caught by TS.
void TEMPLATE_PRESETS;
