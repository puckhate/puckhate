import { formatAsCurrency, formatAsNumber } from "@utils/text";

export interface RaisedCardProps {
  raised: number;
  donors: number;
  goals: number;
}

export default function RaisedCard({ raised, donors, goals }: RaisedCardProps) {
  return (
    <div className="border-border-light bg-dark-amethyst-950 flex w-full flex-col justify-center rounded-3xl border p-10 px-11 shadow-xl lg:w-1/2">
      <div className="mb-4 flex items-center gap-2.5">
        <span className="relative flex size-4">
          <span className="bg-heading-pink absolute inline-flex h-full w-full animate-ping rounded-full opacity-75" />
          <span className="bg-heading-pink relative inline-flex size-4 rounded-full" />
        </span>
        <span className="font-heading text-muted text-sm font-bold tracking-widest uppercase">
          Raised In Protest
        </span>
      </div>

      {/* Total raised */}
      <div className="font-heading text-heading-blue leading-tightest text-5xl font-black tracking-tight tabular-nums [text-shadow:0_0_30px_rgb(54_196_252/0.4)] md:text-7xl">
        {formatAsCurrency(raised)}
      </div>

      <div className="mt-7 flex gap-10 border-t border-white/10 pt-6">
        {/* Donors count */}
        <div>
          <div className="font-heading text-3xl font-black tabular-nums">
            {formatAsNumber(donors)}
          </div>
          <div className="font-heading text-muted mt-1 text-xs font-bold tracking-wider uppercase">
            Donors
          </div>
        </div>

        {/* Goals count */}
        <div>
          <div className="font-heading text-heading-pink text-3xl font-black tabular-nums">
            {formatAsNumber(goals)}
          </div>
          <div className="font-heading text-muted mt-1 text-xs font-bold tracking-wider uppercase">
            Goals Answered
          </div>
        </div>
      </div>
    </div>
  );
}
