// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {copyText} from '../copy';
import type {ReactNode} from 'react';
import {CanvasImage, staticFile} from 'remotion';
import {tween} from '../shared/motion';
import {FILM} from '../theme';
import {Video} from '@remotion/media';
import {usePerformanceAsset, type PerformanceAsset} from './production-media';

export type PortraitPose = {
  readonly faceX: number;
  readonly faceY: number;
  readonly height: number;
  readonly headroom?: number;
};

export const portraitGeometry = ({faceX, faceY, height, headroom}: PortraitPose,
  override: PerformanceAsset) => {
  const canvas = override.dimensions;
  const face = [override.face[0] * canvas[0], override.face[1] * canvas[1]];
  const head = [override.head[0] * canvas[0], override.head[1] * canvas[1]];
  const bounds = override?.alphaBounds ?? [0, 0, 1, 1];
  let scale = height / canvas[1];
  if (override) scale = Math.min(scale, 900 / Math.max(1, (bounds[2] - bounds[0]) * canvas[0]),
    970 / Math.max(1, (bounds[3] - bounds[1]) * canvas[1]));
  if (override && headroom) scale = Math.min(scale,
    (1060 - headroom) / Math.max(1, bounds[3] * canvas[1] - head[1]));
  const left = faceX - face[0] * scale;
  const intendedTop = faceY - face[1] * scale;
  const minTop = Math.max(50 - bounds[1] * canvas[1] * scale,
    headroom ? headroom - head[1] * scale : -Infinity);
  const maxTop = 1060 - bounds[3] * canvas[1] * scale;
  const top = override ? Math.max(minTop, Math.min(maxTop, intendedTop)) : intendedTop;
  return {left, top, width: canvas[0] * scale, height: canvas[1] * scale,
    headX: left + head[0] * scale, headY: top + head[1] * scale,
    origin: `${face[0] * scale}px ${face[1] * scale}px`};
};

export const PerformancePortrait = ({pose, frame}: {
  readonly pose: PortraitPose;
  readonly frame: number;
}) => {
  const override = usePerformanceAsset();
  if (!override) throw new Error('Performance media assignment is required.');
  if (override?.kind === 'video') return <ProductionVideo asset={override} left={pose.faceX < 960} />;
  if (override?.kind === 'photo' && override.framing === 'full') return (
    <PhotoPanel left={pose.faceX < 960}>
      <CompletePerformancePhoto asset={override} />
    </PhotoPanel>
  );
  const {left, top, width, height, origin} = portraitGeometry(pose, override);
  return <div style={{position: 'absolute', left, top, width, height,
    transformOrigin: origin, transform: `scale(${tween(frame, [0, 5], [1.035, 1])})`}}>
    <CanvasImage name={copyText('performance.portrait.053', {value0: override.original})}
      src={staticFile(override.asset)}
      width={width} height={height} fit="contain" style={{display: 'block'}} />
  </div>;
};

/** A complete photograph provides a different visual rhythm from a cutout. */
export const FramedPerformancePhoto = () => {
  const override = usePerformanceAsset();
  if (!override) throw new Error('Performance media assignment is required.');
  if (override?.kind === 'video') return <ProductionVideo asset={override} left />;
  return <PhotoPanel left>
    <ProductionFramedPhoto asset={override} />
  </PhotoPanel>;
};

const PhotoPanel = ({children, left}: {readonly children: ReactNode; readonly left: boolean}) =>
  <div style={{position: 'absolute', left: left ? 140 : 1060, top: 60, width: 720, height: 960,
    borderRadius: 28, overflow: 'hidden', background: FILM.colors.cream,
    boxShadow: `0 0 0 12px ${FILM.colors.cream}, 0 18px 40px rgba(72,70,88,0.08)`}}>
    {children}
  </div>;

const CompletePerformancePhoto = ({asset}: {readonly asset: PerformanceAsset}) =>
  <CanvasImage name={copyText('performance.portrait.054', {value0: asset.original})} src={staticFile(asset.asset)}
    width={720} height={960} fit="contain" style={{display: 'block'}} />;

export const framedHead = (asset: PerformanceAsset) => {
  if (asset.preserveContext) {
    const [w, h] = asset.dimensions;
    const scale = Math.min(720 / w, 960 / h);
    return {headX: 140 + (720 - w * scale) / 2 + asset.head[0] * w * scale,
      headY: 60 + (960 - h * scale) / 2 + asset.head[1] * h * scale};
  }
  const crop = framedCrop(asset);
  return {headX: 140 + (asset.head[0] - crop.x) / crop.w * 720,
    headY: 60 + (asset.head[1] - crop.y) / crop.h * 960};
};

const framedCrop = (asset: PerformanceAsset) => {
  const [w, h] = asset.dimensions;
  const y = Math.max(0, asset.head[1] - 0.12);
  const cropH = Math.min(1 - y, w / (h * 0.75));
  const cropW = cropH * h * 0.75 / w;
  return {x: Math.max(0, Math.min(1 - cropW, asset.face[0] - cropW / 2)), y, w: cropW, h: cropH};
};

const ProductionFramedPhoto = ({asset}: {readonly asset: PerformanceAsset}) => {
  if (asset.preserveContext) return <CompletePerformancePhoto asset={asset} />;
  const crop = framedCrop(asset);
  return <CanvasImage src={staticFile(asset.asset)} width={720 / crop.w} height={960 / crop.h}
    fit="fill" style={{position: 'absolute', left: -crop.x * 720 / crop.w,
      top: -crop.y * 960 / crop.h}} />;
};

const ProductionVideo = ({asset, left}: {readonly asset: PerformanceAsset; readonly left: boolean}) =>
  <div style={{position: 'absolute', left: left ? 140 : 1060, top: 60, width: 720,
    height: 960, background: FILM.colors.cream, borderRadius: 32, overflow: 'hidden'}}>
    <Video src={staticFile(asset.asset)} muted objectFit="contain"
      playbackRate={asset.playbackRate ?? 1}
      style={{width: 720, height: 960}} />
  </div>;
