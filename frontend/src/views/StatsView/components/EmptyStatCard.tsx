import clsx from "clsx";
import Skeleton from "react-loading-skeleton";

interface EmptyStatCardProps {
  className?: string;
  loading?: boolean;
}

export default function EmptyStatCard(props: EmptyStatCardProps) {
  const { className, loading = false } = props;

  return (
    <div
      className={clsx(
        "bg-dark-amethyst-950/60 border-border-light flex flex-col rounded-lg border p-6 shadow-xl",
        className,
      )}
    >
      {loading ? (
        <>
          <span className={clsx("font-heading mb-2 grow text-5xl font-bold")}>
            <Skeleton />
          </span>
          <span className="font-heading text-muted text-xs font-bold tracking-widest uppercase">
            <Skeleton />
          </span>
        </>
      ) : (
        <div
          aria-hidden="true"
          className="font-heading text-muted/20 flex h-full grow items-center justify-center text-6xl font-black tracking-tighter"
        >
          PH!
        </div>
      )}
    </div>
  );
}
