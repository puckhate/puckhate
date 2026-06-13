import { useEffect, useState } from "react";

import client from "@client";
import {
  Container,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from "@components";
import constants from "@constants";
import { useExchangeRate } from "@providers/ExchangeRateProvider";
import type { Donation } from "@types";
import { convertFromUSD } from "@utils/currency";
import { formatAsCurrency, formatAsLocaleDate } from "@utils/text";
import Skeleton from "react-loading-skeleton";

export default function Donations(): React.ReactNode {
  const [donations, setDonations] = useState<Donation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const { rate, ensureRate } = useExchangeRate();

  /*
   * Load the list of verified donations
   */
  useEffect(() => {
    const controller = new AbortController();
    client
      .get<Donation[]>(constants.API_ENDPOINTS.DONATIONS, {
        signal: controller.signal,
      })
      .then((response) => {
        setDonations(response.data);
        setLoading(false);
      })
      .catch(() => {
        // Persist loading state on error, do not raise exception
      });
    return () => controller.abort();
  }, []);

  /*
   * Fetch exchange rate if not already in the ExchangeRateContext
   */
  useEffect(() => {
    ensureRate();
  }, [ensureRate]);

  let tableBody: React.ReactNode;
  if (loading) {
    // loading state table
    tableBody = [1, 2, 3].map((idx) => (
      <TableRow key={idx}>
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
    ));
  } else if (donations.length === 0) {
    // empty state table
    tableBody = (
      <TableRow>
        <TableCell colSpan={4} align="center" className="text-muted py-8">
          No verified donations yet, why not break the ice?
        </TableCell>
      </TableRow>
    );
  } else {
    // donations list table
    tableBody = donations.map((donation) => (
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
          {formatAsCurrency(convertFromUSD(Number(donation.amount), rate ?? 1))}
        </TableCell>
      </TableRow>
    ));
  }

  return (
    <Container>
      <article className="mx-auto max-w-3xl space-y-10">
        <header className="space-y-2">
          <h1 className="font-heading text-heading-pink text-4xl font-black tracking-tight uppercase">
            Donations List
          </h1>
          <p className="text-muted text-sm">
            The list of donations in support of PUCKCURL! will update as
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
        </section>
      </article>
    </Container>
  );
}
