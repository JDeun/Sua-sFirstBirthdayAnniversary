// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {Composition} from 'remotion';
import {FamilyFilm} from './NarrativeFilmDraft';
import {FaceMatchcut, MATCHCUT_PHOTO_COUNT, matchcutDuration} from './FaceMatchcut';
import {NARRATIVE} from './narrative/edit';

export const filmMetadata = () => ({fps: NARRATIVE.fps, width: 1920, height: 1080,
  durationInFrames: NARRATIVE.total_frames});

export const Root = () => <>
  <Composition id="FamilyFilm" component={FamilyFilm} {...filmMetadata()}
    calculateMetadata={filmMetadata} />
  {MATCHCUT_PHOTO_COUNT > 0 ? <Composition id="FaceMatchcut" component={FaceMatchcut}
    fps={NARRATIVE.fps} width={1920} height={1080}
    durationInFrames={matchcutDuration(15, NARRATIVE.fps)}
    calculateMetadata={({props}) => ({durationInFrames: matchcutDuration(typeof props.rate === 'number' ? props.rate : 15, NARRATIVE.fps)})} /> : null}
</>;
