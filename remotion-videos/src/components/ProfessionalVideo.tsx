import React, { useState } from 'react';
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
  Easing,
  Video,
  Audio,
  Img,
  staticFile,
  delayRender,
  continueRender,
} from 'remotion';

export type ProfessionalVideoProps = {
  brand: string;
  hook: string;
  title: string;
  points: string[];
  cta: string;
  theme: {
    primary: string;
    secondary: string;
    accent: string;
  };
  backgroundVideoUrl: string;
  musicFile?: string;
  voiceoverFile?: string;
  localBackgroundVideo?: string;
  backgroundImage?: string; // Static image with Ken Burns effect
};

// Main Professional Video Component
export const ProfessionalVideo: React.FC<ProfessionalVideoProps> = ({
  brand,
  hook,
  title,
  points,
  cta,
  theme,
  backgroundVideoUrl,
  musicFile,
  voiceoverFile,
  localBackgroundVideo,
  backgroundImage,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Timing configuration (optimized for 15-second video at 30fps = 450 frames)
  const HOOK_START = 0;
  const HOOK_DURATION = 3 * fps; // 3 seconds - grab attention
  const TITLE_START = HOOK_DURATION;
  const TITLE_DURATION = 2.5 * fps; // 2.5 seconds
  const POINTS_START = TITLE_START + TITLE_DURATION;
  const POINT_DURATION = 2 * fps; // 2 seconds each
  const CTA_START = POINTS_START + points.length * POINT_DURATION;

  // Background video opacity - always visible
  const bgOpacity = interpolate(frame, [0, fps * 0.5], [0.3, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {/* Layer 1: Background - Image with Ken Burns, video, or animated gradient */}
      <AbsoluteFill style={{ opacity: bgOpacity }}>
        {backgroundImage ? (
          <KenBurnsImage
            src={staticFile(backgroundImage)}
            frame={frame}
            durationInFrames={durationInFrames}
          />
        ) : localBackgroundVideo ? (
          <Video
            src={staticFile(localBackgroundVideo)}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
          />
        ) : (
          <AnimatedGradientBackground frame={frame} fps={fps} theme={theme} />
        )}
      </AbsoluteFill>

      {/* Layer 2: Dark gradient overlay for text readability */}
      <AbsoluteFill>
        <div
          style={{
            width: '100%',
            height: '100%',
            background: `linear-gradient(
              180deg,
              rgba(0,0,0,0.6) 0%,
              rgba(0,0,0,0.3) 30%,
              rgba(0,0,0,0.3) 70%,
              rgba(0,0,0,0.7) 100%
            )`,
          }}
        />
      </AbsoluteFill>

      {/* Layer 3: Animated accent shapes */}
      <AnimatedShapes frame={frame} theme={theme} fps={fps} />

      {/* Layer 4: Content sections */}
      <Sequence from={HOOK_START} durationInFrames={HOOK_DURATION}>
        <HookSection hook={hook} theme={theme} fps={fps} />
      </Sequence>

      <Sequence from={TITLE_START} durationInFrames={TITLE_DURATION}>
        <TitleSection title={title} theme={theme} fps={fps} />
      </Sequence>

      {points.map((point, index) => (
        <Sequence
          key={index}
          from={POINTS_START + index * POINT_DURATION}
          durationInFrames={POINT_DURATION}
        >
          <PointSection
            point={point}
            index={index}
            theme={theme}
            fps={fps}
          />
        </Sequence>
      ))}

      <Sequence from={CTA_START}>
        <CTASection cta={cta} theme={theme} fps={fps} />
      </Sequence>

      {/* Layer 5: Brand watermark - always visible */}
      <BrandWatermark brand={brand} theme={theme} />

      {/* Layer 6: Progress indicator */}
      <ProgressBar frame={frame} durationInFrames={durationInFrames} theme={theme} />

      {/* Voiceover audio track */}
      {voiceoverFile && (
        <Audio
          src={staticFile(voiceoverFile)}
          volume={(f) =>
            interpolate(
              f,
              [0, fps * 0.5, durationInFrames - fps * 0.5, durationInFrames],
              [0, 1, 1, 0],
              { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
            )
          }
        />
      )}

      {/* Background music track */}
      {musicFile && (
        <Audio
          src={staticFile(musicFile)}
          volume={(f) =>
            interpolate(
              f,
              [0, fps, durationInFrames - fps, durationInFrames],
              [0, 0.15, 0.15, 0],
              { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
            )
          }
        />
      )}
    </AbsoluteFill>
  );
};

// Ken Burns effect for static images (slow zoom and pan)
const KenBurnsImage: React.FC<{
  src: string;
  frame: number;
  durationInFrames: number;
}> = ({ src, frame, durationInFrames }) => {
  // Slow zoom from 100% to 120% over the duration
  const scale = interpolate(frame, [0, durationInFrames], [1, 1.2], {
    extrapolateRight: 'clamp',
  });

  // Subtle pan movement
  const translateX = interpolate(frame, [0, durationInFrames], [0, -5], {
    extrapolateRight: 'clamp',
  });
  const translateY = interpolate(frame, [0, durationInFrames], [0, -3], {
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        overflow: 'hidden',
      }}
    >
      <Img
        src={src}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `scale(${scale}) translate(${translateX}%, ${translateY}%)`,
        }}
      />
    </div>
  );
};

// Beautiful animated gradient background
const AnimatedGradientBackground: React.FC<{
  frame: number;
  fps: number;
  theme: { primary: string; secondary: string; accent: string };
}> = ({ frame, fps, theme }) => {
  // Slowly rotating gradient angle
  const angle = interpolate(frame, [0, fps * 30], [0, 360], {
    extrapolateRight: 'extend',
  });

  // Shifting gradient stops for organic movement
  const shift1 = 30 + Math.sin(frame * 0.02) * 20;
  const shift2 = 60 + Math.cos(frame * 0.015) * 25;
  const shift3 = 90 + Math.sin(frame * 0.025) * 15;

  // Secondary rotating layer
  const angle2 = interpolate(frame, [0, fps * 45], [180, 540], {
    extrapolateRight: 'extend',
  });

  return (
    <AbsoluteFill>
      {/* Base gradient layer */}
      <div
        style={{
          width: '100%',
          height: '100%',
          background: `linear-gradient(${angle}deg,
            ${theme.primary} ${shift1 - 30}%,
            ${theme.secondary} ${shift2}%,
            ${theme.accent}90 ${shift3}%,
            ${theme.primary} ${shift3 + 30}%)`,
        }}
      />
      {/* Overlay gradient for depth */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `radial-gradient(circle at ${50 + Math.sin(frame * 0.01) * 30}% ${50 + Math.cos(frame * 0.015) * 30}%,
            transparent 0%,
            rgba(0,0,0,0.3) 100%)`,
        }}
      />
      {/* Moving light spots */}
      <div
        style={{
          position: 'absolute',
          top: `${30 + Math.sin(frame * 0.02) * 20}%`,
          left: `${20 + Math.cos(frame * 0.025) * 25}%`,
          width: 600,
          height: 600,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${theme.accent}30 0%, transparent 70%)`,
          filter: 'blur(60px)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: `${20 + Math.cos(frame * 0.018) * 15}%`,
          right: `${15 + Math.sin(frame * 0.022) * 20}%`,
          width: 500,
          height: 500,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${theme.secondary}40 0%, transparent 70%)`,
          filter: 'blur(50px)',
        }}
      />
    </AbsoluteFill>
  );
};

