/**
 * Original design directions. These are not copies of any vendor assets.
 * The preview uses abstract media slots and no real photographs.
 */
export type TemplateId = 'cinematic' | 'scrapbook' | 'variety';

export type TemplatePreset = {
  id: TemplateId;
  name: string;
  tagline: string;
  subtitle: string;
  chapter: string;
  caption: string;
  closing: string;
  background: string;
  foreground: string;
  muted: string;
  accent: string;
  secondary: string;
};

export const TEMPLATE_PRESETS: Record<TemplateId, TemplatePreset> = {
  cinematic: {
    id: 'cinematic',
    name: 'CINEMATIC ARCHIVE',
    tagline: 'THE FIRST YEAR',
    subtitle: '우리의 가장 소중한 365일',
    chapter: 'CHAPTER 01',
    caption: '작은 순간들이 모여 하나의 이야기가 되었습니다.',
    closing: 'Our little story continues.',
    background: '#F3EDE4',
    foreground: '#303335',
    muted: '#8D8179',
    accent: '#A26E55',
    secondary: '#E2D2C3',
  },
  scrapbook: {
    id: 'scrapbook',
    name: 'PLAYFUL SCRAPBOOK',
    tagline: 'a little memory book',
    subtitle: '매일 새롭게 피어나는 이야기',
    chapter: 'little moments',
    caption: '웃고, 놀고, 자라고! 오늘도 한 뼘 더.',
    closing: 'so many little moments.',
    background: '#F8F2DE',
    foreground: '#3D4941',
    muted: '#797B68',
    accent: '#D97D68',
    secondary: '#A8C3AB',
  },
  variety: {
    id: 'variety',
    name: 'BRIGHT VARIETY',
    tagline: 'HELLO, WORLD!',
    subtitle: '드디어 등장! 오늘의 주인공',
    chapter: 'TODAY'S HIGHLIGHT',
    caption: '하루하루 레벨 업! 귀여움은 현재 진행형.',
    closing: 'TO BE CONTINUED…',
    background: '#2552A2',
    foreground: '#F9F1D8',
    muted: '#C3D8EE',
    accent: '#F9DC72',
    secondary: '#EE8979',
  },
};

export const DEMO_FPS = 30;
export const DEMO_DURATION_FRAMES = 24 * DEMO_FPS;
