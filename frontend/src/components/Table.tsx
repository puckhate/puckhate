import clsx from "clsx";

type Align = "left" | "right" | "center";

const alignClass: Record<Align, string> = {
  left: "text-left",
  right: "text-right",
  center: "text-center",
};

/**
 * Scroll-safe wrapper around a semantic <table>. Compose with TableHead,
 * TableBody, TableRow, TableHeaderCell, and TableCell.
 */
export function Table({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}): React.ReactNode {
  return (
    <div className="border-border-dark overflow-x-auto rounded-xl border">
      <table className={clsx("w-full border-collapse text-sm", className)}>
        {children}
      </table>
    </div>
  );
}

/** Table head (<thead>) */
export function TableHead({
  children,
}: {
  children: React.ReactNode;
}): React.ReactNode {
  return (
    <thead className="bg-dark-amethyst-900 border-border-dark border-b">
      {children}
    </thead>
  );
}

/** Table body (<tbody>) */
export function TableBody({
  children,
}: {
  children: React.ReactNode;
}): React.ReactNode {
  return <tbody className="divide-border-dark divide-y">{children}</tbody>;
}

/**
 * A table row. Body rows pick up a subtle hover tint
 * pass `header` for the row that lives inside `TableHead` so it stays flat.
 */
export function TableRow({
  children,
  header = false,
  className,
}: {
  children: React.ReactNode;
  header?: boolean;
  className?: string;
}): React.ReactNode {
  return (
    <tr
      className={clsx(
        !header && "hover:bg-dark-amethyst-800/40 transition-colors",
        className,
      )}
    >
      {children}
    </tr>
  );
}

/** A column header cell (<th>). */
export function TableHeaderCell({
  children,
  align = "left",
  className,
}: {
  children?: React.ReactNode;
  align?: Align;
  className?: string;
}): React.ReactNode {
  return (
    <th
      scope="col"
      className={clsx(
        "text-muted px-3 py-2 text-xs font-bold tracking-wider uppercase md:px-4 md:py-3",
        alignClass[align],
        className,
      )}
    >
      {children}
    </th>
  );
}

/** A data cell (<td>). */
export function TableCell({
  children,
  align = "left",
  colSpan,
  className,
}: {
  children?: React.ReactNode;
  align?: Align;
  colSpan?: number;
  className?: string;
}): React.ReactNode {
  return (
    <td
      colSpan={colSpan}
      className={clsx(
        "text-body px-3 py-2 md:px-4 md:py-3",
        alignClass[align],
        className,
      )}
    >
      {children}
    </td>
  );
}
