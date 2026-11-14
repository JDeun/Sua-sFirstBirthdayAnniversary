// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {FILM} from '../theme';
import {DrawnCrown, StarBloom, StarTrail} from './stars-and-crown';
import {GiftBoxBack, GiftBoxFront, GiftBoxLid, HeartHalo} from './gift';
import {Halo, QuietStars, SubjectOrbits} from './space';
import {CelestialSticker, STICKER_KINDS} from './stickers';

export const ASSET_IDS = ['star', 'crown', 'gift', 'universe', 'heart', ...STICKER_KINDS] as const;
export type MotionAssetId = typeof ASSET_IDS[number];
export const ASSET_LABELS: Readonly<Record<MotionAssetId, string>> = {
  star: '별', crown: '왕관', gift: '선물상자', universe: '우주 궤도', heart: '하트',
  moon: '초승달', planet: '고리 행성', 'shooting-star': '별똥별', cloud: '구름',
  castle: '작은 성', balloons: '풍선',
};

const Graphic = ({id, frame}: {readonly id: MotionAssetId; readonly frame: number}) => {
  if (id === 'star') return <><StarBloom frame={frame} x={960} y={540} size={640} />
    <StarTrail frame={frame} /></>;
  if (id === 'crown') return <DrawnCrown frame={frame} x={600} y={310} width={720} />;
  if (id === 'gift') return <div style={{position: 'absolute', inset: 0,
    transform: 'translate(-300px, -80px) scale(0.85)', transformOrigin: '960px 540px'}}>
    <GiftBoxBack /><GiftBoxLid frame={frame} /><GiftBoxFront frame={frame} />
  </div>;
  if (id === 'universe') return <><QuietStars frame={frame} color={FILM.colors.lavenderInk} />
    <Halo frame={frame} x={960} y={540} radius={310} color={FILM.colors.blue} filled />
    <SubjectOrbits frame={frame} x={960} y={540} color={FILM.colors.lavenderInk} /></>;
  if (id === 'heart') return <div style={{position: 'absolute', inset: 0,
    transform: 'translate(468px, -12px)'}}><HeartHalo frame={frame} /></div>;
  return <CelestialSticker kind={id} frame={frame} />;
};

/** Transparent 1920x1080 layer. frame is a local clock measured at 30 fps. */
export const MotionAsset = ({id, frame, x = 0, y = 0, scale = 1, rotation = 0,
  opacity = 1}: Readonly<{id: MotionAssetId; frame: number; x?: number; y?: number;
    scale?: number; rotation?: number; opacity?: number}>) => {
  if (frame < 0) return null;
  return <div aria-hidden style={{position: 'absolute', inset: 0, pointerEvents: 'none',
    opacity, transformOrigin: '50% 50%',
    transform: `translate(${x}px, ${y}px) rotate(${rotation}deg) scale(${scale})`}}>
    <Graphic id={id} frame={frame} />
  </div>;
};
