"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { motion, useAnimationFrame, useMotionValue, useReducedMotion } from "framer-motion";

import { cn } from "@/lib/utils";

/**
 * Founding team marquee, modelled on the reference recording: a slow,
 * endless horizontal band of slightly tilted member cards. Hovering (or
 * focusing) a card pauses the band, straightens the card, lifts it with a
 * brand-green offset panel behind it, and reveals the role line. Touch and
 * small screens get the same cards in a snap-scroll carousel; reduced-motion
 * users get a static row.
 *
 * Team portraits live in `frontend/public/team` and are mapped explicitly
 * below so the order and identity of each card remain unambiguous.
 */

export interface FoundingTeamMember {
  name: string;
  designation: string;
  responsibilities: string[];
  /** Public path of the portrait, e.g. "/team/ali-raza.png". */
  photoSrc: string;
  linkedinUrl: string;
}

export const FOUNDING_TEAM: FoundingTeamMember[] = [
  {
    name: "Ali Raza",
    designation: "Founder & CEO",
    responsibilities: [
      "Product Vision & Strategy",
      "Platform Development",
      "Product Architecture & Technical Decisions",
      "Leadership & Overall Project Direction",
    ],
    photoSrc: "/team/ali-raza.png",
    linkedinUrl: "https://www.linkedin.com/in/ali-raza-py",
  },
  {
    name: "Shabbar Raza",
    designation: "Co-Founder",
    responsibilities: [
      "Social Media Management",
      "Community Building",
      "Brand Communication",
      "Content & Outreach",
    ],
    photoSrc: "/team/shabbar-raza.png",
    linkedinUrl: "https://www.linkedin.com/in/syed-muhammad-shabbar-raza-611355400",
  },
  {
    name: "Abdullah",
    designation: "Co-Founder & CTO",
    responsibilities: [
      "Technical Collaboration",
      "Backend Development",
      "Engineering & Technical Implementation",
      "Infrastructure and Development Coordination",
    ],
    photoSrc: "/team/abdullah.png",
    linkedinUrl: "https://www.linkedin.com/in/m-abdullah-hussain-6b179739b",
  },
];

/* Marquee tuning: px per second at full speed, and the hover-straighten tilt. */
const MARQUEE_SPEED = 38;
const TILT_DEGREES = 2.4;
const CARD_WIDTH = "w-[264px] sm:w-[280px]";
/* Copies of the member set rendered side by side; 4 x 3 x ~300px covers any
   realistic viewport with room to loop seamlessly. */
const LOOP_COPIES = 4;

function subscribeCompact(onChange: () => void) {
  const mq = window.matchMedia("(max-width: 767px)");
  mq.addEventListener("change", onChange);
  return () => mq.removeEventListener("change", onChange);
}

function useIsCompact() {
  /* External store over matchMedia: no setState-in-effect cascade, and the
     server snapshot renders the desktop shape before hydration settles. */
  return useSyncExternalStore(
    subscribeCompact,
    () => window.matchMedia("(max-width: 767px)").matches,
    () => false,
  );
}

