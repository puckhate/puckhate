import { useEffect, useState } from "react";

import constants from "@constants";
import type { Charity } from "@types";
import { Link } from "react-router";

interface CharityPickerModalProps {
  charities: Charity[];
}

/*
 * Split out CharityPickerDialog so motion/react stays out of the initial page load
 * Loaded after first paint in a useEffect so it is available by the time
 * a user clicks the button to open the modal.
 */
type CharityPickerDialogModule = typeof import("./CharityPickerDialog");
let dialogModule: Promise<CharityPickerDialogModule> | undefined;
const loadDialog = () => (dialogModule ??= import("./CharityPickerDialog"));

export default function CharityPickerModal({
  charities,
}: CharityPickerModalProps): React.ReactNode {
  const [openCount, setOpenCount] = useState(0);
  const [Dialog, setDialog] = useState<
    CharityPickerDialogModule["default"] | null
  >(null);

  /*
   * Resolve the module into state rather than rendering it through lazy()
   */
  useEffect(() => {
    if (charities.length === 0) return;
    let cancelled = false;
    loadDialog().then((module) => {
      if (!cancelled) setDialog(() => module.default);
    });
    return () => {
      cancelled = true;
    };
  }, [charities.length]);

  if (charities.length === 0) {
    return (
      <Link to={constants.ROUTES.charities} className="button-outline">
        Get a Suggestion
      </Link>
    );
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpenCount((count) => count + 1)}
        className="button-outline"
      >
        Get a Suggestion
      </button>
      {openCount > 0 && Dialog && (
        <Dialog key={openCount} charities={charities} />
      )}
    </>
  );
}