// Animated background shapes for visual interest
const AnimatedShapes: React.FC<{
  frame: number;
  theme: { primary: string; secondary: string; accent: string };
  fps: number;
}> = ({ frame, theme, fps }) => {
  const shapes = [
    { size: 400, x: -100, y: -100, speed: 0.3, opacity: 0.15 },
    { size: 300, x: 900, y: 1400, speed: 0.2, opacity: 0.1 },
    { size: 250, x: 800, y: 300, speed: 0.4, opacity: 0.12 },
  ];

  return (
    <AbsoluteFill style={{ overflow: 'hidden' }}>
      {shapes.map((shape, i) => {
        const movement = Math.sin(frame * shape.speed * 0.05) * 50;
        const scale = 1 + Math.sin(frame * shape.speed * 0.03) * 0.1;

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
              filter: 'blur(40px)',
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// Karaoke-style word component with highlight animation
const KaraokeWord: React.FC<{
  word: string;
  isActive: boolean;
  isSpoken: boolean;
  theme: { primary: string; secondary: string; accent: string };
}> = ({ word, isActive, isSpoken, theme }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Pulse animation for active word
  const pulseScale = isActive
    ? 1 + Math.sin(frame * 0.3) * 0.05
    : 1;

  return (
    <span
      style={{
        display: 'inline-block',
        marginRight: 14,
        padding: '4px 8px',
        borderRadius: 8,
        transform: `scale(${pulseScale})`,
        backgroundColor: isActive
          ? theme.accent
          : isSpoken
          ? `${theme.primary}80`
          : 'transparent',
        color: isActive || isSpoken ? 'white' : 'rgba(255,255,255,0.6)',
        textShadow: isActive
          ? `0 0 20px ${theme.accent}, 0 2px 10px rgba(0,0,0,0.5)`
          : '0 2px 10px rgba(0,0,0,0.5)',
        transition: 'all 0.1s ease-out',
      }}
    >
      {word}
    </span>
  );
};

// Hook section - first impression with karaoke-style text
const HookSection: React.FC<{
  hook: string;
  theme: { primary: string; secondary: string; accent: string };
  fps: number;
}> = ({ hook, theme, fps }) => {
  const frame = useCurrentFrame();

  // Dramatic entrance animation
  const enterProgress = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 100, mass: 0.8 },
  });

  const scale = interpolate(enterProgress, [0, 1], [1.5, 1]);
  const opacity = interpolate(frame, [0, fps * 0.3], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const blur = interpolate(frame, [0, fps * 0.3], [10, 0], {
    extrapolateRight: 'clamp',
  });

  // Karaoke-style word timing - each word gets highlighted in sequence
  const words = hook.split(' ');
  const wordDuration = (fps * 2.5) / words.length; // Spread words across 2.5 seconds
  const startDelay = fps * 0.3; // Start after entrance animation

  // Calculate which word is currently active
  const currentWordIndex = Math.floor(
    interpolate(frame, [startDelay, startDelay + fps * 2.5], [0, words.length], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 50,
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
            fontSize: 64,
            fontWeight: 900,
            color: 'white',
            textAlign: 'center',
            lineHeight: 1.4,
            letterSpacing: '-1px',
            maxWidth: 900,
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

// Title section with karaoke-style presentation
const TitleSection: React.FC<{
  title: string;
  theme: { primary: string; secondary: string; accent: string };
  fps: number;
}> = ({ title, theme, fps }) => {
  const frame = useCurrentFrame();

  const scaleSpring = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 150 },
  });

  const scale = interpolate(scaleSpring, [0, 1], [0.8, 1]);
  const opacity = interpolate(frame, [0, fps * 0.2], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const y = interpolate(scaleSpring, [0, 1], [50, 0]);

  // Karaoke-style word timing for title
  const words = title.split(' ');
  const wordDuration = (fps * 2) / words.length;
  const startDelay = fps * 0.3;

  const currentWordIndex = Math.floor(
    interpolate(frame, [startDelay, startDelay + fps * 2], [0, words.length], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 40,
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
            width: interpolate(frame, [0, fps * 0.3], [0, 120], {
              extrapolateRight: 'clamp',
            }),
            height: 6,
            backgroundColor: theme.accent,
            borderRadius: 3,
            margin: '0 auto 20px',
          }}
        />

        {/* Main title card with karaoke text */}
        <div
          style={{
            background: `linear-gradient(135deg, ${theme.primary} 0%, ${theme.secondary} 100%)`,
            borderRadius: 24,
            padding: '35px 50px',
            boxShadow: `0 25px 80px rgba(0,0,0,0.4), 0 0 0 2px ${theme.accent}30`,
          }}
        >
          <div
            style={{
              fontSize: 52,
              fontWeight: 800,
              color: 'white',
              textAlign: 'center',
              lineHeight: 1.3,
            }}
          >
            {words.map((word, i) => {
              const isActive = i === currentWordIndex;
              const isSpoken = i < currentWordIndex;
              const pulseScale = isActive ? 1 + Math.sin(frame * 0.3) * 0.05 : 1;

              return (
                <span
                  key={i}
                  style={{
                    display: 'inline-block',
                    marginRight: 12,
                    padding: '2px 6px',
                    borderRadius: 6,
                    transform: `scale(${pulseScale})`,
                    backgroundColor: isActive
                      ? 'rgba(255,255,255,0.3)'
                      : 'transparent',
                    textShadow: isActive
                      ? `0 0 30px white, 0 2px 10px rgba(0,0,0,0.3)`
                      : '0 2px 10px rgba(0,0,0,0.3)',
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

// Point section with karaoke-style text
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
    config: { damping: 14, stiffness: 120 },
  });

  const slideX = interpolate(slideSpring, [0, 1], [index % 2 === 0 ? -100 : 100, 0]);
  const opacity = interpolate(slideSpring, [0, 1], [0, 1]);

  // Number pop animation
  const numberScale = spring({
    frame: frame - 5,
    fps,
    config: { damping: 8, stiffness: 200 },
  });

  // Karaoke-style word timing
  const words = point.split(' ');
  const startDelay = fps * 0.4; // Start after slide animation
  const wordDuration = (fps * 1.5) / words.length;

  const currentWordIndex = Math.floor(
    interpolate(frame, [startDelay, startDelay + fps * 1.5], [0, words.length], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  const colors = [
    { bg: '#FF6B6B', text: '#fff' },
    { bg: '#4ECDC4', text: '#fff' },
    { bg: '#45B7D1', text: '#fff' },
    { bg: '#96CEB4', text: '#fff' },
    { bg: '#FFEAA7', text: '#333' },
  ];
  const color = colors[index % colors.length];

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 40,
      }}
    >
      <div
        style={{
          transform: `translateX(${slideX}px)`,
          opacity,
          display: 'flex',
          alignItems: 'center',
          gap: 25,
          background: 'rgba(255,255,255,0.95)',
          borderRadius: 20,
          padding: '25px 40px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          maxWidth: '95%',
          borderLeft: `6px solid ${color.bg}`,
        }}
      >
        {/* Animated number badge */}
        <div
          style={{
            width: 70,
            height: 70,
            borderRadius: '50%',
            backgroundColor: color.bg,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            flexShrink: 0,
            transform: `scale(${numberScale})`,
            boxShadow: `0 8px 25px ${color.bg}50`,
          }}
        >
          <span
            style={{
              fontSize: 36,
              fontWeight: 900,
              color: color.text,
            }}
          >
            {index + 1}
          </span>
        </div>

        {/* Point text with karaoke highlighting */}
        <div
          style={{
            fontSize: 38,
            fontWeight: 700,
            lineHeight: 1.3,
          }}
        >
          {words.map((word, i) => {
            const isActive = i === currentWordIndex;
            const isSpoken = i < currentWordIndex;
            const pulseScale = isActive ? 1.05 : 1;

            return (
              <span
                key={i}
                style={{
                  display: 'inline-block',
                  marginRight: 10,
                  padding: '2px 4px',
                  borderRadius: 4,
                  transform: `scale(${pulseScale})`,
                  backgroundColor: isActive
                    ? color.bg
                    : isSpoken
                    ? `${color.bg}40`
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

// CTA section with attention-grabbing animation
const CTASection: React.FC<{
  cta: string;
  theme: { primary: string; secondary: string; accent: string };
  fps: number;
}> = ({ cta, theme, fps }) => {
  const frame = useCurrentFrame();

  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 10, stiffness: 100 },
  });

  const scale = interpolate(enterSpring, [0, 1], [0.5, 1]);
  const opacity = interpolate(enterSpring, [0, 1], [0, 1]);

  // Pulsing glow effect
  const pulsePhase = (frame % (fps * 0.6)) / (fps * 0.6);
  const glowSize = 20 + Math.sin(pulsePhase * Math.PI * 2) * 15;
  const buttonScale = 1 + Math.sin(pulsePhase * Math.PI * 2) * 0.03;

  // Floating arrow animation
  const arrowY = interpolate(frame % fps, [0, fps / 2, fps], [0, -15, 0]);
  const arrowOpacity = interpolate(frame % fps, [0, fps / 2, fps], [0.6, 1, 0.6]);

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 40,
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
            padding: '35px 70px',
            transform: `scale(${buttonScale})`,
            boxShadow: `0 0 ${glowSize}px ${theme.accent}80, 0 20px 50px rgba(0,0,0,0.3)`,
            border: '3px solid rgba(255,255,255,0.3)',
          }}
        >
          <div
            style={{
              fontSize: 46,
              fontWeight: 800,
              color: 'white',
              textShadow: '0 2px 10px rgba(0,0,0,0.3)',
              letterSpacing: '1px',
            }}
          >
            {cta}
          </div>
        </div>

        {/* Animated arrow */}
        <div
          style={{
            marginTop: 30,
            fontSize: 60,
            opacity: arrowOpacity,
            transform: `translateY(${arrowY}px)`,
          }}
        >
          👇
        </div>

        {/* "Save this!" text */}
        <div
          style={{
            marginTop: 15,
            fontSize: 28,
            fontWeight: 600,
            color: 'rgba(255,255,255,0.9)',
            textShadow: '0 2px 10px rgba(0,0,0,0.5)',
          }}
        >
          Save this for later!
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Brand watermark - subtle but visible
const BrandWatermark: React.FC<{
  brand: string;
  theme: { primary: string; secondary: string; accent: string };
}> = ({ brand, theme }) => {
  const brandNames: Record<string, string> = {
    daily_deal_darling: 'DailyDealDarling',
    fitnessmadeasy: 'FitOver35',
    menopause_planner: 'MenopausePlanner',
  };

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 100,
        left: 0,
        right: 0,
        display: 'flex',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          background: 'rgba(0,0,0,0.5)',
          backdropFilter: 'blur(10px)',
          padding: '10px 25px',
          borderRadius: 30,
          border: `1px solid ${theme.accent}40`,
        }}
      >
        <span
          style={{
            fontSize: 22,
            fontWeight: 600,
            color: 'white',
            letterSpacing: '0.5px',
          }}
        >
          @{brandNames[brand] || brand}
        </span>
      </div>
    </div>
  );
};

// Progress bar at bottom
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
        height: 6,
        background: 'rgba(255,255,255,0.2)',
      }}
    >
      <div
        style={{
          width: `${progress}%`,
          height: '100%',
          background: `linear-gradient(90deg, ${theme.accent}, ${theme.primary})`,
          boxShadow: `0 0 20px ${theme.accent}`,
        }}
      />
    </div>
  );
};

export default ProfessionalVideo;
