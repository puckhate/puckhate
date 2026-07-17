import { TrophyIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Skeleton from "react-loading-skeleton";

interface DonorCardProps {
  rank?: number;
  name: string;
  amount: string;
  charity: string;
  loading?: boolean;
}

export default function DonorCard(props: DonorCardProps): React.ReactNode {
  const { rank, name, amount, charity, loading = false } = props;

  return (
    <div className="bg-dark-amethyst-950/60 border-border-light flex flex-col rounded-lg border p-6 shadow-xl">
      {/* Donor Name */}
      <div className="flex items-center space-x-2">
        {loading ? (
          <Skeleton width={200} height={24} />
        ) : (
          <>
            <TrophyIcon
              className={clsx("size-6", {
                "text-yellow-500": rank === 1,
                "text-gray-400": rank === 2,
                "text-yellow-800": rank === 3,
              })}
            />
            <span className="font-heading text-2xl font-bold tracking-tighter">
              {name}
            </span>
          </>
        )}
      </div>
      <div className="border-b-muted/20 mb-3 w-full border-b pb-3" />

      {/* Donation Details */}
      {loading ? (
        <Skeleton height={48} className="mb-2" />
      ) : (
        <span
          className={clsx(
            "font-heading animate-ripple from-sky-aqua-100 to-sky-aqua-100 via-sky-aqua-600 mb-2 bg-linear-to-r bg-size-[200%_auto] bg-clip-text text-5xl font-bold text-transparent",
            {
              "delay-[400ms]": rank === 2,
              "delay-[800ms]": rank === 3,
            },
          )}
        >
          {amount}
        </span>
      )}

      <div className="font-heading text-muted space-x-2 text-xs font-bold tracking-widest uppercase">
        {loading ? <Skeleton /> : `Donated to ${charity}`}
      </div>
    </div>
  );
}
