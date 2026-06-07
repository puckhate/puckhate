/**
 * Format a numeric value as a currency string
 * @param value - monetary amount (e.g. 123)
 * @returns - formatted currency string (e.g. $123)
 */
export function formatAsCurrency(value: number | null | undefined): string {
  const numberFormat = Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
  if (typeof value !== "number") {
    return numberFormat.format(0).replace("0", "");
  }
  return numberFormat.format(value);
}

/**
 * Format a numeric value as a localized number
 * @param value - unformatted value
 * @returns - formatted value
 */
export function formatAsNumber(value: number | null | undefined): string {
  const numberFormat = Intl.NumberFormat("en-US", {
    style: "decimal",
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
  if (typeof value !== "number") {
    return numberFormat.format(0).replace("0", "");
  }
  return numberFormat.format(value);
}

/**
 * Format a datetime string as a local date string
 * @param value - datetime compatible string
 * @returns - formatted date as string
 */
export function formatAsLocaleDate(value: string | null | undefined): string {
  if (typeof value !== "string") {
    return "";
  }
  return (
    new Date(value).toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
    }) || ""
  );
}

/**
 * Format a datetime string as a local datetime string
 * @param value - datetime compatible string
 * @returns - formatted date as string
 */
export function formatAsLocaleDateTime(
  value: string | null | undefined,
): string {
  if (typeof value !== "string") {
    return "";
  }
  return (
    new Date(value).toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "numeric",
      minute: "numeric",
    }) || ""
  );
}

/**
 * Format a string as title case
 * @param value - string
 * @returns - string
 */
export function toTitleCase(value?: string): string {
  if (typeof value !== "string") {
    return "";
  }
  return value
    .toLowerCase()
    .split(" ")
    .map((val) => val.charAt(0).toUpperCase() + val.slice(1))
    .join(" ");
}
