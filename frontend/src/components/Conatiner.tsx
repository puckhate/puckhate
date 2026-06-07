export default function Container({
  children,
}: {
  children: React.ReactNode;
}): React.ReactNode {
  return (
    <div className="mx-auto w-full max-w-6xl flex-1 px-6 py-10">{children}</div>
  );
}
