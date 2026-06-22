import { useId } from "react";

import cn from "@utils/classNames";
import { useField } from "formik";

interface TextFieldProps extends Omit<
  React.InputHTMLAttributes<HTMLInputElement>,
  "id"
> {
  /** Formik field name. */
  name: string;
  /** Visible label text. */
  label: string;
  /** Optional helper text shown beneath the input. */
  help?: string;
  /** Optional decorative content rendered inside the input's leading edge (e.g. a currency symbol). */
  leadingAddon?: React.ReactNode;
}

/**
 * Formik-bound text input with a label, optional help text, and validation
 * error. Accessibility: the input is nested in its label and linked via
 * `htmlFor`/`id`, help + error are wired through `aria-describedby`, and
 * `aria-invalid` / `aria-required` reflect state.
 */
export default function TextField({
  name,
  label,
  help,
  leadingAddon,
  required,
  className,
  ...props
}: TextFieldProps): React.ReactNode {
  const [field, meta] = useField(name);
  const reactId = useId();
  const inputId = `${reactId}-${name}`;
  const helpId = `${inputId}-help`;
  const errorId = `${inputId}-error`;
  const hasError = Boolean(meta.touched && meta.error);
  const describedBy = cn(help && helpId, hasError && errorId) || undefined;

  return (
    <div>
      <label htmlFor={inputId} className="block">
        <span className="text-body mb-1 block text-sm font-bold">
          {label}
          {required && (
            <span aria-hidden="true" className="text-heading-pink">
              {" "}
              *
            </span>
          )}
        </span>
        <div className="relative">
          {leadingAddon && (
            <span
              aria-hidden="true"
              className="text-muted pointer-events-none absolute inset-y-0 left-3 flex items-center"
            >
              {leadingAddon}
            </span>
          )}
          <input
            id={inputId}
            aria-required={required || undefined}
            aria-invalid={hasError || undefined}
            aria-describedby={describedBy}
            className={cn(
              "text-body placeholder:text-space-indigo-500 bg-dark-amethyst-800 block w-full rounded-lg border py-2 pr-3 focus:ring-2 focus:outline-none",
              leadingAddon ? "pl-7" : "pl-3",
              hasError
                ? "border-red-500 focus:ring-red-500"
                : "border-border-dark focus:ring-sky-aqua-500",
              className,
            )}
            {...field}
            {...props}
          />
        </div>
      </label>
      {help && (
        <p id={helpId} className="text-muted mt-1 text-sm">
          {help}
        </p>
      )}
      {hasError && (
        <p id={errorId} role="alert" className="mt-1 text-sm text-red-400">
          {meta.error}
        </p>
      )}
    </div>
  );
}
