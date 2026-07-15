# Contributing to PUCKHATE!

Thanks for your interest in contributing. This is a small fan project maintained
by a small group, but thoughtful outside contributions are welcome.

## What PUCKHATE! is (and isn't)

PUCKHATE! is a public record of charitable donations that fans self-report having
made elsewhere. It does not accept, process, or facilitate donations or
payments. Please keep contributions within that scope.

## Ground rules (please read before contributing)

This project is protest speech, and it stays legally protected only if we are
careful. These rules are not optional:

- **Only publicly verifiable claims.** Any statement about a person — especially
  the player the campaign responds to — must be grounded in publicly documented,
  verifiable sources and framed as opinion or commentary on those facts, not as
  new assertions of fact. When in doubt, leave it out.
- **No threats or harassment.** Nothing in the app, copy, issues, or PRs may
  threaten, target, or harass any individual.
- **No copyrighted or branded material.** Do not add PWHL or team logos, marks,
  or other copyrighted/branded assets anywhere. This keeps liability off the
  league, the teams, and the player.

Contributions that cross these lines won't be merged, regardless of code quality.

## How to contribute

1. Discuss features before you build them. For anything beyond a small fix,
   open an issue to talk through the idea first. This project has a deliberately
   narrow scope and a particular ethos (see the ground rules above), so a quick
   conversation up front confirms a feature is a good fit before you invest your
   time in it. Bug fixes and small improvements don't need this.
2. Fork the repository and create a branch for your change.
3. Make your change, following the conventions below.
4. Run the checks and preview your change in the running app (see
   [Before you open a PR](#before-you-open-a-pr)).
5. Open a pull request against `master`. Describe what you changed and why.

## Conventions

- **No "vibe coding"**: contributions wholly authored by AI "vibe coding" will be rejected. The use of
  AI tools in your development workflow is permissible, but you are accountable for the code you contribute.
- **Commit messages**: we encourage [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `chore:`, `docs:`, `build:`, …). It keeps history readable.
- **Match the surrounding code.** Follow the style, naming, and structure already
  present in the file you're editing.

## Before you open a PR

Please make sure these pass locally.

```bash
make format-be   # backend (ruff format)
make lint-be     # backend (ruff + ty check)
```

```bash
make format-fe   # frontend (prettier)
make lint-fe     # frontend (eslint)
```

Also confirm migrations apply cleanly (`make migrate`), and include any new
migration files your model changes generate.

**Run the app and preview your change.** Lint and types passing isn't enough,
start the project locally and exercise the actual behavior you changed in the
browser (and the Django admin, if relevant) to confirm it works as intended.

A short note in your PR about how you verified the change helps reviewers.

> There's no automated test suite yet. Backend tests are planned, if your change
> is a good candidate for one, tests are very welcome.

## Reporting issues

Open a GitHub issue describing the problem or proposal. For anything touching the
ground rules above (a claim about a person, an asset's provenance), please flag it
explicitly so a maintainer can review it carefully.

## Code of conduct

Be respectful and constructive. Assume good faith, keep discussion focused on the
work, and remember this project exists to support people — extend that same
respect to everyone you interact with here. Harassment or discriminatory behavior
won't be tolerated.
