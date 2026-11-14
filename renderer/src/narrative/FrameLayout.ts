// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import type {NarrativeAsset, NarrativeShot} from './edit';

export type CaptionCue = NonNullable<NarrativeShot['captionCues']>[number];
export type StoryShot = NarrativeShot;
export type Rect = Readonly<{x: number; y: number; width: number; height: number}>;
export type FrameFamily = 'near-bleed' | 'contact-print' | 'cinema' | 'milestone' | 'family-album';
export type FrameLayout = Readonly<{
  family: FrameFamily; media: Rect; words: Rect; radius: number; mat: number;
  tilt: number; align: 'left' | 'center' | 'right'; typeSize: number;
  shade: 'cream' | 'blue' | 'lavender' | 'peach' | 'rose';
  typeface: 'serif' | 'sans'; inset: number; backing?: Rect; foot?: number; captionFlow?: 'line';
}>;
type Recipe = Omit<FrameLayout, 'media'> & Readonly<{bounds: Rect}>;
const rect = (x: number, y: number, width: number, height: number): Rect => ({x, y, width, height});

const recipes = {
  'near-bleed': {family: 'near-bleed', bounds: rect(36, 0, 608, 1080),
    words: rect(844, 368, 900, 400), radius: 0, mat: 0, tilt: 0, inset: 14,
    align: 'left', typeSize: 156, shade: 'cream', typeface: 'sans'},
  'contact-print': {family: 'contact-print', bounds: rect(180, 116, 660, 858),
    words: rect(1032, 456, 760, 400), radius: 2, mat: 14, tilt: 0, inset: 0,
    align: 'left', typeSize: 148, shade: 'rose', typeface: 'sans'},
  cinema: {family: 'cinema', bounds: rect(64, 32, 1792, 918),
    words: rect(190, 968, 1540, 108), radius: 0, mat: 0, tilt: 0, inset: 0,
    align: 'center', typeSize: 84, shade: 'blue', typeface: 'sans'},
  milestone: {family: 'milestone', bounds: rect(1036, 0, 608, 1080),
    words: rect(148, 386, 816, 560), radius: 0, mat: 0, tilt: 0, inset: 0,
    align: 'left', typeSize: 156, shade: 'lavender', typeface: 'sans'},
  'family-album': {family: 'family-album', bounds: rect(68, 96, 1160, 888),
    words: rect(1320, 392, 520, 470), radius: 1, mat: 20, tilt: 0, inset: 0,
    align: 'left', typeSize: 148, shade: 'peach', typeface: 'sans'},
} as const satisfies Readonly<Record<FrameFamily, Recipe>>;

export const sourceAspect = (asset: NarrativeAsset): number => {
  const [width, height] = asset.dimensions;
  return width * (asset.crop?.[2] ?? 1) / (height * (asset.crop?.[3] ?? 1));
};

const fitFrame = (bounds: Rect, aspect: number, mat: number, foot = 0): Rect => {
  const height = Math.min(bounds.height - mat * 2 - foot, (bounds.width - mat * 2) / aspect);
  const width = height * aspect;
  return rect(bounds.x + (bounds.width - width - mat * 2) / 2,
    bounds.y + (bounds.height - height - mat * 2 - foot) / 2, width + mat * 2, height + mat * 2 + foot);
};

/** Reserve the left text column when a closing lyric owns the frame. */
const closingLayout = (asset: NarrativeAsset): FrameLayout => {
  const recipe: Recipe = {...recipes['near-bleed'], bounds: rect(1110, 0, 810, 1080),
    words: rect(148, 294, 770, 650), inset: 14};
  return {...recipe, media: fitFrame(recipe.bounds, sourceAspect(asset), recipe.mat)};
};

export const getStoryAsset = (_shot: StoryShot, asset: NarrativeAsset): NarrativeAsset => asset;

/** Caption-free album cuts give the complete picture the canvas, without an empty text column. */
const galleryLayout = (shot: StoryShot, asset: NarrativeAsset): FrameLayout => {
  const aspect = sourceAspect(asset);
  const variation = [...shot.id].reduce((sum, letter) => sum + letter.charCodeAt(0), 0) % 3;
  const photo = asset.kind === 'photo';
  const recipe: Recipe = {...recipes.cinema,
    bounds: aspect > 1.25 ? rect(72, 44, 1776, 992) : rect(400 + variation * 32, 44, 1056, 992),
    mat: photo ? 12 : 0, shade: (['cream', 'rose', 'blue'] as const)[variation],
    words: rect(148, 384, 770, 340)};
  return {...recipe, media: fitFrame(recipe.bounds, aspect, recipe.mat)};
};

/** Five editorial silhouettes; source aspect, never a fixed card, defines the aperture. */
export const getFrameLayout = (shot: StoryShot, asset: NarrativeAsset): FrameLayout => {
  if (shot.frameLayout) return shot.frameLayout;
  if (shot.lyricOwned) return closingLayout(asset);
  if (shot.layout === 'gallery' && !shot.event && !shot.captionCues?.length && !shot.caption) {
    return galleryLayout(shot, asset);
  }
  const aspect = sourceAspect(asset);
  const fallback = aspect > 1.45 ? 'cinema' : asset.kind === 'photo' ? 'contact-print' : 'near-bleed';
  const family = shot.layout && shot.layout in recipes ? shot.layout as FrameFamily : fallback;
  const recipe = recipes[family];
  return {...recipe, media: fitFrame(recipe.bounds, aspect, recipe.mat)};
};
