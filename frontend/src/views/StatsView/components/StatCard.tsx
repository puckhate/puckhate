import clsx from "clsx";
import Skeleton from "react-loading-skeleton";

interface StatCardProps {
  title: string;
  value: string;
  className?: string;
  valueVariant?: "blue" | "pink";
  loading?: boolean;
}

export default function StatCard(props: StatCardProps) {
  const {
    title,
    value,
    className,
    valueVariant = "blue",
    loading = false,
  } = props;

  return (
    <div
      className={clsx(
        "bg-dark-amethyst-950/60 border-border-light flex flex-col rounded-lg border p-6 shadow-xl",
        className,
      )}
    >
      <span
        className={clsx("font-heading mb-2 grow text-5xl font-bold", {
          "text-heading-blue": valueVariant === "blue",
          "text-heading-pink": valueVariant === "pink",
        })}
      >
        {loading ? <Skeleton /> : value}
      </span>
      <span className="font-heading text-muted text-xs font-bold tracking-widest uppercase">
        {loading ? <Skeleton /> : title}
      </span>
    </div>
  );
}