function TeamCard({
  member,
  index,
  interactive,
  onEnter,
  onLeave,
}: {
  member: FoundingTeamMember;
  index: number;
  /** Marquee cards react to hover/focus; carousel cards rely on touch-active only. */
  interactive: boolean;
  onEnter?: () => void;
  onLeave?: () => void;
}) {
  const tilt = index % 2 === 0 ? -TILT_DEGREES : TILT_DEGREES;

  return (
    <motion.article
      tabIndex={0}
      aria-label={`${member.name}, ${member.designation}`}
      onHoverStart={onEnter}
      onHoverEnd={onLeave}
      onFocus={onEnter}
      onBlur={onLeave}
      whileHover={interactive ? "lifted" : undefined}
      whileFocus={interactive ? "lifted" : undefined}
      initial={{ rotate: tilt, y: 0, scale: 1 }}
      animate="rest"
      variants={{ rest: { rotate: tilt, y: 0, scale: 1 }, lifted: { rotate: 0, y: -10, scale: 1.03 } }}
      transition={{ type: "spring", stiffness: 260, damping: 22, mass: 0.6 }}
      className={cn(
        "group relative shrink-0 outline-none",
        CARD_WIDTH
      )}
      style={{ perspective: "var(--perspective-card)" }}
    >
      {/* Brand-green backing panel — slides out from behind the card on hover. */}
      <motion.div
        aria-hidden="true"
        className="absolute -inset-1 rounded-[20px] bg-cta"
        variants={{ rest: { x: 0, y: 0, opacity: 0 }, lifted: { x: -10, y: 8, opacity: 1 } }}
        transition={{ type: "spring", stiffness: 260, damping: 22, mass: 0.6 }}
      />

      <div className="relative flex h-full flex-col overflow-hidden rounded-[16px] border border-white/10 bg-forest-panel shadow-[0_18px_40px_-18px_rgba(0,0,0,0.55)] transition-shadow duration-300 group-focus-visible:ring-2 group-focus-visible:ring-mint group-hover:shadow-[0_28px_56px_-20px_rgba(0,0,0,0.65)] dark:border-white/10 dark">
        {/* Portrait */}
        <div className="relative h-[258px] shrink-0 overflow-hidden bg-forest-chip-bg">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={member.photoSrc}
            alt={`Portrait of ${member.name}`}
            className={cn(
              "h-full w-full object-top transition-[filter] duration-500 group-hover:grayscale-0 group-focus-visible:grayscale-0 [filter:grayscale(0.35)_contrast(1.02)]",
              member.name === "Ali Raza" ? "object-contain bg-white" : "object-cover",
            )}
          />
          {/* Soft fade into the text block, mirroring the reference treatment. */}
          <div aria-hidden="true" className="pointer-events-none absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-white via-white/80 to-transparent dark:from-forest-panel dark:via-forest-panel/80" />
        </div>

        <div className="relative z-10 flex min-h-[310px] flex-1 flex-col bg-forest-panel px-5 pb-6 pt-4">
          <p className="tech-label flex items-center gap-2 text-forest-muted dark:text-forest-on-deep-soft">
            <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-cta" />
            {member.designation}
          </p>
          <h3 className="mt-2.5 font-display text-[1.35rem] font-semibold leading-tight tracking-tight text-forest-ink dark:text-slate-100">
            {member.name}
          </h3>
          <p className="mt-3 text-xs font-semibold uppercase tracking-[0.14em] text-forest-muted dark:text-forest-on-deep-soft">Responsibilities</p>
          <ul className="mt-2 space-y-1.5 text-sm leading-relaxed text-forest-muted transition-colors duration-300 group-hover:text-forest-ink/80 group-focus-visible:text-forest-ink/80 dark:text-slate-300 dark:group-hover:text-slate-100 dark:group-focus-visible:text-slate-100">
            {member.responsibilities.map((responsibility) => (
              <li key={responsibility} className="flex gap-2">
                <span aria-hidden="true" className="mt-[0.55rem] h-1 w-1 shrink-0 rounded-full bg-cta" />
                <span>{responsibility}</span>
              </li>
            ))}
          </ul>
          <a
            href={member.linkedinUrl}
            target="_blank"
            rel="noreferrer"
            aria-label={`${member.name} on LinkedIn`}
            className="absolute bottom-5 left-5 z-10 inline-flex h-10 w-10 items-center justify-center rounded-[10px] border-2 border-[#0a66c2]/70 bg-white text-[#0a66c2] shadow-[0_6px_18px_rgba(10,102,194,0.16)] transition duration-300 hover:-translate-y-1 hover:scale-105 hover:bg-[#0a66c2] hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0a66c2] motion-safe:animate-[pulse_2.4s_ease-in-out_infinite]"
          >
            <svg aria-hidden="true" viewBox="0 0 24 24" className="h-6 w-6 fill-current">
              <path d="M20.45 20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.34V8.99h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.61 0 4.27 2.38 4.27 5.48v6.27ZM5.32 7.43a2.07 2.07 0 1 1 0-4.14 2.07 2.07 0 0 1 0 4.14ZM3.54 20.45H7.1V8.99H3.54v11.46ZM22.22 0H1.77C.79 0 0 .77 0 1.72v20.56C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.72V1.72C24 .77 23.2 0 22.22 0Z" />
            </svg>
          </a>
        </div>
      </div>
    </motion.article>
  );
}

