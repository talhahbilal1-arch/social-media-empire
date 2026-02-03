import { Composition, Folder } from 'remotion';
import { ProfessionalVideo } from './components/ProfessionalVideo';
import { SlideshowVideo } from './components/SlideshowVideo';
import { BRAND_CONFIG, getBrandIds } from './config/brands';

// Video dimensions for Pinterest/TikTok/Reels (9:16 vertical)
const VERTICAL_WIDTH = 1080;
const VERTICAL_HEIGHT = 1920;
const FPS = 30;
const DURATION_SECONDS = 15; // Optimized 15-second video for Pinterest

// Pexels video URLs - high quality stock footage (kept for legacy ProfessionalVideo)
const PEXELS_VIDEOS = {
  // Kitchen/cooking related for deals brand
  kitchen: 'https://videos.pexels.com/video-files/4252599/4252599-hd_1080_1920_25fps.mp4',
  shopping: 'https://videos.pexels.com/video-files/6962744/6962744-hd_1080_1920_25fps.mp4',
  lifestyle: 'https://videos.pexels.com/video-files/5750737/5750737-uhd_1440_2560_24fps.mp4',

  // Fitness related
  workout: 'https://videos.pexels.com/video-files/4761440/4761440-hd_1080_1920_25fps.mp4',
  fitness: 'https://videos.pexels.com/video-files/4761671/4761671-hd_1080_1920_25fps.mp4',
  gym: 'https://videos.pexels.com/video-files/4761563/4761563-hd_1080_1920_25fps.mp4',
  yoga: 'https://videos.pexels.com/video-files/4536400/4536400-hd_1080_1920_30fps.mp4',

  // Wellness/relaxation for menopause brand
  wellness: 'https://videos.pexels.com/video-files/3327309/3327309-hd_1080_1920_30fps.mp4',
  relaxation: 'https://videos.pexels.com/video-files/4057411/4057411-hd_1080_1920_25fps.mp4',
  nature: 'https://videos.pexels.com/video-files/2098989/2098989-hd_1080_1920_30fps.mp4',
  meditation: 'https://videos.pexels.com/video-files/5239805/5239805-hd_1080_1920_25fps.mp4',
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* ============= SLIDESHOW VIDEOS (Multi-Image with Fade Transitions) ============= */}
      {/* These use the centralized brand configuration and show 4 transitioning images */}
      <Folder name="Slideshow">
        <Composition
          id="Slideshow-DailyDealDarling"
          component={SlideshowVideo}
          durationInFrames={DURATION_SECONDS * FPS}
          fps={FPS}
          width={VERTICAL_WIDTH}
          height={VERTICAL_HEIGHT}
          defaultProps={{
            brand: 'daily_deal_darling',
          }}
        />
        <Composition
          id="Slideshow-FitOver35"
          component={SlideshowVideo}
          durationInFrames={DURATION_SECONDS * FPS}
          fps={FPS}
          width={VERTICAL_WIDTH}
          height={VERTICAL_HEIGHT}
          defaultProps={{
            brand: 'fitnessmadeasy',
          }}
        />
        <Composition
          id="Slideshow-MenopausePlanner"
          component={SlideshowVideo}
          durationInFrames={DURATION_SECONDS * FPS}
          fps={FPS}
          width={VERTICAL_WIDTH}
          height={VERTICAL_HEIGHT}
          defaultProps={{
            brand: 'menopause_planner',
          }}
        />
      </Folder>

      {/* ============= LEGACY: DAILY DEAL DARLING ============= */}
      <Folder name="DailyDealDarling">
        <Composition
          id="DailyDealDarling"
          component={ProfessionalVideo}
          durationInFrames={DURATION_SECONDS * FPS}
          fps={FPS}
          width={VERTICAL_WIDTH}
          height={VERTICAL_HEIGHT}
          defaultProps={{
            brand: 'daily_deal_darling',
            hook: 'This changed everything...',
            title: 'Must-Have Kitchen Gadget!',
            points: [
              'Saves 10 min every morning',
              'Under $25 on Amazon',
              '50,000+ 5-star reviews',
            ],
            cta: 'Link in Bio!',
            theme: {
              primary: '#E54D3E',
              secondary: '#FF6B5B',
              accent: '#FFD93D',
            },
            backgroundVideoUrl: PEXELS_VIDEOS.kitchen,
            backgroundImage: 'assets/images/daily-deal-darling-bg.jpg',
            voiceoverFile: 'assets/audio/daily-deal-darling-voice.mp3',
          }}
        />

        <Composition
          id="DailyDealDarling-Lifestyle"
          component={ProfessionalVideo}
          durationInFrames={DURATION_SECONDS * FPS}
          fps={FPS}
          width={VERTICAL_WIDTH}
          height={VERTICAL_HEIGHT}
          defaultProps={{
            brand: 'daily_deal_darling',
            hook: 'I wish I found this sooner...',
            title: "Today's Best Deal",
            points: [
              '70% OFF right now',
              'Selling out fast',
              'Free Prime shipping',
            ],
            cta: 'Grab the Deal!',
            theme: {
              primary: '#E54D3E',
              secondary: '#FF6B5B',
              accent: '#FFD93D',
            },
            backgroundVideoUrl: PEXELS_VIDEOS.lifestyle,
          }}
        />
      </Folder>

      {/* ============= FITNESS MADE EASY / FITOVER35 ============= */}
      <Folder name="FitnessMadeEasy">
        <Composition
          id="FitnessMadeEasy"
          component={ProfessionalVideo}
          durationInFrames={DURATION_SECONDS * FPS}
          fps={FPS}
          width={VERTICAL_WIDTH}
          height={VERTICAL_HEIGHT}
          defaultProps={{
            brand: 'fitnessmadeasy',
            hook: 'No equipment needed...',
            title: '5-Minute Ab Workout',
            points: [
              'Burns belly fat fast',
              'Perfect for beginners',
              'Do it anywhere',
            ],
            cta: 'Save for Later!',
            theme: {
              primary: '#1DB954',
              secondary: '#1ED760',
              accent: '#4ECDC4',
            },
            backgroundVideoUrl: PEXELS_VIDEOS.workout,
            backgroundImage: 'assets/images/fitness-made-easy-bg.jpg',
            voiceoverFile: 'assets/audio/fitness-made-easy-voice.mp3',
          }}
        />

        <Composition
          id="FitnessMadeEasy-Yoga"
          component={ProfessionalVideo}
          durationInFrames={DURATION_SECONDS * FPS}
          fps={FPS}
          width={VERTICAL_WIDTH}
          height={VERTICAL_HEIGHT}
          defaultProps={{
            brand: 'fitnessmadeasy',
            hook: 'Try this morning stretch...',
            title: 'Wake Up Energized',
            points: [
              'Takes only 5 minutes',
              'Boosts your energy',
              'Feel 10 years younger',
            ],
            cta: 'Follow for More!',
            theme: {
              primary: '#1DB954',
              secondary: '#1ED760',
              accent: '#45B7D1',
            },
            backgroundVideoUrl: PEXELS_VIDEOS.yoga,
          }}
        />

        <Composition
          id="FitnessMadeEasy-Gym"
          component={ProfessionalVideo}
          durationInFrames={DURATION_SECONDS * FPS}
          fps={FPS}
          width={VERTICAL_WIDTH}
          height={VERTICAL_HEIGHT}
          defaultProps={{
            brand: 'fitnessmadeasy',
            hook: 'Over 35? Try this...',
            title: 'Build Muscle After 35',
            points: [
              'Science-backed method',
              'See results in weeks',
              'Safe for any fitness level',
            ],
            cta: 'Get Started!',
            theme: {
              primary: '#1DB954',
              secondary: '#1ED760',
              accent: '#FF6B6B',
            },
            backgroundVideoUrl: PEXELS_VIDEOS.gym,
          }}
        />
      </Folder>

      {/* ============= MENOPAUSE PLANNER ============= */}
      <Folder name="MenopausePlanner">
        <Composition
          id="MenopausePlanner"
          component={ProfessionalVideo}
          durationInFrames={DURATION_SECONDS * FPS}
          fps={FPS}
          width={VERTICAL_WIDTH}
          height={VERTICAL_HEIGHT}
          defaultProps={{
            brand: 'menopause_planner',
            hook: 'I wish I knew this sooner...',
            title: 'Natural Hot Flash Relief',
            points: [
              'Works in 5 minutes',
              'No medications needed',
              'Doctor-approved method',
            ],
            cta: 'Get the Guide!',
            theme: {
              primary: '#9B59B6',
              secondary: '#A855F7',
              accent: '#F472B6',
            },
            backgroundVideoUrl: PEXELS_VIDEOS.wellness,
            backgroundImage: 'assets/images/menopause-planner-bg.jpg',
            voiceoverFile: 'assets/audio/menopause-planner-voice.mp3',
          }}
        />

        <Composition
          id="MenopausePlanner-Sleep"
          component={ProfessionalVideo}
          durationInFrames={DURATION_SECONDS * FPS}
          fps={FPS}
          width={VERTICAL_WIDTH}
          height={VERTICAL_HEIGHT}
          defaultProps={{
            brand: 'menopause_planner',
            hook: "Can't sleep? Try this...",
            title: 'Sleep Better Tonight',
            points: [
              'Natural sleep remedy',
              'No grogginess',
              'Works every time',
            ],
            cta: 'Link in Bio!',
            theme: {
              primary: '#6366F1',
              secondary: '#818CF8',
              accent: '#C4B5FD',
            },
            backgroundVideoUrl: PEXELS_VIDEOS.relaxation,
          }}
        />

        <Composition
          id="MenopausePlanner-Wellness"
          component={ProfessionalVideo}
          durationInFrames={DURATION_SECONDS * FPS}
          fps={FPS}
          width={VERTICAL_WIDTH}
          height={VERTICAL_HEIGHT}
          defaultProps={{
            brand: 'menopause_planner',
            hook: 'This hormone hack...',
            title: 'Balance Your Hormones',
            points: [
              '3 simple daily habits',
              'Feel like yourself again',
              'Science-backed tips',
            ],
            cta: 'Save This!',
            theme: {
              primary: '#9B59B6',
              secondary: '#A855F7',
              accent: '#34D399',
            },
            backgroundVideoUrl: PEXELS_VIDEOS.nature,
          }}
        />
      </Folder>
    </>
  );
};
