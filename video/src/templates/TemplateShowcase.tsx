import React from 'react';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  Sequence,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {TEMPLATE_PRESETS, type TemplateId, type TemplatePreset} from './presets';

/** All graphics are original CSS shapes and synthetic labels, never private photos. */
const mediaColors = ['#BCB1A5', '#D5B79F', '#A4B8B0'];

const PhotoSlot: React.FC<{
  index: number;
  style?: React.CSSProperties;
  radius?: number;
}> = ({index, style, radius = 16}) => (
  <div
    style={{
      position: 'relative',
      overflow: 'hidden',
      borderRadius: radius,
      background: 'linear-gradient(135deg, ' + mediaColors[index % 3] + ', #F0E8DA)',
      boxShadow: '0 24px 55px rgba(41, 35, 28, 0.12)',
      ...style,
    }}
  >
    <div
      style={{
        position: 'absolute',
        left: '22%',
        top: '20%',
        width: '56%',
        height: '50%',
        borderRadius: '50%',
        background: 'rgba(255, 255, 255, 0.23)',
      }}
    />
    <div
      style={{
        position: 'absolute',
        left: '12%',
        bottom: '-28%',
        width: '76%',
        height: '66%',
        borderRadius: '50%',
        background: 'rgba(255, 255, 255, 0.18)',
      }}
    />
    <div
      style={{
        position: 'absolute',
        bottom: 28,
        left: 30,
        color: '#393B3C',
        font: '600 20px Arial, sans-serif',
        letterSpacing: 4,
        opacity: 0.65,
      }}
    >
      PHOTO SLOT {String(index + 1).padStart(2, '0')}
    </div>
  </div>
);

