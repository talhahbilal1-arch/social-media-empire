import React from 'react';
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
  Audio,
  Img,
  staticFile,
} from 'remotion';
import { BRAND_CONFIG, BrandConfig } from '../config/brands';

export interface SlideshowVideoProps {
  brand?: string;
  hook?: string;
  title?: string;
  points?: string[];
  cta?: string;
  images?: string[];
  voiceover?: string;
}

/**
 * Multi-image slideshow video component
 *
 * Structure (15 seconds total at 30fps = 450 frames):
 * - 0-3s (0-90): Hook text with image 1
 * - 3-5.5s (90-165): Title with image 2
 * - 5.5-11.5s (165-345): 3 points (2s each) with images 3-4 alternating
 * - 11.5-15s (345-450): CTA with image 1 (loop back)
 */
export const SlideshowVideo: React.FC<SlideshowVideoProps> = ({
  brand = 'daily_deal_darling',
  hook,
  title,
  points,
  cta,
  images,
  voiceover,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const config = BRAND_CONFIG[brand] || BRAND_CONFIG['daily_deal_darling'];

  // Merge dynamic props with static brand config fallback
  const content = {
    hook: hook || config.content.hook,
    title: title || config.content.title,
    points: (points && points.length > 0) ? points : config.content.points,
    cta: cta || config.content.cta,
  };
  const imageList = (images && images.length > 0) ? images : config.images;
  const voiceoverSrc = voiceover || config.voiceover;

  // Timing configuration (15-second video)
  const HOOK_START = 0;
  const HOOK_DURATION = 3 * fps; // 3 seconds
  const TITLE_START = HOOK_DURATION;
  const TITLE_DURATION = 2.5 * fps; // 2.5 seconds
  const POINTS_START = TITLE_START + TITLE_DURATION;
  const POINT_DURATION = 2 * fps; // 2 seconds each
  const CTA_START = POINTS_START + content.points.length * POINT_DURATION;

  // Image timing: which image to show at each frame
  const getActiveImageIndex = (currentFrame: number): number => {
    if (currentFrame < HOOK_DURATION) return 0; // Image 1 for hook
    if (currentFrame < TITLE_START + TITLE_DURATION) return 1; // Image 2 for title
    if (currentFrame < POINTS_START + POINT_DURATION) return 2; // Image 3 for point 1
    if (currentFrame < POINTS_START + 2 * POINT_DURATION) return 3; // Image 4 for point 2
    if (currentFrame < POINTS_START + 3 * POINT_DURATION) return 2; // Image 3 for point 3
    return 0; // Image 1 for CTA
  };

  const activeImageIndex = getActiveImageIndex(frame);

  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {/* Layer 1: Multi-image slideshow background with fade transitions */}
      <SlideshowBackground
        images={imageList}
        activeIndex={activeImageIndex}
        frame={frame}
        fps={fps}
        durationInFrames={durationInFrames}
      />

      {/* Layer 2: Dark gradient overlay for text readability */}
      <AbsoluteFill>
        <div
          style={{
            width: '100%',
            height: '100%',
            background: `linear-gradient(
              180deg,
              rgba(0,0,0,0.5) 0%,
              rgba(0,0,0,0.2) 30%,
              rgba(0,0,0,0.2) 70%,
              rgba(0,0,0,0.6) 100%
            )`,
          }}
        />
      </AbsoluteFill>

      {/* Layer 3: Animated accent shapes */}
      <AnimatedShapes frame={frame} theme={config.theme} />

      {/* Layer 4: Content sections */}
      <Sequence from={HOOK_START} durationInFrames={HOOK_DURATION}>
        <HookSection hook={content.hook} theme={config.theme} fps={fps} />
      </Sequence>

      <Sequence from={TITLE_START} durationInFrames={TITLE_DURATION}>
        <TitleSection title={content.title} theme={config.theme} fps={fps} />
      </Sequence>

      {content.points.map((point, index) => (
        <Sequence
          key={index}
          from={POINTS_START + index * POINT_DURATION}
          durationInFrames={POINT_DURATION}
        >
          <PointSection
            point={point}
            index={index}
            theme={config.theme}
            fps={fps}
          />
        </Sequence>
      ))}

      <Sequence from={CTA_START}>
        <CTASection cta={content.cta} theme={config.theme} fps={fps} />
      </Sequence>

      {/* Layer 5: Brand watermark */}
      <BrandWatermark brand={config.displayName} theme={config.theme} />

      {/* Layer 6: Progress bar */}
      <ProgressBar frame={frame} durationInFrames={durationInFrames} theme={config.theme} />

      {/* Audio: Voiceover (conditionally rendered — omitted if no audio available) */}
      {voiceoverSrc && (
        <Audio
          src={voiceoverSrc.startsWith('http') ? voiceoverSrc : staticFile(voiceoverSrc)}
          volume={(f) =>
            interpolate(
              f,
              [0, fps * 0.3, durationInFrames - fps * 0.3, durationInFrames],
              [0, 1, 1, 0],
              { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
            )
          }
        />
      )}
    </AbsoluteFill>
  );
};

/**
 * Slideshow background with multiple images and fade transitions
 */
const SlideshowBackground: React.FC<{
  images: string[];
  activeIndex: number;
  frame: number;
  fps: number;
  durationInFrames: number;
}> = ({ images, activeIndex, frame, fps, durationInFrames }) => {
  // Ken Burns parameters for each image (different directions for variety)
  const kenBurnsConfigs = [
    { startScale: 1, endScale: 1.15, startX: 0, endX: -3, startY: 0, endY: -2 },
    { startScale: 1.1, endScale: 1, startX: -2, endX: 2, startY: -1, endY: 1 },
    { startScale: 1, endScale: 1.12, startX: 2, endX: -2, startY: 1, endY: -1 },
    { startScale: 1.08, endScale: 1, startX: -1, endX: 1, startY: -2, endY: 2 },
  ];

  return (
    <AbsoluteFill>
      {images.map((imagePath, index) => {
        const isActive = index === activeIndex;
        const kb = kenBurnsConfigs[index % kenBurnsConfigs.length];

        // Fade transition
        const opacity = interpolate(
          frame,
          [0, fps * 0.3],
          [0, 1],
          { extrapolateRight: 'clamp' }
        );

        // Ken Burns effect
        const scale = interpolate(
          frame,
          [0, durationInFrames],
          [kb.startScale, kb.endScale],
          { extrapolateRight: 'clamp' }
        );
        const translateX = interpolate(
          frame,
          [0, durationInFrames],
          [kb.startX, kb.endX],
          { extrapolateRight: 'clamp' }
        );
        const translateY = interpolate(
          frame,
          [0, durationInFrames],
          [kb.startY, kb.endY],
          { extrapolateRight: 'clamp' }
        );

        return (
          <AbsoluteFill
            key={index}
            style={{
              opacity: isActive ? opacity : 0,
              transition: 'opacity 0.3s ease-in-out',
            }}
          >
            <div
              style={{
                width: '100%',
                height: '100%',
                overflow: 'hidden',
              }}
            >
              <Img
                src={imagePath.startsWith('http') ? imagePath : staticFile(imagePath)}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  transform: `scale(${scale}) translate(${translateX}%, ${translateY}%)`,
                }}
              />
            </div>
          </AbsoluteFill>
        );
      })}
    </AbsoluteFill>
  );
};

