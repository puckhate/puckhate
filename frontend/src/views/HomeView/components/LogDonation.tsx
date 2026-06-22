import { useCallback, useEffect, useMemo, useState } from "react";

import client from "@client";
import { ComboboxField, LoadingSpinner, TextField } from "@components";
import constants from "@constants";
import {
  CheckBadgeIcon,
  DocumentArrowUpIcon,
} from "@heroicons/react/24/outline";
import type { Charity, DonationReceipt } from "@types";
import cn from "@utils/classNames";
import { getLocaleCurrency } from "@utils/currency";
import { Form, Formik } from "formik";
import { useDropzone } from "react-dropzone";
import * as Yup from "yup";

const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024;
const FILE_TOO_LARGE_MESSAGE = `File is too large. Maximum size is ${MAX_FILE_SIZE_MB}MB.`;
const FILE_WRONG_FORMAT_MESSAGE = "Only image and PDF files are accepted.";

type FileUploadState = "new" | "uploading" | "success" | "error";

interface LogDonationProps {
  charities: Charity[];
}

export default function LogDonation({ charities }: LogDonationProps) {
  const [fileUploadStatus, setFileUploadStatus] =
    useState<FileUploadState>("new");
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [receiptToken, setReceiptToken] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  /*
   * Names of approved charities to suggest in the typeahead.
   */
  const charityNames = useMemo(
    () => charities.map((charity) => charity.name),
    [charities],
  );

  /*
   * Upload receipt image to API
   * Upload is processed asynchronsly while the user completes the form. The
   * returned receipt id is held until the form is submitted, which claims it.
   */
  const handleUploadReceipt = useCallback(async (file: File) => {
    setFileUploadStatus("uploading");
    setUploadError(null);
    const body = new FormData();
    body.append("file", file);
    try {
      const { data } = await client.post<DonationReceipt>(
        constants.API_ENDPOINTS.RECEIPTS,
        body,
      );
      setReceiptToken(data.token);
      setFileUploadStatus("success");
    } catch {
      setReceiptToken(null);
      setFileUploadStatus("error");
      setUploadError("That receipt could not be uploaded. Please try again.");
    }
  }, []);

  /*
   * Dropzone hook and file handling callback
   */
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const [file] = acceptedFiles;
      if (file) handleUploadReceipt(file);
    },
    [handleUploadReceipt],
  );
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDropRejected: (rejections) => {
      const codes = new Set(
        rejections.flatMap((rejection) =>
          rejection.errors.map((error) => error.code),
        ),
      );
      setFileUploadStatus("error");
      if (codes.has("file-too-large")) {
        setUploadError(FILE_TOO_LARGE_MESSAGE);
      } else if (codes.has("file-invalid-type")) {
        setUploadError(FILE_WRONG_FORMAT_MESSAGE);
      } else {
        setUploadError("That file could not be accepted.");
      }
    },
    accept: { "image/*": [], "application/pdf": [".pdf"] },
    maxSize: MAX_FILE_SIZE,
    multiple: false,
  });

  /*
   * Handle pasting of images anywhere on the page
   */
  useEffect(() => {
    const handlePaste = (event: ClipboardEvent) => {
      const items = Array.from(event.clipboardData?.items ?? []);
      const imageItem = items.find(
        (item) => item.kind === "file" && item.type.startsWith("image/"),
      );
      if (!imageItem) {
        // Do not accept non-image files
        setFileUploadStatus("error");
        setUploadError(FILE_WRONG_FORMAT_MESSAGE);
        return;
      }
      const file = imageItem.getAsFile();
      if (file) {
        event.preventDefault();
        if (file.size > MAX_FILE_SIZE) {
          // Do not accept files larger than {MAX_FILE_SIZE_MB}
          setFileUploadStatus("error");
          setUploadError(FILE_TOO_LARGE_MESSAGE);
          return;
        }
        handleUploadReceipt(file);
      }
    };
    window.addEventListener("paste", handlePaste);
    return () => window.removeEventListener("paste", handlePaste);
  }, [handleUploadReceipt]);

  return (
    <section>
      <h1 className="font-heading text-body text-center text-4xl font-black uppercase">
        Log Your Donation
      </h1>
      <p className="text-muted mt-5 text-center">
        Upload your donation receipt, tell us about your donation, and we'll add
        it to the total.
      </p>

      <div className="border-border-dark bg-dark-amethyst-950 mt-10 justify-center rounded-3xl border p-10 px-11 shadow-xl">
        {submitted ? (
          <div className="py-8 text-center">
            <CheckBadgeIcon className="mx-auto size-12 text-green-500" />
            <p className="font-heading text-body mt-2 text-lg font-bold">
              Thank you! Your donation has been logged.
            </p>
            <p className="text-muted mt-2 text-sm">
              Once reviewed, it will be reflected in the total.
            </p>
          </div>
        ) : (
          <>
            {/* File upload complete state */}
            {fileUploadStatus === "success" && (
              <div className="mb-12 text-center">
                <CheckBadgeIcon className="mx-auto size-12 text-green-500" />
                <span className="font-heading text-body font-bold">
                  Donation Receipt Accepted!
                </span>
              </div>
            )}

            {/* File upload in progress state */}
            {fileUploadStatus === "uploading" && (
              <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-12 text-center transition-colors">
                <LoadingSpinner className="text-heading-blue my-4" />
                <p className="font-heading text-body font-bold">Uploading...</p>
              </div>
            )}

            {/* File upload dropzone */}
            {["new", "error"].includes(fileUploadStatus) && (
              <div
                {...getRootProps()}
                className={cn(
                  "focus:ring-sky-aqua-500 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-12 text-center transition-colors focus:ring-2 focus:outline-0",
                  isDragActive
                    ? "border-border-light bg-dark-amethyst-900"
                    : "border-border-dark hover:border-border-light",
                  fileUploadStatus === "error" && "border-red-500",
                )}
              >
                <label htmlFor="receipt-upload" className="sr-only">
                  Upload your donation receipt
                  <input {...getInputProps()} id="receipt-upload" />
                </label>
                <p className="font-heading text-body font-bold">
                  Drop your receipt here, or paste a screenshot.
                </p>
                <DocumentArrowUpIcon className="text-space-indigo-600 my-4 size-12" />
                <p className="text-muted mt-2 text-sm">
                  Image or PDF files, up to {MAX_FILE_SIZE_MB}MB. You may redact
                  personal information.
                </p>
                {fileUploadStatus === "error" && (
                  <p className="mt-2 text-sm text-red-400">{uploadError}</p>
                )}
              </div>
            )}

            <div className="mt-5">
              <Formik
                initialValues={{ amount: "", charity: "", name: "" }}
                validationSchema={Yup.object({
                  amount: Yup.number()
                    .transform((value, original) =>
                      original === "" ? undefined : value,
                    )
                    .typeError("Enter a valid amount")
                    .positive("Amount must be greater than zero")
                    .required("Amount donated is required"),
                  charity: Yup.string().trim().required("Charity is required"),
                  name: Yup.string().trim(),
                })}
                onSubmit={async (values, { setSubmitting }) => {
                  setSubmitError(null);
                  try {
                    await client.post(constants.API_ENDPOINTS.DONATIONS, {
                      amount: values.amount,
                      charity: values.charity.trim(),
                      name: values.name.trim(),
                      receipt: receiptToken,
                      currency: getLocaleCurrency().currency,
                    });
                    setSubmitted(true);
                  } catch {
                    setSubmitError(
                      "We couldn't record your donation. Please try again.",
                    );
                  } finally {
                    setSubmitting(false);
                  }
                }}
              >
                {({ isSubmitting }) => (
                  <Form className="space-y-4">
                    <div className="flex flex-col gap-4 sm:flex-row">
                      <div className="flex-1">
                        <TextField
                          name="amount"
                          label="Amount Donated"
                          type="number"
                          inputMode="decimal"
                          leadingAddon="$"
                          min="0"
                          step="0.01"
                          placeholder="7"
                          required
                          help={`Total in ${getLocaleCurrency().currency}`}
                        />
                      </div>
                      <div className="flex-1">
                        <ComboboxField
                          name="charity"
                          label="Charity"
                          placeholder="Organization name"
                          options={charityNames}
                          required
                        />
                      </div>
                      <div className="flex-1">
                        <TextField
                          name="name"
                          label="Your Name"
                          help="Optional, will be displayed on leaderboard"
                        />
                      </div>
                    </div>
                    {submitError && (
                      <p role="alert" className="text-sm text-red-400">
                        {submitError}
                      </p>
                    )}
                    <button
                      type="submit"
                      disabled={isSubmitting || receiptToken === null}
                      className="button-solid-blue mt-3 w-full py-3"
                    >
                      {isSubmitting ? "Submitting..." : "Submit Donation"}
                    </button>
                  </Form>
                )}
              </Formik>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
