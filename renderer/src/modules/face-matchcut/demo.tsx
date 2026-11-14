// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {Composition} from 'remotion';
import {FaceMatchcut} from './FaceMatchcut';
import {getMatchcutDuration} from './timeline';
import type {MatchcutPhoto} from './types';

const tones = ['#DDEBF7', '#E8E0F4', '#F6DED3', '#F5E4E8'] as const;
const geometricPhoto = (index: number): MatchcutPhoto => {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
    <rect width="1920" height="1080" fill="${tones[index % tones.length]}"/>
    <path d="M460 1080 Q490 700 960 730 Q1430 700 1460 1080" fill="${tones[(index + 1) % tones.length]}"/>
    <ellipse cx="960" cy="420" rx="370" ry="390" fill="#FFF8F0" stroke="#75628F" stroke-width="8"/>
    <circle cx="850" cy="430" r="20" fill="#484658"/><circle cx="1070" cy="430" r="20" fill="#484658"/>
    <path d="M875 555 Q960 ${590 + index * 4} 1045 555" stroke="#9A6456" stroke-width="12" fill="none" stroke-linecap="round"/>
    <circle cx="${220 + index * 22}" cy="160" r="35" fill="#FFF8F0"/>
  </svg>`;
  return {id: `geometry-${index + 1}`, asset: 'data:image/svg+xml,' + encodeURIComponent(svg)};
};
export const MATCHCUT_DEMO_PHOTOS = Array.from({length: 12}, (_, i) => geometricPhoto(i));

const Demo = ({rate = 6, reverse = false, guide = true}: Readonly<{
  rate?: number; reverse?: boolean; guide?: boolean}>) => <FaceMatchcut
  photos={MATCHCUT_DEMO_PHOTOS} rate={rate} reverse={reverse} guide={guide}
  resolveAsset={asset => asset} />;

export const MatchcutDemoRoot = () => <Composition id="FaceMatchcutDemo" component={Demo}
  width={1920} height={1080} fps={30} durationInFrames={60}
  defaultProps={{rate: 6, reverse: false, guide: true}}
  calculateMetadata={({props}) => ({durationInFrames:
    getMatchcutDuration(12, typeof props.rate === 'number' ? props.rate : 6, 30)})} />;
