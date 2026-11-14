// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {AbsoluteFill, Composition, useCurrentFrame, useVideoConfig} from 'remotion';
import {FILM} from '../theme';
import {ASSET_IDS, ASSET_LABELS, MotionAsset} from './library';
import type {MotionAssetId} from './library';

export const AssetPreview = ({id = 'star'}: {readonly id?: MotionAssetId}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return <AbsoluteFill><MotionAsset id={id} frame={frame * 30 / fps} /></AbsoluteFill>;
};

export const AssetCatalog = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return <AbsoluteFill style={{background: FILM.colors.cream, color: FILM.colors.ink,
    fontFamily: FILM.font, padding: '40px 60px'}}>
    <div style={{fontSize: 36, fontWeight: 800}}>모션 에셋 라이브러리</div>
    <div style={{fontSize: 18, color: FILM.colors.muted, marginTop: 8}}>
      코드로 그린 11종 · 개인 사진과 음원 없이 미리보기</div>
    <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 20, marginTop: 28}}>
      {ASSET_IDS.map(id => <div key={id} style={{position: 'relative', height: 278,
        background: '#FFFFFF99', border: `1px solid ${FILM.colors.lavender}`, borderRadius: 20,
        overflow: 'hidden'}}>
        <div style={{position: 'absolute', left: 8, top: 0, width: 1920, height: 1080,
          transformOrigin: '0 0', transform: 'scale(0.215)'}}>
          <MotionAsset id={id} frame={frame * 30 / fps} />
        </div>
        <div style={{position: 'absolute', bottom: 12, left: 18, fontSize: 22, fontWeight: 600}}>
          {ASSET_LABELS[id]} <span style={{fontSize: 14, color: FILM.colors.muted}}>{id}</span>
        </div>
      </div>)}
    </div>
  </AbsoluteFill>;
};

export const AssetRoot = () => <>
  <Composition id="AssetCatalog" component={AssetCatalog}
    durationInFrames={90} fps={30} width={1920} height={1080} />
  {ASSET_IDS.map(id => <Composition key={id} id={`Asset-${id}`} component={AssetPreview}
    defaultProps={{id}} durationInFrames={90} fps={30} width={1920} height={1080} />)}
</>;
