import { useId, useState } from "react";

import {
  Combobox,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
} from "@headlessui/react";
import { CheckIcon } from "@heroicons/react/24/outline";
import cn from "@utils/classNames";
import { useField } from "formik";

interface ComboboxFieldProps {
  /** Formik field name. */
  name: string;
  /** Visible label text. */
  label: string;
  /** Suggested values shown in the dropdown. Free text is always allowed. */
  options: string[];
  /** Optional helper text shown beneath the input. */
  help?: string;
  /** Optional placeholder. */
  placeholder?: string;
  /** Marks the field as required (visual asterisk + aria). */
  required?: boolean;
}

/**
 * Formik-bound typeahead. Suggests values from `options` but never constrains
 * the user to them — whatever is typed is committed to the field, so a brand
 * new value can always be submitted. Styling and accessibility mirror
 * `TextField`: the input is labelled via `htmlFor`/`id`, help + error are wired
 * through `aria-describedby`, and `aria-invalid` / `aria-required` reflect
 * state.
 */
export default function ComboboxField({
  name,
  label,
  options,
  help,
  placeholder,
  required,
}: ComboboxFieldProps): React.ReactNode {
  const [field, meta, helpers] = useField(name);
  const [query, setQuery] = useState("");
  const reactId = useId();
  const inputId = `${reactId}-${name}`;
  const helpId = `${inputId}-help`;
  const errorId = `${inputId}-error`;
  const hasError = Boolean(meta.touched && meta.error);
  const describedBy = cn(help && helpId, hasError && errorId) || undefined;

  // Only suggest once the user has started typing — an empty query shows
  // nothing, which keeps the panel hidden (see `empty:invisible` below).
  const trimmedQuery = query.trim().toLowerCase();
  const filtered = trimmedQuery
    ? options.filter((option) => option.toLowerCase().includes(trimmedQuery))
    : [];

  return (
    <div>
      <Combobox
        value={field.value}
        onChange={(value: string | null) => helpers.setValue(value ?? "")}
        onClose={() => setQuery("")}
      >
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
          <ComboboxInput
            id={inputId}
            placeholder={placeholder}
            autoComplete="off"
            aria-required={required || undefined}
            aria-invalid={hasError || undefined}
            aria-describedby={describedBy}
            displayValue={(value: string) => value}
            onChange={(event) => {
              setQuery(event.target.value);
              helpers.setValue(event.target.value);
            }}
            onBlur={() => helpers.setTouched(true)}
            className={cn(
              "text-body placeholder:text-space-indigo-500 bg-dark-amethyst-800 block w-full rounded-lg border px-3 py-2 focus:ring-2 focus:outline-none",
              hasError
                ? "border-red-500 focus:ring-red-500"
                : "border-border-dark focus:ring-border-light",
            )}
          />
        </label>
        <ComboboxOptions
          anchor="bottom"
          className="border-border-dark bg-dark-amethyst-800 z-10 mt-1 max-h-60 w-(--input-width) overflow-auto rounded-lg border py-1 shadow-xl empty:invisible"
        >
          {filtered.map((option) => (
            <ComboboxOption
              key={option}
              value={option}
              className="text-body data-focus:bg-dark-amethyst-900 flex cursor-pointer items-center gap-2 px-3 py-2 text-sm"
            >
              {({ selected }) => (
                <>
                  <CheckIcon
                    aria-hidden="true"
                    className={cn(
                      "text-heading-blue size-4 shrink-0",
                      !selected && "invisible",
                    )}
                  />
                  <span>{option}</span>
                </>
              )}
            </ComboboxOption>
          ))}
        </ComboboxOptions>
      </Combobox>
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
