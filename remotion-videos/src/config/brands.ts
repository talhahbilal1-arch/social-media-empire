/**
 * Centralized Brand Configuration
 * Single source of truth for all brand settings including:
 * - Visual themes and colors
 * - Slideshow images (4 per brand)
 * - Voiceover audio files
 * - Content (hook, title, points, CTA)
 * - Pinterest account credentials
 */

export interface BrandTheme {
  primary: string;
  secondary: string;
  accent: string;
}

export interface BrandContent {
  hook: string;
  title: string;
  points: string[];
  cta: string;
}

export interface PinterestConfig {
  accountId: string;
  boardId: string;
  apiKey: string;
  link: string;
}

export interface BrandConfig {
  id: string;
  displayName: string;
  theme: BrandTheme;
  images: string[];
  fallbackImage?: string;
  voiceover: string;
  content: BrandContent;
  pinterest: PinterestConfig;
}

export const BRAND_CONFIG: Record<string, BrandConfig> = {
  daily_deal_darling: {
    id: 'daily_deal_darling',
    displayName: 'DailyDealDarling',
    theme: {
      primary: '#E54D3E',
      secondary: '#FF6B5B',
      accent: '#FFD93D',
    },
    images: [
      'assets/images/daily-deal-darling/slide1.jpg',
      'assets/images/daily-deal-darling/slide2.jpg',
      'assets/images/daily-deal-darling/slide3.jpg',
      'assets/images/daily-deal-darling/slide4.jpg',
    ],
    fallbackImage: 'assets/images/daily-deal-darling-bg.jpg',
    voiceover: 'assets/audio/daily-deal-darling-voice.mp3',
    content: {
      hook: 'Every woman needs this...',
      title: 'Life-Changing Beauty Find!',
      points: [
        'Makes your skin glow',
        'Under $30 on sale now',
        'TikTok made me buy it',
      ],
      cta: 'Link in Bio!',
    },
    pinterest: {
      accountId: '697ba20193a320156c4220b4',
      boardId: '874683627569021288',
      apiKey: 'sk_191f58baa59a897d5836822d023958b4b08dc50b942c42608f54f35db5e51f26',
      link: 'https://dailydealdarling.com',
    },
  },

  fitnessmadeasy: {
    id: 'fitnessmadeasy',
    displayName: 'FitOver35',
    theme: {
      primary: '#1DB954',
      secondary: '#1ED760',
      accent: '#4ECDC4',
    },
    images: [
      'assets/images/fitnessmadeasy/slide1.jpg',
      'assets/images/fitnessmadeasy/slide2.jpg',
      'assets/images/fitnessmadeasy/slide3.jpg',
      'assets/images/fitnessmadeasy/slide4.jpg',
    ],
    fallbackImage: 'assets/images/fitness-made-easy-bg.jpg',
    voiceover: 'assets/audio/fitness-made-easy-voice.mp3',
    content: {
      hook: 'Over 35? Try this...',
      title: 'Boost Your Metabolism!',
      points: [
        'Works in just 10 minutes',
        'No gym required',
        'Feel stronger every day',
      ],
      cta: 'Save for Later!',
    },
    pinterest: {
      accountId: '697bb4b893a320156c4221ab',
      boardId: '756745612325868912',
      apiKey: 'sk_78b46c6df3c475b75acb864d30343172b1502a2ddb836adcc5c165f5fbc7ee82',
      link: 'https://fitnessmadeasy.com',
    },
  },

  menopause_planner: {
    id: 'menopause_planner',
    displayName: 'MenopausePlanner',
    theme: {
      primary: '#9B59B6',
      secondary: '#A855F7',
      accent: '#F472B6',
    },
    images: [
      'assets/images/menopause-planner/slide1.jpg',
      'assets/images/menopause-planner/slide2.jpg',
      'assets/images/menopause-planner/slide3.jpg',
      'assets/images/menopause-planner/slide4.jpg',
    ],
    fallbackImage: 'assets/images/menopause-planner-bg.jpg',
    voiceover: 'assets/audio/menopause-planner-voice.mp3',
    content: {
      hook: 'Struggling with menopause?',
      title: 'Sleep Better Tonight!',
      points: [
        'Natural remedies that work',
        'No more night sweats',
        'Wake up refreshed',
      ],
      cta: 'Get the Guide!',
    },
    pinterest: {
      accountId: '697c329393a320156c422e6d',
      boardId: '1076993767079887530',
      apiKey: 'sk_37d9439119d55bdaab7316707b2dda03ad616752ae9b4ee720764c944dac39cb',
      link: 'https://www.etsy.com/listing/4435219468/menopause-wellness-planner-bundle',
    },
  },
};

// Helper to get all brand IDs
export const getBrandIds = (): string[] => Object.keys(BRAND_CONFIG);

// Helper to get brand config by ID
export const getBrandConfig = (brandId: string): BrandConfig | undefined =>
  BRAND_CONFIG[brandId];

// Build voiceover script from content
export const buildVoiceoverScript = (brandId: string): string => {
  const config = BRAND_CONFIG[brandId];
  if (!config) return '';

  const { hook, title, points, cta } = config.content;
  let script = `${hook} ${title}. `;
  points.forEach((point) => {
    script += `${point}. `;
  });
  script += cta;
  return script;
};

// Build Pinterest description from content
export const buildPinterestDescription = (brandId: string): string => {
  const config = BRAND_CONFIG[brandId];
  if (!config) return '';

  const { title, points, cta } = config.content;

  const hashtags: Record<string, string> = {
    daily_deal_darling:
      '#amazonfinds #kitchengadgets #morningroutine #deals #dailydealdarling',
    fitnessmadeasy:
      '#fitness #workout #abs #homeworkout #fitover35',
    menopause_planner:
      '#menopause #wellness #hotflashes #womenshealth #naturalremedy',
  };

  return `${title} - Watch with Sound!

${config.content.hook} ${points.join('. ')}!

${cta}

${hashtags[brandId] || ''}`;
};

export default BRAND_CONFIG;
