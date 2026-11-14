// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {copyText} from '../copy';
import {Video} from '@remotion/media';
import {CanvasImage, staticFile} from 'remotion';
import {FILM} from '../theme';
import {usePerformanceAsset} from './production-media';

const {colors} = FILM;

type ArchVideoProps = {
  readonly source: 'love' | 'prayer';
  readonly side: 'left' | 'right';
};

/** The inset rectangle fits wholly inside the arch, without a crop or RGB grade. */
export const FaithArchVideo = ({source, side}: ArchVideoProps) => {
  const asset = usePerformanceAsset();
  if (!asset) throw new Error('Performance media assignment is required.');
  const left = side === 'left';
  const width = left ? 700 : 620;
  return <div style={{position: 'absolute', left: left ? 150 : 1180, top: 120,
    width, height: 880, borderRadius: `${width / 2}px ${width / 2}px 36px 36px`,
    backgroundColor: colors.cream, border: `2px solid ${colors.peach}`}}>
    {asset?.kind === 'photo' ? <CanvasImage src={staticFile(asset.asset)}
      width={width - 140} height={680} fit="contain"
      style={{position: 'absolute', left: 70, top: 150}} />
      : <Video name={source === 'love' ? copyText('performance.faith-graphics.036') : copyText('performance.faith-graphics.037')}
        src={staticFile(asset.asset)} muted objectFit="contain"
        playbackRate={asset?.playbackRate ?? 1}
        style={{position: 'absolute', left: 70, top: 150, width: width - 140, height: 680}} />}
  </div>;
};
