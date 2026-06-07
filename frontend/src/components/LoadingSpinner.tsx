import { ArrowPathIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";

export default function LoadingSpinner({
  className,
}: {
  className?: string;
}): React.ReactNode {
  return (
    <ArrowPathIcon
      aria-label="Loading"
      className={clsx("size-12 animate-spin", className)}
    />
  );
}
