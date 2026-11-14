// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {tween} from "../shared/motion";
import {FILM} from "../theme";

const {colors} = FILM;
const stage = {position: "absolute", inset: 0} as const;

/** Painted behind both the lifted lid and the real photographic cutout. */
export const GiftBoxBack = () => <svg width="1920" height="1080"
  viewBox="0 0 1920 1080" aria-hidden style={stage}>
  <ellipse cx="1260" cy="1016" rx="347" ry="22" fill={colors.peachInk} opacity={0.08} />
  <path d="M880 620 L935 568 H1585 L1640 620 V1010 H880Z"
    fill={colors.lavender} stroke={colors.lavenderInk} strokeWidth="3" strokeLinejoin="round" />
  <path d="M880 620 L935 568 H1585 L1640 620Z" fill={colors.lavenderInk} opacity={0.22} />
</svg>;


export const GiftBoxLid = ({frame}: {readonly frame: number}) => {
  const lift = tween(frame, [0, 6], [0, 1]);
  return <svg width="1920" height="1080" viewBox="0 0 1920 1080"
    aria-hidden style={stage}>
    <g transform={`translate(${1260 + lift * 390} ${620 - lift * 285}) rotate(${lift * 54})`}>
      <rect x="-395" y="-58" width="790" height="80" rx="13"
        fill={colors.blue} stroke={colors.blueInk} strokeWidth="3" />
      <path d="M-394 -37 H394" stroke={colors.cream} strokeWidth="4" opacity={0.8} />
      <path d="M-43 -57 H43 V21 H-43Z" fill={colors.lavender} />
      <path d="M0 -60 C-124 -63 -140 -148 -74 -143 C-29 -140 -9 -90 0 -60Z
        M0 -60 C124 -63 140 -148 74 -143 C29 -140 9 -90 0 -60Z"
        fill={colors.rose} stroke={colors.lavenderInk} strokeWidth="3" strokeLinejoin="round" />
      <rect x="-20" y="-81" width="40" height="29" rx="12" fill={colors.lavender} />
    </g>
  </svg>;
};

/** Side walls conceal the photographed bib's clipped edges as the front opens. */
export const GiftBoxFront = ({frame}: {readonly frame: number}) => {
  const lip = tween(frame, [0, 6], [620, 715]);
  return <svg width="1920" height="1080" viewBox="0 0 1920 1080" aria-hidden style={stage}>
    <path d={`M880 620 L1070 ${lip} H1440 L1640 620 V1010 H880Z`}
      fill={colors.peach} stroke={colors.peachInk} strokeWidth="3" strokeLinejoin="round" />
    <path d={`M1218 ${lip + 1} H1302 V1009 H1218Z`} fill={colors.lavender} />
    <path d={`M898 638 L1074 ${lip + 12} H1436 L1622 638`}
      fill="none" stroke={colors.cream} strokeWidth="4" opacity={0.75} />
    <path d="M905 987 H1615" stroke={colors.peachInk} strokeWidth="2" opacity={0.13} />
  </svg>;
};

/** Restrained drawn heart, always behind the original RGB video. */
export const HeartHalo = ({frame}: {readonly frame: number}) => <svg
  width="1920" height="1080" viewBox="0 0 1920 1080" aria-hidden style={stage}>
  <g transform={`translate(492 552) scale(${1 + Math.sin(Math.max(0, frame) * 0.035) * 0.012})`}>
    <path d="M0 411 C-140 304 -426 114 -426 -101 C-426 -324 -163 -375 0 -173
      C163 -375 426 -324 426 -101 C426 114 140 304 0 411Z"
      fill="none" stroke={colors.peachInk} strokeWidth="3" opacity={0.13} />
  </g>
</svg>;

