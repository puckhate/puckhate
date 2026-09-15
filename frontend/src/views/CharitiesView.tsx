import { useEffect, useState } from "react";

import client from "@client";
import Container from "@components/Container";
import { H1 } from "@components/Headings";
import {
  Table,
  TableBody,
  TableCell,
  TableError,
  TableHead,
  TableHeaderCell,
  TableRow,
} from "@components/Table";
import constants from "@constants";
import { ArrowTopRightOnSquareIcon } from "@heroicons/react/24/outline";
import type { Charity } from "@types";
import { routeMeta } from "@utils/meta";
import { isCancel } from "axios";
import Skeleton from "react-loading-skeleton";
import type { MetaFunction } from "react-router";

export const meta: MetaFunction = () => routeMeta(constants.ROUTES.charities);

export default function CharitiesView(): React.ReactNode {
  const [charities, setCharities] = useState<Charity[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  /*
   * Load the list of approved charities
   */
  useEffect(() => {
    const controller = new AbortController();
    client
      .get<Charity[]>(constants.API_ENDPOINTS.CHARITIES, {
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
      .catch((err) => {
        if (!isCancel(err)) {
          setError("Failed to load charities");
          setLoading(false);
        }
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
              className="link inline-flex items-center justify-items-end space-x-3 no-underline"
            >
              <div>Visit Site</div>
              <ArrowTopRightOnSquareIcon className="size-4" />
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
          <H1>Suggested Charities List</H1>
          <p className="text-muted text-sm">
            These organizations are doing the work. Every donation to them is an
            assist. This list is curated by our organizers and community, and is
            by no means exhaustive.
          </p>
        </header>

        <section className="space-y-3">
          {error ? (
            <TableError message={error} />
          ) : (
            <Table>
              <TableHead>
                <TableRow header>
                  <TableHeaderCell>Charity</TableHeaderCell>
                  <TableHeaderCell align="right">Website</TableHeaderCell>
                </TableRow>
              </TableHead>
              <TableBody>{tableBody}</TableBody>
            </Table>
          )}
        </section>

        <p className="text-muted mt-5 text-xs">
          A charity's name appearing on this list does not imply that
          organization's endorsement of, or involvement in, this campaign.
          <br />
          If you are a representative of a charity who's name appears on this
          list and would like to request that your organization be removed,
          please reach out to us at{" "}
          <a href="mailto:hello@puckhate.com" className="link">
            hello@puckhate.com
          </a>
          .
        </p>
      </article>
    </Container>
  );
}
