// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {copyText} from '../copy';
import {Video} from '@remotion/media';
import {CanvasImage, staticFile} from 'remotion';
import type {NarrativeAsset} from './edit';
import type {FrameLayout} from './FrameLayout';
import {verseMediaMotion} from './VerseMotion';

const SourcePhoto = ({asset, width, height}: Readonly<{
  asset: NarrativeAsset; width: number; height: number;
}>) => {
  if (!asset.crop) return <CanvasImage src={staticFile(asset.asset)} width={width} height={height} fit="contain" />;
  const [x, y, cropWidth, cropHeight] = asset.crop;
  const [sourceWidth, sourceHeight] = asset.dimensions;
  const scale = Math.min(width / (cropWidth * sourceWidth), height / (cropHeight * sourceHeight));
  return <CanvasImage src={staticFile(asset.asset)} width={sourceWidth * scale}
    height={sourceHeight * scale} fit="fill" style={{position: 'absolute',
      left: -x * sourceWidth * scale, top: -y * sourceHeight * scale}} />;
};

/** No opacity entrance, source zoom or source-duration trim: the enclosing Sequence owns lifetime. */
export const NarrativeMedia = ({asset, layout, frame, duration, songFrame = frame, closing = false}: Readonly<{
  asset: NarrativeAsset; layout: FrameLayout; frame: number; duration: number;
  songFrame?: number; closing?: boolean;
}>) => {
  const {media, radius, mat, inset, backing, foot = 0} = layout;
  const photo = asset.kind === 'photo';
  const motion = verseMediaMotion(layout, frame, duration, songFrame, photo, closing);
  const width = media.width - mat * 2;
  const height = media.height - mat * 2 - foot;
  return <div data-verse-media="whole-frame" style={{position: 'absolute', inset: 0,
    transformOrigin: `${media.x + media.width / 2}px ${media.y + media.height / 2}px`,
    transform: `translate(${motion.x}px, ${motion.y}px) scale(${motion.scale})`}}>
    {backing ? <div aria-hidden="true" style={{position: 'absolute', left: backing.x,
      top: backing.y, width: backing.width, height: backing.height, background: '#FDFBF8',
      border: '1px solid rgba(72,70,88,0.12)'}} /> : null}
    <div data-frame-family={layout.family} aria-label={photo ? copyText('narrative.NarrativeMedia.009') : copyText('narrative.NarrativeMedia.010')}
      style={{position: 'absolute', left: media.x, top: media.y, width: media.width,
        height: media.height, borderRadius: radius, background: '#FFFEFC', padding: mat,
        boxSizing: 'border-box', outline: mat ? '1px solid rgba(72,70,88,0.13)' : undefined}}>
      <div style={{position: 'relative', width, height, overflow: 'hidden',
        borderRadius: Math.max(0, radius - mat), background: '#FFFEFC'}}>
        {asset.kind === 'video' ? <Video src={staticFile(asset.asset)} muted objectFit="contain"
          playbackRate={asset.playbackRate ?? 1} style={{width, height, display: 'block'}} /> :
          <SourcePhoto asset={asset} width={width} height={height} />}
      </div>
      {inset ? <div aria-hidden="true" style={{position: 'absolute', inset,
        border: '1px solid rgba(255,254,252,0.65)', pointerEvents: 'none'}} /> : null}
    </div>
  </div>;
};
