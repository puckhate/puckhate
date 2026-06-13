import { useCallback, useState } from "react";

import { Modal } from "@components";
import constants from "@constants";
import {
  ArrowTopRightOnSquareIcon,
  ArrowsUpDownIcon,
} from "@heroicons/react/24/outline";
import type { Charity } from "@types";
import { Link } from "react-router-dom";

import CharitySlotMachine from "./CharitySlotMachine";

interface CharityPickerModalProps {
  charities: Charity[];
}

interface CharityPickerContentsProps {
  charities: Charity[];
  closeModal: () => void;
}

function CharityPickerContents({
  charities,
  closeModal,
}: CharityPickerContentsProps): React.ReactNode {
  const [spinId, setSpinId] = useState(0); // Bumped to remount CharitySlotMachine, which kicks off a fresh spin
  const [winner, setWinner] = useState<Charity | undefined>(undefined);

  const spinAgain = useCallback(() => {
    setWinner(undefined);
    setSpinId((id) => id + 1);
  }, []);

  const canVisit = !!winner?.url;

  return (
    <div className="text-center">
      <h1 className="text-heading-pink mb-1.5 text-3xl font-black tracking-tighter">
        Not Sure Where to Donate?
      </h1>
      <span className="text-muted">Why not check out...</span>

      {/* "Slot machine" spinner */}
      <div className="mx-auto py-6">
        <CharitySlotMachine
          key={spinId}
          charities={charities}
          onSelect={closeModal}
          onSpinComplete={setWinner}
        />
      </div>

      {/* Button Row */}
      <div className="flex w-full flex-col items-center gap-5 md:flex-row">
        {/*
         * Both buttons remount when the reel settles rather than animating
         * their hover transition (a visible "flash").
         */}
        <a
          key={canVisit ? "visit-ready" : "visit-idle"}
          href={winner?.url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={closeModal}
          aria-disabled={!canVisit || undefined}
          tabIndex={canVisit ? undefined : -1}
          className="button-outline flex w-full items-center justify-center space-x-3 aria-disabled:pointer-events-none aria-disabled:opacity-50"
        >
          <div>Visit Charity</div>
          <ArrowTopRightOnSquareIcon className="size-4" />
        </a>
        <button
          key={winner === undefined ? "spin-idle" : "spin-ready"}
          type="button"
          onClick={spinAgain}
          disabled={winner === undefined}
          className="button-outline flex w-full items-center justify-center space-x-3 disabled:pointer-events-none disabled:opacity-50"
        >
          <div>Spin Again</div>
          <ArrowsUpDownIcon className="size-4" />
        </button>
      </div>

      <div className="text-muted pt-6 text-xs">
        Or,{" "}
        <Link className="link" to={constants.ROUTES.charities}>
          view our full list of charities
        </Link>
      </div>
    </div>
  );
}

export default function CharityPickerModal({
  charities,
}: CharityPickerModalProps): React.ReactNode {
  if (charities.length === 0) {
    return (
      <Link to={constants.ROUTES.charities} className="button-outline">
        Get a Suggestion
      </Link>
    );
  }

  return (
    <Modal
      label="Get a random charity suggestion"
      width="large"
      trigger={({ onClick }) => (
        <button type="button" onClick={onClick} className="button-outline">
          Get a Suggestion
        </button>
      )}
    >
      {({ closeModal }) => (
        <CharityPickerContents charities={charities} closeModal={closeModal} />
      )}
    </Modal>
  );
}