/**
 * Animated background shapes for visual interest
 */
const AnimatedShapes: React.FC<{
  frame: number;
  theme: { primary: string; secondary: string; accent: string };
}> = ({ frame, theme }) => {
  const shapes = [
    { size: 350, x: -80, y: -80, speed: 0.3, opacity: 0.12 },
    { size: 280, x: 850, y: 1350, speed: 0.2, opacity: 0.08 },
    { size: 220, x: 750, y: 280, speed: 0.35, opacity: 0.1 },
  ];

  return (
    <AbsoluteFill style={{ overflow: 'hidden' }}>
      {shapes.map((shape, i) => {
        const movement = Math.sin(frame * shape.speed * 0.05) * 40;
        const scale = 1 + Math.sin(frame * shape.speed * 0.03) * 0.08;

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: shape.x,
              top: shape.y + movement,
              width: shape.size,
              height: shape.size,
              borderRadius: '50%',
              background: `radial-gradient(circle, ${theme.accent}${Math.round(shape.opacity * 255).toString(16).padStart(2, '0')} 0%, transparent 70%)`,
              transform: `scale(${scale})`,
              filter: 'blur(35px)',
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/**
 * Karaoke-style word highlighting component
 */
const KaraokeWord: React.FC<{
  word: string;
  isActive: boolean;
  isSpoken: boolean;
  theme: { primary: string; secondary: string; accent: string };
}> = ({ word, isActive, isSpoken, theme }) => {
  const frame = useCurrentFrame();
  const pulseScale = isActive ? 1 + Math.sin(frame * 0.3) * 0.04 : 1;

  return (
    <span
      style={{
        display: 'inline-block',
        marginRight: 12,
        padding: '3px 7px',
        borderRadius: 6,
        transform: `scale(${pulseScale})`,
        backgroundColor: isActive
          ? theme.accent
          : isSpoken
          ? `${theme.primary}70`
          : 'transparent',
        color: isActive || isSpoken ? 'white' : 'rgba(255,255,255,0.6)',
        textShadow: isActive
          ? `0 0 18px ${theme.accent}, 0 2px 8px rgba(0,0,0,0.5)`
          : '0 2px 8px rgba(0,0,0,0.5)',
        transition: 'all 0.08s ease-out',
      }}
    >
      {word}
    </span>
  );
};

/**
 * Hook section with karaoke-style text
 */
const HookSection: React.FC<{
  hook: string;
  theme: { primary: string; secondary: string; accent: string };
  fps: number;
}> = ({ hook, theme, fps }) => {
  const frame = useCurrentFrame();

  const enterProgress = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 100, mass: 0.8 },
  });

  const scale = interpolate(enterProgress, [0, 1], [1.4, 1]);
  const opacity = interpolate(frame, [0, fps * 0.25], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const blur = interpolate(frame, [0, fps * 0.25], [8, 0], {
    extrapolateRight: 'clamp',
  });

  const words = hook.split(' ');
  const startDelay = fps * 0.25;

  const currentWordIndex = Math.floor(
    interpolate(frame, [startDelay, startDelay + fps * 2.3], [0, words.length], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 45,
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          opacity,
          filter: `blur(${blur}px)`,
        }}
      >
        <div
          style={{
            fontSize: 60,
            fontWeight: 900,
            color: 'white',
            textAlign: 'center',
            lineHeight: 1.4,
            letterSpacing: '-0.5px',
            maxWidth: 880,
          }}
        >
          {words.map((word, i) => (
            <KaraokeWord
              key={i}
              word={word}
              isActive={i === currentWordIndex}
              isSpoken={i < currentWordIndex}
              theme={theme}
            />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/**
 * Title section with gradient card and karaoke text
 */
const TitleSection: React.FC<{
  title: string;
  theme: { primary: string; secondary: string; accent: string };
  fps: number;
}> = ({ title, theme, fps }) => {
  const frame = useCurrentFrame();

  const scaleSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 140 },
  });

  const scale = interpolate(scaleSpring, [0, 1], [0.85, 1]);
  const opacity = interpolate(frame, [0, fps * 0.2], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const y = interpolate(scaleSpring, [0, 1], [40, 0]);

  const words = title.split(' ');
  const startDelay = fps * 0.25;

  const currentWordIndex = Math.floor(
    interpolate(frame, [startDelay, startDelay + fps * 1.8], [0, words.length], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 35,
      }}
    >
      <div
        style={{
          transform: `scale(${scale}) translateY(${y}px)`,
          opacity,
        }}
      >
        {/* Accent bar above title */}
        <div
          style={{
            width: interpolate(frame, [0, fps * 0.25], [0, 110], {
              extrapolateRight: 'clamp',
            }),
            height: 5,
            backgroundColor: theme.accent,
            borderRadius: 3,
            margin: '0 auto 18px',
          }}
        />

        {/* Title card */}
        <div
          style={{
            background: `linear-gradient(135deg, ${theme.primary} 0%, ${theme.secondary} 100%)`,
            borderRadius: 22,
            padding: '32px 45px',
            boxShadow: `0 22px 70px rgba(0,0,0,0.4), 0 0 0 2px ${theme.accent}25`,
          }}
        >
          <div
            style={{
              fontSize: 48,
              fontWeight: 800,
              color: 'white',
              textAlign: 'center',
              lineHeight: 1.3,
            }}
          >
            {words.map((word, i) => {
              const isActive = i === currentWordIndex;
              const isSpoken = i < currentWordIndex;
              const pulseScale = isActive ? 1 + Math.sin(frame * 0.3) * 0.04 : 1;

              return (
                <span
                  key={i}
                  style={{
                    display: 'inline-block',
                    marginRight: 10,
                    padding: '2px 5px',
                    borderRadius: 5,
                    transform: `scale(${pulseScale})`,
                    backgroundColor: isActive ? 'rgba(255,255,255,0.28)' : 'transparent',
                    textShadow: isActive
                      ? '0 0 25px white, 0 2px 8px rgba(0,0,0,0.3)'
                      : '0 2px 8px rgba(0,0,0,0.3)',
                    opacity: isSpoken || isActive ? 1 : 0.7,
                  }}
                >
                  {word}
                </span>
              );
            })}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/**
 * Point section with slide-in animation and karaoke text
 */
const PointSection: React.FC<{
  point: string;
  index: number;
  theme: { primary: string; secondary: string; accent: string };
  fps: number;
}> = ({ point, index, theme, fps }) => {
  const frame = useCurrentFrame();

  const slideSpring = spring({
    frame,
    fps,
    config: { damping: 13, stiffness: 115 },
  });

  const slideX = interpolate(slideSpring, [0, 1], [index % 2 === 0 ? -90 : 90, 0]);
  const opacity = interpolate(slideSpring, [0, 1], [0, 1]);

  const numberScale = spring({
    frame: frame - 4,
    fps,
    config: { damping: 8, stiffness: 180 },
  });

  const words = point.split(' ');
  const startDelay = fps * 0.35;

  const currentWordIndex = Math.floor(
    interpolate(frame, [startDelay, startDelay + fps * 1.4], [0, words.length], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  const colors = [
    { bg: '#FF6B6B', text: '#fff' },
    { bg: '#4ECDC4', text: '#fff' },
    { bg: '#45B7D1', text: '#fff' },
  ];
  const color = colors[index % colors.length];

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 35,
      }}
    >
      <div
        style={{
          transform: `translateX(${slideX}px)`,
          opacity,
          display: 'flex',
          alignItems: 'center',
          gap: 22,
          background: 'rgba(255,255,255,0.94)',
          borderRadius: 18,
          padding: '22px 36px',
          boxShadow: '0 18px 55px rgba(0,0,0,0.28)',
          maxWidth: '94%',
          borderLeft: `5px solid ${color.bg}`,
        }}
      >
        {/* Number badge */}
        <div
          style={{
            width: 65,
            height: 65,
            borderRadius: '50%',
            backgroundColor: color.bg,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            flexShrink: 0,
            transform: `scale(${numberScale})`,
            boxShadow: `0 7px 22px ${color.bg}45`,
          }}
        >
          <span
            style={{
              fontSize: 34,
              fontWeight: 900,
              color: color.text,
            }}
          >
            {index + 1}
          </span>
        </div>

        {/* Point text with karaoke */}
        <div
          style={{
            fontSize: 36,
            fontWeight: 700,
            lineHeight: 1.3,
          }}
        >
          {words.map((word, i) => {
            const isActive = i === currentWordIndex;
            const isSpoken = i < currentWordIndex;
            const pulseScale = isActive ? 1.04 : 1;

            return (
              <span
                key={i}
                style={{
                  display: 'inline-block',
                  marginRight: 9,
                  padding: '2px 4px',
                  borderRadius: 4,
                  transform: `scale(${pulseScale})`,
                  backgroundColor: isActive
                    ? color.bg
                    : isSpoken
                    ? `${color.bg}35`
                    : 'transparent',
                  color: isActive ? 'white' : '#1a1a1a',
                  transition: 'all 0.05s ease-out',
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/**
 * CTA section with pulsing button animation
 */
const CTASection: React.FC<{
  cta: string;
  theme: { primary: string; secondary: string; accent: string };
  fps: number;
}> = ({ cta, theme, fps }) => {
  const frame = useCurrentFrame();

  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 10, stiffness: 95 },
  });

  const scale = interpolate(enterSpring, [0, 1], [0.55, 1]);
  const opacity = interpolate(enterSpring, [0, 1], [0, 1]);

  const pulsePhase = (frame % (fps * 0.55)) / (fps * 0.55);
  const glowSize = 18 + Math.sin(pulsePhase * Math.PI * 2) * 12;
  const buttonScale = 1 + Math.sin(pulsePhase * Math.PI * 2) * 0.025;

  const arrowY = interpolate(frame % fps, [0, fps / 2, fps], [0, -12, 0]);
  const arrowOpacity = interpolate(frame % fps, [0, fps / 2, fps], [0.6, 1, 0.6]);

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 35,
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          opacity,
          textAlign: 'center',
        }}
      >
        {/* CTA Button */}
        <div
          style={{
            background: `linear-gradient(135deg, ${theme.accent} 0%, ${theme.primary} 100%)`,
            borderRadius: 100,
            padding: '32px 65px',
            transform: `scale(${buttonScale})`,
            boxShadow: `0 0 ${glowSize}px ${theme.accent}75, 0 18px 45px rgba(0,0,0,0.28)`,
            border: '2.5px solid rgba(255,255,255,0.28)',
          }}
        >
          <div
            style={{
              fontSize: 44,
              fontWeight: 800,
              color: 'white',
              textShadow: '0 2px 8px rgba(0,0,0,0.3)',
              letterSpacing: '0.5px',
            }}
          >
            {cta}
          </div>
        </div>

        {/* Animated arrow */}
        <div
          style={{
            marginTop: 28,
            fontSize: 55,
            opacity: arrowOpacity,
            transform: `translateY(${arrowY}px)`,
          }}
        >
          <span role="img" aria-label="point down">
            {'\u{1F447}'}
          </span>
        </div>

        {/* Save prompt */}
        <div
          style={{
            marginTop: 12,
            fontSize: 26,
            fontWeight: 600,
            color: 'rgba(255,255,255,0.88)',
            textShadow: '0 2px 8px rgba(0,0,0,0.5)',
          }}
        >
          Save this for later!
        </div>
      </div>
    </AbsoluteFill>
  );
};

/**
 * Brand watermark
 */
const BrandWatermark: React.FC<{
  brand: string;
  theme: { primary: string; secondary: string; accent: string };
}> = ({ brand, theme }) => {
  return (
    <div
      style={{
        position: 'absolute',
        bottom: 95,
        left: 0,
        right: 0,
        display: 'flex',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          background: 'rgba(0,0,0,0.48)',
          backdropFilter: 'blur(8px)',
          padding: '9px 22px',
          borderRadius: 28,
          border: `1px solid ${theme.accent}35`,
        }}
      >
        <span
          style={{
            fontSize: 20,
            fontWeight: 600,
            color: 'white',
            letterSpacing: '0.4px',
          }}
        >
          @{brand}
        </span>
      </div>
    </div>
  );
};

/**
 * Progress bar at bottom
 */
const ProgressBar: React.FC<{
  frame: number;
  durationInFrames: number;
  theme: { primary: string; secondary: string; accent: string };
}> = ({ frame, durationInFrames, theme }) => {
  const progress = (frame / durationInFrames) * 100;

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: 5,
        background: 'rgba(255,255,255,0.18)',
      }}
    >
      <div
        style={{
          width: `${progress}%`,
          height: '100%',
          background: `linear-gradient(90deg, ${theme.accent}, ${theme.primary})`,
          boxShadow: `0 0 18px ${theme.accent}`,
        }}
      />
    </div>
  );
};

export default SlideshowVideo;
