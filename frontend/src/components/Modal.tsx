import { useState } from "react";

import {
  Dialog,
  DialogBackdrop,
  DialogPanel,
  DialogTitle,
} from "@headlessui/react";
import { XMarkIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import { AnimatePresence, motion } from "framer-motion";

type ModalWidth = "small" | "medium" | "large";

interface ModalRenderProps {
  closeModal(): void;
}

interface ModalTriggerProps {
  onClick(): void;
}

type ModalSection =
  | ((props: ModalRenderProps) => React.ReactNode)
  | React.ReactNode;

interface ModalProps {
  label: string;
  title?: React.ReactNode;
  onClose?(): void;
  onOpen?(): void;
  isOpen?: boolean;
  hideCloseButton?: boolean;
  width?: ModalWidth;
  className?: string;
  children: ModalSection;
  trigger?: (props: ModalTriggerProps) => React.JSX.Element;
}

const WIDTHS: Record<ModalWidth, string> = {
  small: "max-w-sm",
  medium: "max-w-lg",
  large: "max-w-3xl",
};

/**
 * Reusable modal dialogue component.
 *
 * @example
 * ```tsx
 * <Modal
 *   label="Confirm"
 *   title="Confirm"
 *   trigger={({ onClick }) => (
 *     <button type="button" onClick={onClick}>
 *       Open
 *     </button>
 *   )}
 * >
 *   {({ closeModal }) => (
 *     <>
 *       <p className="text-muted">Are you sure?</p>
 *       <button type="button" onClick={closeModal}>
 *         Cancel
 *       </button>
 *     </>
 *   )}
 * </Modal>
 * ```
 */
export default function Modal(props: ModalProps): React.ReactNode {
  const {
    trigger,
    onOpen,
    onClose,
    label,
    title,
    children,
    className,
    width = "medium",
    hideCloseButton = false,
    isOpen: parentIsOpen = false,
  } = props;
  const [isOpen, setIsOpen] = useState(parentIsOpen);

  const handleOpen = () => {
    setIsOpen(true);
    if (onOpen) onOpen();
  };

  const handleClose = () => {
    setIsOpen(false);
    if (onClose) onClose();
  };

  const renderProps: ModalRenderProps = {
    closeModal: handleClose,
  };

  const triggerProps: ModalTriggerProps = {
    onClick: handleOpen,
  };

  return (
    <>
      {trigger && trigger(triggerProps)}
      <AnimatePresence>
        {isOpen && (
          <Dialog
            static
            open={isOpen}
            onClose={handleClose}
            aria-label={label}
            className="relative z-50"
          >
            <DialogBackdrop
              as={motion.div}
              initial={{ opacity: 0 }}
              animate={{
                opacity: 1,
                transition: { duration: 0.2, ease: "easeOut" },
              }}
              exit={{
                opacity: 0,
                transition: { duration: 0.2, ease: "easeOut" },
              }}
              className="bg-dark-amethyst-950/30 fixed inset-0 backdrop-blur-md"
            />

            <div className="fixed inset-0 flex items-center justify-center p-6">
              <DialogPanel
                as={motion.div}
                initial={{ opacity: 0, scale: 0.96, y: 8 }}
                animate={{
                  opacity: 1,
                  scale: 1,
                  y: 0,
                  transition: { duration: 0.2, ease: [0.16, 1, 0.3, 1] },
                }}
                exit={{
                  opacity: 0,
                  scale: 0.96,
                  y: 8,
                  transition: { duration: 0.2, ease: [0.16, 1, 0.3, 1] },
                }}
                className={clsx(
                  "border-border-dark bg-page relative max-h-[calc(100vh-3rem)] w-full overflow-y-auto rounded-2xl border p-7 shadow-2xl ring-1 shadow-black/50 ring-black/20",
                  WIDTHS[width],
                  className,
                )}
              >
                {!hideCloseButton && (
                  <button
                    type="button"
                    onClick={handleClose}
                    aria-label="Close dialog"
                    className="text-body hover:text-heading-pink focus:ring-sky-aqua-500 absolute top-4 right-4 inline-flex size-9 items-center justify-center rounded-lg transition-colors hover:bg-white/5 focus:ring-2 focus:outline-none"
                  >
                    <XMarkIcon aria-hidden="true" className="size-5" />
                  </button>
                )}

                {title && (
                  <DialogTitle
                    as="h2"
                    className="font-heading text-body mb-3 pr-8 text-xl font-bold tracking-tight"
                  >
                    {title}
                  </DialogTitle>
                )}

                {typeof children === "function"
                  ? children(renderProps)
                  : children}
              </DialogPanel>
            </div>
          </Dialog>
        )}
      </AnimatePresence>
    </>
  );
}
