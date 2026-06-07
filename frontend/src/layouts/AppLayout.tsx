import { Suspense } from "react";

import { Footer, Nav } from "@components";
import { Outlet } from "react-router-dom";

export default function AppLayout(): React.ReactNode {
  return (
    <div className="flex min-h-screen flex-col">
      <Nav />
      <main className="flex-1">
        <Suspense
          fallback={
            <div className="text-muted px-6 py-10 text-center">Loading…</div>
          }
        >
          <Outlet />
        </Suspense>
      </main>
      <Footer />
    </div>
  );
}
