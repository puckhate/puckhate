export function H1({ children }: { children: React.ReactNode }) {
  return (
    <h1 className="font-heading text-heading-pink text-4xl font-black tracking-tight uppercase">
      {children}
    </h1>
  );
}

export function H2({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="font-heading text-heading-blue text-xl font-bold">
      {children}
    </h2>
  );
}
