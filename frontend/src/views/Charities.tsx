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
import CONSTANTS from "@constants";
import type { Charity } from "@types";
import Skeleton from "react-loading-skeleton";

export default function Charities(): React.ReactNode {
  const [charities, setCharities] = useState<Charity[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  /*
   * Load the list of approved charities
   */
  useEffect(() => {
    const controller = new AbortController();
    client
      .get<Charity[]>(CONSTANTS.API_ENDPOINTS.CHARITIES, {
        signal: controller.signal,
      })
      .then((response) => {
        // Shuffle once on mount so no charity is consistently listed first
        const shuffled = [...response.data];
        for (let i = shuffled.length - 1; i > 0; i -= 1) {
          const j = Math.floor(Math.random() * (i + 1));
          [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        setCharities(shuffled);
        setLoading(false);
      })
      .catch(() => {
        // Persist loading state on error, do not raise exception
      });
    return () => controller.abort();
  }, []);

  let tableBody: React.ReactNode;
  if (loading) {
    // loading state table
    tableBody = [1, 2, 3].map((idx) => (
      <TableRow key={idx}>
        <TableCell className="font-bold">
          <Skeleton />
        </TableCell>
        <TableCell align="right">
          <Skeleton />
        </TableCell>
      </TableRow>
    ));
  } else if (charities.length === 0) {
    // empty state table
    tableBody = (
      <TableRow>
        <TableCell colSpan={2} align="center" className="text-muted py-8">
          No charities have been added yet — check back soon.
        </TableCell>
      </TableRow>
    );
  } else {
    // charities list table
    tableBody = charities.map((charity) => (
      <TableRow key={charity.id}>
        <TableCell className="font-bold">{charity.name}</TableCell>
        <TableCell align="right" className="whitespace-nowrap">
          {charity.url?.length > 0 && (
            <a
              href={charity.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-heading-blue font-bold hover:underline"
            >
              Visit Site
            </a>
          )}
        </TableCell>
      </TableRow>
    ));
  }

  return (
    <Container>
      <article className="mx-auto max-w-3xl space-y-10">
        <header className="space-y-2">
          <h1 className="font-heading text-heading-pink text-4xl font-black tracking-tight uppercase">
            Suggested Charities List
          </h1>
          <p className="text-muted text-sm">
            These organizations are doing the work. Every donation to them is an
            assist. This list is curated by our organizers and community, and is
            by no means exhaustive.
          </p>
        </header>

        <section className="space-y-3">
          <Table>
            <TableHead>
              <TableRow header>
                <TableHeaderCell>Charity</TableHeaderCell>
                <TableHeaderCell align="right">Website</TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>{tableBody}</TableBody>
          </Table>
        </section>

        <p className="text-muted mt-5 text-xs">
          A charity's name appearing on this list does not imply that
          organization's endorsement of, or involvement in, this campaign.
          <br />
          If you are a representative of a charity who's name appears on this
          list and would like to request that your organization be removed,
          please reach out to us at{" "}
          <a href="mailto:hello@puckcurl.com" className="link">
            hello@puckcurl.com
          </a>
          .
        </p>
      </article>
    </Container>
  );
}
