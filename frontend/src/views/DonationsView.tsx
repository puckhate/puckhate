import { useEffect, useState } from "react";

import client from "@client";
import {
  Container,
  H1,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from "@components";
import constants from "@constants";
import { ArrowRightIcon } from "@heroicons/react/16/solid";
import { useExchangeRate } from "@providers/ExchangeRateProvider";
import type { Donation, PaginatedResults } from "@types";
import { convertFromUSD } from "@utils/currency";
import { formatAsCurrency, formatAsLocaleDate } from "@utils/text";
import Skeleton from "react-loading-skeleton";

const PAGE_SIZE = 20;

export default function DonationsView(): React.ReactNode {
  const [donations, setDonations] = useState<Donation[]>([]);
  const [donationsPageOffset, setDonationsPageOffset] = useState<number>(0);
  const [donationsPageHasNext, setDonationsPageHasNext] =
    useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const { rate, ensureRate } = useExchangeRate();

  /*
   * Load next page of donations
   */
  function handleLoadMore(): void {
    if (donationsPageHasNext) {
      setDonationsPageOffset(donationsPageOffset + PAGE_SIZE);
      setLoading(true);
    }
  }

  /*
   * Load the list of verified donations
   */
  useEffect(() => {
    const controller = new AbortController();
    client
      .get<PaginatedResults<Donation>>(constants.API_ENDPOINTS.DONATIONS, {
        params: { limit: PAGE_SIZE, offset: donationsPageOffset },
        signal: controller.signal,
      })
      .then((response) => {
        // Append the incoming page to existing list
        setDonations((prev) => [...prev, ...response.data.results]);
        setDonationsPageHasNext(!!response.data.next);
        setLoading(false);
      })
      .catch(() => {
        // Persist loading state on error, do not raise exception
      });
    return () => controller.abort();
  }, [donationsPageOffset]);

  /*
   * Fetch exchange rate if not already in the ExchangeRateContext
   */
  useEffect(() => {
    ensureRate();
  }, [ensureRate]);

  /*
   * Render a skeleton row to use while loading donations
   */
  function renderSkeletonRow(key: React.Key): React.ReactNode {
    return (
      <TableRow key={key}>
        <TableCell className="hidden sm:table-cell">
          <Skeleton />
        </TableCell>
        <TableCell>
          <Skeleton />
        </TableCell>
        <TableCell className="hidden sm:table-cell">
          <Skeleton />
        </TableCell>
        <TableCell>
          <Skeleton />
        </TableCell>
      </TableRow>
    );
  }

  let tableBody: React.ReactNode;
  if (!loading && donations.length === 0) {
    // empty state table
    tableBody = (
      <TableRow>
        <TableCell colSpan={4} align="center" className="text-muted py-8">
          No verified donations yet, why not break the ice?
        </TableCell>
      </TableRow>
    );
  } else {
    // donations list.
    // while loading, skeleton rows are appended below the existing rows
    tableBody = (
      <>
        {donations.map((donation) => (
          <TableRow key={donation.id}>
            <TableCell className="text-muted hidden whitespace-nowrap sm:table-cell">
              <span className="md:hidden">
                {formatAsLocaleDate(donation.created, "short")}
              </span>
              <span className="hidden md:inline">
                {formatAsLocaleDate(donation.created, "long")}
              </span>
            </TableCell>
            <TableCell className="font-bold">{donation.name}</TableCell>
            <TableCell className="hidden sm:table-cell">
              <span className="line-clamp-1">{donation.charity}</span>
            </TableCell>
            <TableCell
              align="right"
              className="text-heading-blue font-bold whitespace-nowrap"
            >
              {formatAsCurrency(
                convertFromUSD(Number(donation.amount), rate ?? 1),
              )}
            </TableCell>
          </TableRow>
        ))}
        {loading &&
          Array.from({ length: PAGE_SIZE }, (_, idx) =>
            renderSkeletonRow(`skeleton-${idx}`),
          )}
      </>
    );
  }

  return (
    <Container>
      <article className="mx-auto max-w-3xl space-y-10">
        <header className="space-y-2">
          <H1>Donations List</H1>
          <p className="text-muted text-sm">
            The list of donations in support of PUCKHATE! will update as
            donation receipts are validated. Donors can choose to provide their
            name or stay anonymous.
          </p>
        </header>

        <section className="space-y-3">
          <Table>
            <TableHead>
              <TableRow header>
                <TableHeaderCell className="hidden sm:table-cell">
                  Date
                </TableHeaderCell>
                <TableHeaderCell>Donor</TableHeaderCell>
                <TableHeaderCell className="hidden sm:table-cell">
                  Charity
                </TableHeaderCell>
                <TableHeaderCell align="right">Amount</TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>{tableBody}</TableBody>
          </Table>

          {!loading && donationsPageHasNext && (
            <div className="flex justify-center pt-6">
              <button
                type="button"
                className="button-outline font-display flex items-center justify-center space-x-1.5 text-sm"
                onClick={handleLoadMore}
              >
                <div>View More</div>
                <ArrowRightIcon className="size-4" />
              </button>
            </div>
          )}
        </section>
      </article>
    </Container>
  );
}
