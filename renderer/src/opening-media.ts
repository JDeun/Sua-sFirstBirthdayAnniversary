// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import photos from './generated/stopmotion.json';
import exclusions from './generated/media-exclusions.json';

export type OpeningPhoto = Readonly<{stem: string; asset: string; captured_at?: string | null}>;
export const EXCLUDED_STEMS: readonly string[] = exclusions.excluded_stems;
const excluded = new Set(EXCLUDED_STEMS);
export const OPENING_PHOTOS = (photos as readonly OpeningPhoto[]).filter((photo) => !excluded.has(photo.stem));