const FadeIn: React.FC<{children: React.ReactNode; delay?: number}> = ({
  children,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [delay, delay + 24], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const y = interpolate(frame, [delay, delay + 36], [42, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  return <div style={{opacity, transform: 'translateY(' + y + 'px)'}}>{children}</div>;
};

const Intro: React.FC<{theme: TemplatePreset}> = ({theme}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const zoom = spring({fps, frame, config: {damping: 18, stiffness: 75}});
  const isVariety = theme.id === 'variety';
  return (
    <AbsoluteFill style={{background: theme.background, color: theme.foreground}}>
      <div style={{
        position: 'absolute', width: 640, height: 640,
        right: -180, top: -200, borderRadius: '50%',
        background: theme.secondary, opacity: isVariety ? 0.78 : 0.26,
        transform: 'scale(' + (0.8 + zoom * 0.2) + ')',
      }}/>
      <div style={{
        position: 'absolute', width: 290, height: 290,
        left: 100, bottom: -145, borderRadius: '50%',
        border: '3px solid ' + theme.accent, opacity: 0.38,
      }}/>
      <div style={{position: 'absolute', left: 140, top: 126,
        font: '600 22px Arial, sans-serif', letterSpacing: 10, color: theme.accent}}>
        {theme.name}
      </div>
      <div style={{position: 'absolute', left: 140, top: 366, right: 100}}>
        <FadeIn>
          <div style={{
            fontFamily: isVariety ? 'Arial, sans-serif' : 'Georgia, serif',
            fontWeight: isVariety ? 900 : 400,
            fontSize: isVariety ? 134 : 158,
            letterSpacing: -5,
            lineHeight: 1.15,
          }}>{theme.tagline}</div>
        </FadeIn>
        <FadeIn delay={16}>
          <div style={{
            font: '500 48px Arial, sans-serif', marginTop: 44,
            letterSpacing: -1,
          }}>{theme.subtitle}</div>
        </FadeIn>
      </div>
      <div style={{
        position: 'absolute', right: 140, bottom: 122, fontSize: 22,
        letterSpacing: 8, opacity: 0.65,
      }}>DESIGN STUDY / 01</div>
      <div style={{
        position: 'absolute', left: 140, bottom: 120, height: 2,
        width: 165 + Math.max(frame, 0) * 0.65,
        maxWidth: 370, background: theme.accent, opacity: 0.65,
      }}/>
    </AbsoluteFill>
  );
};

const Memory: React.FC<{theme: TemplatePreset}> = ({theme}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const float = Math.sin(frame / (fps * 1.7)) * 9;
  const scrapbook = theme.id === 'scrapbook';
  const variety = theme.id === 'variety';
  const pop = spring({frame, fps, config: {damping: 15, stiffness: 130}});

  return (
    <AbsoluteFill style={{background: theme.background, color: theme.foreground}}>
      {scrapbook ? (
        <>
          <div style={{position: 'absolute', inset: '60px 80px', borderRadius: 28,
            border: '3px dashed ' + theme.secondary, opacity: 0.8}}/>
          {[0, 1, 2].map((index) => (
            <div key={index} style={{
              position: 'absolute', left: 130 + index * 525,
              top: 220 + (index % 2) * 42,
              width: 450, height: 560,
              padding: 24, paddingBottom: 75,
              background: '#FFFDF7',
              transform: 'translateY(' + (float * (index % 2 === 0 ? 1 : -1)) +
                'px) rotate(' + [-7, 5, -4][index] + 'deg)',
              boxShadow: '0 22px 60px #66584626',
            }}>
              <PhotoSlot index={index} style={{width: '100%', height: '100%'}} radius={2}/>
            </div>
          ))}
        </>
      ) : variety ? (
        <>
          <div style={{position: 'absolute', left: 130, top: 140,
            font: '900 90px Arial, sans-serif', color: theme.accent,
            transform: 'scale(' + (0.86 + 0.14 * pop) + ')'}}>BIG MOMENTS!</div>
          <div style={{position: 'absolute', left: 160, top: 330, width: 940,
            height: 560, transform: 'rotate(-4deg)', border: '15px solid #FFFFFF'}}>
            <PhotoSlot index={1} style={{width: '100%', height: '100%'}} radius={0}/>
          </div>
          <div style={{position: 'absolute', right: 105, top: 260,
            borderRadius: 36, padding: 34, background: theme.accent,
            color: '#243C7E', font: '900 56px Arial, sans-serif',
            transform: 'rotate(8deg) scale(' + (0.85 + 0.15 * pop) + ')'}}>LEVEL UP!</div>
        </>
      ) : (
        <>
          <PhotoSlot index={0} style={{position: 'absolute', left: 120, top: 105,
            width: 1000, height: 835,
            transform: 'scale(' + (1 + frame / 24000) + ')'}}/>
          <div style={{position: 'absolute', right: 140, top: 220, width: 470}}>
            <div style={{font: '600 22px Arial, sans-serif',
              letterSpacing: 10, color: theme.accent}}>{theme.chapter}</div>
            <div style={{font: '400 83px Georgia, serif',
              lineHeight: 1.1, marginTop: 44}}>A year<br/>of wonder.</div>
            <div style={{width: 140, height: 2,
              background: theme.accent, marginTop: 46}}/>
          </div>
        </>
      )}
      <div style={{
        position: 'absolute', left: scrapbook ? 170 : 126,
        bottom: scrapbook ? 75 : 72, right: 100, padding: '18px 30px',
        font: '500 32px Arial, sans-serif',
        display: 'inline-block', width: 'fit-content',
        background: variety ? theme.accent : 'rgba(255,255,255,.75)',
        color: variety ? '#244586' : '#3A4140',
        borderRadius: scrapbook ? 14 : 0,
        transform: 'translateY(' + float + 'px)',
      }}>{theme.caption}</div>
    </AbsoluteFill>
  );
};

const Outro: React.FC<{theme: TemplatePreset}> = ({theme}) => (
  <AbsoluteFill style={{background: theme.background, color: theme.foreground,
    justifyContent: 'center', alignItems: 'center', textAlign: 'center'}}>
    <div style={{position: 'absolute', top: 116, width: 140,
      height: 8, borderRadius: 4, background: theme.accent}}/>
    <FadeIn>
      <div style={{font: '500 120px Georgia, serif', marginBottom: 48}}>
        One year, forever.
      </div>
      <div style={{font: '400 48px Arial, sans-serif'}}>{theme.closing}</div>
      <div style={{font: '600 25px Arial, sans-serif',
        letterSpacing: 10, marginTop: 110, color: theme.accent}}>
        FIRST BIRTHDAY FILM
      </div>
    </FadeIn>
  </AbsoluteFill>
);

export const TemplateShowcase: React.FC<{variant: TemplateId}> = ({variant}) => {
  const theme = TEMPLATE_PRESETS[variant];
  return (
    <AbsoluteFill>
      <Sequence from={0} durationInFrames={150}><Intro theme={theme}/></Sequence>
      <Sequence from={150} durationInFrames={420}><Memory theme={theme}/></Sequence>
      <Sequence from={570} durationInFrames={150}><Outro theme={theme}/></Sequence>
    </AbsoluteFill>
  );
};
