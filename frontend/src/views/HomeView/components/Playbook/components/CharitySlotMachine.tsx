import { useEffect, useState } from "react";

import type { Charity } from "@types";
import cn from "@utils/classNames";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";

const SPIN_DURATION_MS = 500;
const SLOWDOWN_DURATION_MS = 500;
const SPIN_TICK_MS = 45;
const SETTLE_TICK_MS = 150;

interface CharitySlotMachineProps {
  charities: Charity[];
  onSelect?: () => void;
  onSpinComplete?: (winner: Charity) => void;
}

interface ReelState {
  name: string | undefined;
  tick: number;
  delay: number;
}

/**
 * Slot-machine reel that cycles rapidly through charity names, slows to a
 * stop, and settles on a random suggestion.
 *
 * Honors `prefers-reduced-motion`: when set, the reel and glow are skipped
 * entirely and the winning charity is shown as a link immediately.
 */
export default function CharitySlotMachine({
  charities,
  onSelect,
  onSpinComplete,
}: CharitySlotMachineProps): React.ReactNode {
  const reduceMotion = useReducedMotion();
  const [winner] = useState<Charity | undefined>(
    () => charities[Math.floor(Math.random() * charities.length)],
  );
  const [reel, setReel] = useState<ReelState>({
    name: winner?.name,
    tick: 0,
    delay: SPIN_TICK_MS,
  });
  // With reduced motion, render the link straight away with no spin
  const [spinning, setSpinning] = useState<boolean>(!reduceMotion);
  const [glowing, setGlowing] = useState<boolean>(!!reduceMotion);

  /*
   * Mounts in a resting state, start animation if not in reduced motion mode
   */
  useEffect(() => {
    if (spinning || reduceMotion) return undefined;
    const frame = window.requestAnimationFrame(() => setGlowing(true));
    return () => window.cancelAnimationFrame(frame);
  }, [spinning, reduceMotion]);

  /*
   * Handle spin speed and step-down
   */
  useEffect(() => {
    if (reduceMotion) return undefined;
    let timer: number | undefined;
    let index = 0;
    let tick = 0;
    const start = performance.now();
    const step = () => {
      const elapsed = performance.now() - start;
      tick += 1;
      if (elapsed >= SPIN_DURATION_MS + SLOWDOWN_DURATION_MS) {
        // Slide the winner in, then let the last slide finish before
        // swapping the reel for the link.
        setReel({ name: winner?.name, tick, delay: SETTLE_TICK_MS });
        timer = window.setTimeout(() => setSpinning(false), SETTLE_TICK_MS);
        return;
      }
      index = (index + 1) % charities.length;
      // Constant rapid ticks while spinning, then ease toward a stop.
      const slowdown =
        Math.max(0, elapsed - SPIN_DURATION_MS) / SLOWDOWN_DURATION_MS;
      const delay =
        SPIN_TICK_MS + slowdown ** 2 * (SETTLE_TICK_MS - SPIN_TICK_MS);
      setReel({ name: charities[index]?.name, tick, delay });
      timer = window.setTimeout(step, delay);
    };
    step();
    return () => window.clearTimeout(timer);
  }, [charities, winner, reduceMotion]);

  /*
   * Report the settled winner once the reel comes to rest
   * (immediately in reduced-motion mode).
   */
  useEffect(() => {
    if (!spinning && winner !== undefined) onSpinComplete?.(winner);
  }, [spinning, winner, onSpinComplete]);

  const reelClasses =
    "bg-dark-amethyst-950 my-5 block w-full rounded-lg font-heading border p-4 text-2xl";

  return (
    <span role="status" aria-live="polite">
      {!spinning && winner !== undefined && winner.url.length > 0 ? (
        // Static link when spinning completes
        <a
          href={winner.url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={onSelect}
          aria-label={`Donate to ${winner.name} (opens in a new tab)`}
          className={cn(
            reelClasses,
            "hover:text-heading-blue shadow-[0_0_14px] transition-[border,box-shadow] duration-300 ease-in-out",
            glowing
              ? "border-heading-pink shadow-heading-pink/80"
              : "border-border-dark shadow-heading-pink/0",
          )}
        >
          <span className="flex h-16 items-center justify-center">
            <span className="line-clamp-2">{winner.name}</span>
          </span>
        </a>
      ) : (
        // Hide from assistive tech until spinning complete
        <span
          aria-hidden={spinning || undefined}
          className={cn(reelClasses, "border-border-dark")}
        >
          <span className="relative block h-16 overflow-hidden">
            <AnimatePresence mode="popLayout" initial={false}>
              <motion.span
                key={reel.tick}
                initial={{ y: "100%" }}
                animate={{ y: 0 }}
                exit={{ y: "-100%" }}
                transition={{ duration: reel.delay / 1000, ease: "linear" }}
                className="flex h-16 w-full items-center justify-center"
              >
                <span className="line-clamp-2">{reel.name}</span>
              </motion.span>
            </AnimatePresence>
          </span>
        </span>
      )}
    </span>
  );
}
