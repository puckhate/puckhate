import { getLocaleCurrency } from "@utils/currency";

/**
 * Format a numeric value as a currency string in the user's locale
 * @param value - monetary amount (e.g. 123)
 * @returns - formatted currency string (e.g. $123)
 */
export function formatAsCurrency(value: number | null | undefined): string {
  const { locale, currency } = getLocaleCurrency();
  const numberFormat = Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
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
 * @param length - "short" or "long"
 * @returns - formatted date as string
 */
export function formatAsLocaleDate(
  value: string | null | undefined,
  length: "short" | "long" = "long",
): string {
  if (typeof value !== "string") {
    return "";
  }

  const dateOpts: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "long",
    day: "numeric",
  };
  if (length === "short") {
    dateOpts.month = "numeric";
  }
  return new Date(value).toLocaleDateString(undefined, dateOpts) || "";
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