export function FoundingTeam() {
  const compact = useIsCompact();
  const prefersReducedMotion = useReducedMotion();
  const marquee = !compact && !prefersReducedMotion;

  const offset = useMotionValue(0);
  const setRef = useRef<HTMLDivElement>(null);
  const [setWidth, setSetWidth] = useState(0);
  const paused = useRef(false);
  const speed = useRef(MARQUEE_SPEED);

  /* Measure one copy of the set so the loop wraps exactly at its width. */
  useEffect(() => {
    const el = setRef.current;
    if (!el || !marquee) return;
    const measure = () => setSetWidth(el.getBoundingClientRect().width);
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, [marquee]);

  useAnimationFrame((_, delta) => {
    if (!marquee || setWidth <= 0) return;
    /* Ease speed toward zero while hovered instead of stopping dead. */
    const target = paused.current ? 0 : MARQUEE_SPEED;
    speed.current += (target - speed.current) * Math.min(1, (delta / 1000) * 6);
    const step = speed.current * (delta / 1000);
    /* Manual wrap: keep the offset inside (-setWidth, 0] so the loop is seamless. */
    let next = offset.get() - step;
    if (next <= -setWidth) next += setWidth;
    offset.set(next);
  });

  const pause = () => { paused.current = true; };
  const resume = () => { paused.current = false; };

  return (
    <section id="team" aria-labelledby="team-heading" className="border-y border-forest-border bg-forest-deep py-16 text-white lg:py-20">
      <div className="mx-auto max-w-7xl px-5 sm:px-8 lg:px-10">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="tech-label text-mint-soft">THE PEOPLE BEHIND CODE YAAR</p>
            <h2 id="team-heading" className="mt-3 font-display text-3xl font-semibold tracking-tight sm:text-4xl [font-variation-settings:'SOFT'_0,'WONK'_1]">
              Our founding team
            </h2>
          </div>
          <p className="max-w-sm text-sm leading-6 text-forest-on-deep-soft">
            Three people building Code Yaar from first principle: make serious computer-science education feel reachable.
          </p>
        </div>
      </div>

      {marquee ? (
        <div className="relative mt-12 overflow-hidden" aria-roledescription="carousel" aria-label="Founding team members">
          {/* Edge fades so cards dissolve into the band instead of clipping. */}
          <div aria-hidden="true" className="pointer-events-none absolute inset-y-0 left-0 z-10 w-16 bg-gradient-to-r from-forest-deep to-transparent sm:w-28" />
          <div aria-hidden="true" className="pointer-events-none absolute inset-y-0 right-0 z-10 w-16 bg-gradient-to-l from-forest-deep to-transparent sm:w-28" />
          <motion.div style={{ x: offset }} className="flex w-max py-8">
            {Array.from({ length: LOOP_COPIES }, (_, copy) => (
              <div
                key={copy}
                ref={copy === 0 ? setRef : undefined}
                aria-hidden={copy > 0 || undefined}
                className="flex gap-6 px-3"
              >
                {FOUNDING_TEAM.map((member, i) => (
                  <TeamCard key={member.name} member={member} index={i} interactive onEnter={pause} onLeave={resume} />
                ))}
              </div>
            ))}
          </motion.div>
        </div>
      ) : (
        <div
          className={cn(
            "mt-10",
            compact
              ? "-mx-5 flex snap-x snap-mandatory gap-5 overflow-x-auto px-5 pb-4 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden sm:-mx-8 sm:px-8 lg:-mx-10 lg:px-10"
              : "flex flex-wrap justify-center gap-6"
          )}
        >
          {compact
            ? FOUNDING_TEAM.map((member, i) => (
                <div key={member.name} className="snap-center">
                  <TeamCard member={member} index={i} interactive={false} />
                </div>
              ))
            : FOUNDING_TEAM.map((member, i) => (
                <TeamCard key={member.name} member={member} index={i} interactive onEnter={pause} onLeave={resume} />
              ))}
        </div>
      )}
    </section>
  );
}
