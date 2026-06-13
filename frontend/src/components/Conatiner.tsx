import cn from "@utils/classNames";

interface ContainerProps {
  className?: string;
}

export default function Container(
  props: React.PropsWithChildren<ContainerProps>,
): React.ReactNode {
  const { className, children } = props;
  return (
    <div
      className={cn("mx-auto w-full max-w-6xl flex-1 px-6 py-10", className)}
    >
      {children}
    </div>
  );
}
