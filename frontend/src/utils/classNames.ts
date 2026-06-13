import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/* Merge classes (conditionally) with clsx, dedupe (latest wins) with tailwind-merge */
export default function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
