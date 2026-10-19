import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

/**
 * Code-only placeholder: replace with a reviewed storyboard and approved media.
 * Private photos are never committed or bundled into the repository.
 */
export const BirthdayPreview: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 24, 530, 590], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const drift = interpolate(frame, [0, 600], [30, -30]);
  return (
    <AbsoluteFill style={{
      background: 'linear-gradient(145deg, #F6F0E7, #DFD1C5)',
      color: '#363738',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Arial, sans-serif',
      textAlign: 'center',
    }}>
      <div style={{opacity, transform: 'translateY(' + drift + 'px)'}}>
        <div style={{fontSize: 35, letterSpacing: 16, marginBottom: 40}}>
          FIRST BIRTHDAY
        </div>
        <div style={{fontSize: 98, fontWeight: 600, letterSpacing: -4}}>
          Our Little Story
        </div>
        <div style={{fontSize: 31, marginTop: 42}}>
          소중한 성장 기록을 준비 중입니다.
        </div>
        <div style={{fontSize: 23, marginTop: 55, opacity: 0.65}}>
          Local-first media pipeline · Remotion preview
        </div>
      </div>
    </AbsoluteFill>
  );
};
