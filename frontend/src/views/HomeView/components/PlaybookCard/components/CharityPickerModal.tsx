import { Modal } from "@components";
import constants from "@constants";
import type { Charity } from "@types";
import { Link } from "react-router-dom";

import CharitySlotMachine from "./CharitySlotMachine";

interface CharityPickerModalProps {
  charities: Charity[];
}

export default function CharityPickerModal({
  charities,
}: CharityPickerModalProps): React.ReactNode {
  if (charities.length === 0) {
    return null;
  }

  return (
    <Modal
      label="Get a random charity suggestion"
      width="large"
      trigger={({ onClick }) => (
        <button
          type="button"
          onClick={onClick}
          className="border-border-light text-body hover:border-heading-blue hover:text-heading-blue rounded-xl border px-3 py-1"
        >
          Get a Suggestion
        </button>
      )}
    >
      {({ closeModal }) => (
        <div className="text-center">
          <h1 className="text-heading-pink mb-1.5 text-3xl font-black tracking-tighter">
            Not Sure Where to Donate?
          </h1>
          <span className="text-muted">Why not check out...</span>
          <div className="mx-auto py-6 md:w-3/4">
            <CharitySlotMachine charities={charities} onSelect={closeModal} />
          </div>
          <span className="text-muted text-xs">
            Or,{" "}
            <Link className="link" to={constants.ROUTES.charities}>
              view our full list of charities
            </Link>
          </span>
        </div>
      )}
    </Modal>
  );
}
