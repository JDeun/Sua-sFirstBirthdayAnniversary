// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import type {MatchcutPhoto, MatchcutPlan, MatchcutTiming} from './types';

const positive = (value: number, name: string) => {
  if (!Number.isFinite(value) || value <= 0) throw new Error(`${name} must be positive and finite.`);
};

export const getMatchcutDuration = (count: number, rate = 15, fps = 30) => {
  if (!Number.isSafeInteger(count) || count < 0) throw new Error('Photo count must be a nonnegative integer.');
  positive(fps, 'fps');
  positive(rate, 'rate');
  if (rate > fps) throw new Error('Photo rate cannot exceed fps.');
  const duration = Math.round(count * fps / rate);
  if (!Number.isSafeInteger(duration)) throw new Error('Matchcut duration is too large.');
  return duration;
};

const selectedPhotos = (photos: readonly MatchcutPhoto[], options: MatchcutTiming) => {
  const excluded = new Set(options.excludedIds ?? []);
  const selected = photos.filter(photo => !excluded.has(photo.id));
  const ids = new Set<string>();
  for (const photo of selected) {
    if (typeof photo.id !== 'string' || typeof photo.asset !== 'string' ||
      !photo.id.trim() || !photo.asset.trim()) throw new Error('Every photo needs an id and asset.');
    if (ids.has(photo.id)) throw new Error('Photo ids must be unique.');
    ids.add(photo.id);
  }
  return options.reverse ? selected.slice().reverse() : selected;
};

/** Integer boundaries cover the exact duration without gaps or zero-frame cuts. */
export const createMatchcutPlan = (photos: readonly MatchcutPhoto[], options: MatchcutTiming): MatchcutPlan => {
  positive(options.fps, 'fps');
  if (options.rate !== undefined && options.durationInFrames !== undefined) {
    throw new Error('Choose a photo rate or an exact duration, not both.');
  }
  const selected = selectedPhotos(photos, options);
  const duration = options.durationInFrames ?? getMatchcutDuration(selected.length, options.rate, options.fps);
  if (!Number.isSafeInteger(duration) || duration < selected.length || duration < 0) {
    throw new Error('Duration must be an integer with at least one frame per photo.');
  }
  if (!selected.length) return {durationInFrames: duration, cuts: []};
  const boundary = options.durationInFrames === undefined ?
    (index: number) => Math.round(index * options.fps / (options.rate ?? 15)) :
    (index: number) => Math.round(index * duration / selected.length);
  const cuts = selected.map((photo, index) => {
    const from = boundary(index);
    const end = boundary(index + 1);
    return {photo, from, durationInFrames: end - from};
  });
  return {durationInFrames: duration, cuts};
};

/** Keep endpoints and input order; a larger limit never repeats photos. */
export const sampleMatchcutPhotos = <T,>(photos: readonly T[], limit: number): readonly T[] => {
  if (!Number.isSafeInteger(limit) || limit < 1) throw new Error('Sample limit must be a positive integer.');
  if (photos.length <= limit) return photos.slice();
  if (limit === 1) return [photos[0]];
  return Array.from({length: limit}, (_, i) => photos[Math.round(i * (photos.length - 1) / (limit - 1))]);
};
