import React from 'react';
import {Composition} from 'remotion';
import {BirthdayPreview} from './BirthdayPreview';
import {TemplateShowcase} from './templates/TemplateShowcase';
import {DEMO_DURATION_FRAMES, type TemplateId} from './templates/presets';
import {OpeningSequence, type OpeningSequenceProps} from './opening/OpeningSequence';
import {OPENING_DURATION_FRAMES, OPENING_FPS} from './opening/timing';
import {BirthdayFilm, filmDurationOf, type BirthdayFilmProps} from './film/BirthdayFilm';

const VARIANTS: {id: TemplateId; compositionId: string}[] = [
  {id: 'cinematic', compositionId: 'CinematicPreview'},
  {id: 'scrapbook', compositionId: 'ScrapbookPreview'},
  {id: 'variety', compositionId: 'VarietyPreview'},
];

const defaultOpeningProps: OpeningSequenceProps = {
  imagePaths: [],
  musicPath: '',
};

// Synthetic-only preview: the real film length comes from --props=../data/film-props.json.
const defaultFilmProps: BirthdayFilmProps = {
  opening: {
    imagePaths: [],
    musicPath: '',
    timing: {matchcutEndFrame: 270, songStartFrame: 360},
  },
  songDurationFrames: 90 * OPENING_FPS,
  endCardFrames: 120,
  shots: [],
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
      id="BirthdayFilm"
      component={BirthdayFilm}
      defaultProps={defaultFilmProps}
      calculateMetadata={({props}) => ({durationInFrames: filmDurationOf(props)})}
      durationInFrames={filmDurationOf(defaultFilmProps)}
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
