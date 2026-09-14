import { Suspense } from "react";

import { Footer, Nav } from "@components";
import LoadingView from "@views/LoadingView";
import { Outlet } from "react-router";

export default function AppLayout(): React.ReactNode {
  return (
    <div className="flex min-h-screen flex-col">
      <Nav />
      <main className="flex flex-1 flex-col">
        <Suspense fallback={<LoadingView />}>
          <Outlet />
        </Suspense>
      </main>
      <Footer />
    </div>
  );
}
