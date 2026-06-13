import { ArrowPathIcon } from "@heroicons/react/24/outline";
import cn from "@utils/classNames";

export default function LoadingSpinner({
  className,
}: {
  className?: string;
}): React.ReactNode {
  return (
    <ArrowPathIcon
      aria-label="Loading"
      className={cn("size-12 animate-spin", className)}
    />
  );
}
