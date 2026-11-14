// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {copyText} from './copy';
import {Track} from 'remotion';
import {FaceMatchcut as SharedFaceMatchcut, getMatchcutDuration} from './modules/face-matchcut';
import {OPENING_MATCHCUT_PHOTOS as activePhotos} from './opening-media';

export const MATCHCUT_PHOTO_COUNT = activePhotos.length;
export const matchcutDuration = (rate = 15, fps = 30) => getMatchcutDuration(activePhotos.length, rate, fps);

export const FaceMatchcut = ({guide = false, rate = 15}: {
  readonly guide?: boolean;
  readonly rate?: number;
}) => {
  const photos = activePhotos.map(photo => ({...photo, label: copyText('FaceMatchcut.002',
    {value0: photo.captured_at?.slice(0, 10) ?? '', value1: photo.id})}));
  return <Track name={copyText('FaceMatchcut.001')}>
    <SharedFaceMatchcut photos={photos} rate={rate} guide={guide} />
  </Track>;
};
