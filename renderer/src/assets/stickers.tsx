// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {FILM} from '../theme';
import {tween} from '../shared/motion';

export const STICKER_KINDS = ['moon', 'planet', 'shooting-star', 'cloud', 'castle', 'balloons'] as const;
export type StickerKind = typeof STICKER_KINDS[number];
export type StickerProps = Readonly<{kind: StickerKind; frame: number; x?: number;
  y?: number; size?: number; color?: string; fill?: string}>;

const Moon = () => <path d="M224 44 A118 118 0 1 0 272 234 A111 111 0 0 1 224 44Z" />;

const Planet = ({frame}: {readonly frame: number}) => <>
  <circle cx="160" cy="160" r="76" />
  <path d="M94 119 Q147 96 206 139 M88 152 Q147 126 222 168 M102 190 Q153 167 222 193"
    fill="none" opacity="0.35" />
  <ellipse cx="160" cy="168" rx="137" ry="35" fill="none"
    transform={`rotate(${-26 + tween(frame, [0, 90], [-3, 3])} 160 160)`} />
  <circle cx="263" cy="64" r="7" stroke="none" />
</>;

const ShootingStar = ({frame}: {readonly frame: number}) => {
  const travel = tween(frame, [0, 60], [-48, 40]);
  return <g transform={`translate(${travel} ${-travel * 0.32})`}>
    <path d="M30 216 Q91 186 179 163 M47 241 Q111 204 184 184 M52 186 Q103 168 174 146"
      fill="none" opacity="0.5" />
    <path d="M220 84 L233 132 L281 139 L243 168 L251 215 L211 188 L167 211 L180 165 L146 133 L195 129Z" />
  </g>;
};

const Cloud = () => <>
  <path d="M77 226 H244 C294 226 307 161 264 143 C258 81 175 62 139 112 C99 99 62 129 64 167 C21 180 35 226 77 226Z" />
  <path d="M96 263 H139 M173 263 H224" fill="none" opacity="0.35" />
</>;

const Castle = () => <>
  <path d="M51 264 V132 H100 V264 M220 264 V132 H269 V264 M100 264 V170 H220 V264Z" />
  <path d="M44 132 L76 80 L108 132Z M212 132 L244 80 L276 132Z M118 170 V138 H139 V157 H155 V138 H177 V157 H194 V138 H212 V170Z" />
  <path d="M139 264 V222 A21 21 0 0 1 181 222 V264 M76 102 V47 L112 59 L76 72 M244 102 V47 L280 59 L244 72"
    fill="none" />
  <path d="M71 167 V185 M249 167 V185" fill="none" />
</>;

const Balloons = ({frame}: {readonly frame: number}) => {
  const rise = tween(frame, [0, 60], [16, 0]);
  return <g transform={`translate(0 ${rise})`}>
    <path d="M101 169 Q83 231 161 284 M218 172 Q239 233 161 284 M158 142 Q147 211 161 284"
      fill="none" opacity="0.65" />
    <ellipse cx="98" cy="119" rx="45" ry="58" transform="rotate(-14 98 119)" />
    <ellipse cx="219" cy="122" rx="44" ry="58" transform="rotate(14 219 122)" />
    <ellipse cx="159" cy="88" rx="46" ry="61" />
    <path d="M87 93 Q88 78 99 74 M148 61 Q150 46 161 42 M208 96 Q208 82 220 78"
      fill="none" stroke={FILM.colors.cream} strokeWidth="5" />
  </g>;
};

/** One entrance and one continuous drift; no implicit loop or random state. */
export const CelestialSticker = ({kind, frame, x = 960, y = 540, size = 640,
  color = FILM.colors.lavenderInk, fill = FILM.colors.lavender}: StickerProps) => {
  if (frame < 0 || size <= 0) return null;
  const open = tween(frame, [0, 18], [0, 1]);
  return <svg aria-hidden width={size} height={size} viewBox="0 0 320 320"
    style={{position: 'absolute', left: x - size / 2, top: y - size / 2,
      overflow: 'visible', pointerEvents: 'none', opacity: open,
      transform: `translateY(${(1 - open) * 20}px) scale(${0.88 + open * 0.12})`}}
    fill={fill} stroke={color} strokeWidth="3" strokeLinejoin="round" strokeLinecap="round">
    {kind === 'moon' ? <Moon /> : kind === 'planet' ? <Planet frame={frame} /> :
      kind === 'shooting-star' ? <ShootingStar frame={frame} /> : kind === 'cloud' ? <Cloud /> :
        kind === 'castle' ? <Castle /> : <Balloons frame={frame} />}
  </svg>;
};
