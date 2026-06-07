import { includeIgnoreFile } from "@eslint/compat";
import js from "@eslint/js";
import type { Linter } from "eslint";
import { configs, plugins } from "eslint-config-airbnb-extended";
import { rules as prettierConfigRules } from "eslint-config-prettier";
import prettierPlugin from "eslint-plugin-prettier";
import globals from "globals";
import path from "node:path";

const gitignorePath = path.resolve(".", ".gitignore");

const jsConfig: Linter.Config[] = [
  // ESLint Recommended Rules
  {
    name: "js/config",
    ...js.configs.recommended,
  },
  // Stylistic Plugin
  plugins.stylistic,
  // Import X Plugin
  plugins.importX,
  // Airbnb Base Recommended Config
  ...configs.base.recommended,
];

const reactConfig: Linter.Config[] = [
  // React Plugin
  plugins.react,
  // React Hooks Plugin
  plugins.reactHooks,
  // React JSX A11y Plugin
  plugins.reactA11y,
  // Airbnb React Recommended Config
  ...configs.react.recommended,
];

const typescriptConfig: Linter.Config[] = [
  // TypeScript ESLint Plugin
  plugins.typescriptEslint,
  // Airbnb Base TypeScript Config
  ...configs.base.typescript,
  // Airbnb React TypeScript Config
  ...configs.react.typescript,
];

const prettierConfig: Linter.Config[] = [
  // Prettier Plugin
  {
    name: "prettier/plugin/config",
    plugins: {
      prettier: prettierPlugin,
    },
  },
  // Prettier Config
  {
    name: "prettier/config",
    rules: {
      ...prettierConfigRules,
      "prettier/prettier": "error",
    },
  },
];

const customRules: Linter.Config = {
  name: "custom/rules",
  rules: {
    "import-x/no-cycle": "off",
    "import-x/no-extraneous-dependencies": ["error", { devDependencies: true }],
    "import-x/prefer-default-export": "off",
    "import-x/no-rename-default": "off",
    "jsx-a11y/click-events-have-key-events": "off",
    "jsx-a11y/label-has-associated-control": [
      "error",
      { controlComponents: ["Field"], assert: "both" },
    ],
    "no-restricted-exports": [
      "error",
      { restrictDefaultExports: { defaultFrom: false } },
    ],
    "react/jsx-props-no-spreading": "off",
    "react/no-unescaped-entities": "off",
    "react/no-unstable-nested-components": ["error", { allowAsProps: true }],
    "react/react-in-jsx-scope": "off",
    "react/require-default-props": ["error", { functions: "ignore" }],
  },
};

const typescriptOverrides: Linter.Config = {
  name: "custom/typescript-overrides",
  files: ["*.ts", "*.tsx", "**/*.ts", "**/*.tsx"],
  rules: {
    "no-undef": "off",
  },
};

const nodeScriptsOverrides: Linter.Config = {
  name: "custom/node-scripts-overrides",
  files: ["scripts/**/*.{js,mjs,cjs}"],
  languageOptions: {
    globals: globals.node,
  },
  rules: {
    "no-console": "off",
    "no-continue": "off",
    "no-plusplus": "off",
    "no-restricted-syntax": "off",
  },
};

const config: Linter.Config[] = [
  includeIgnoreFile(gitignorePath),
  // Javascript Config
  ...jsConfig,
  // React Config
  ...reactConfig,
  // TypeScript Config
  ...typescriptConfig,
  // Prettier Config
  ...prettierConfig,
  // Custom Rules
  customRules,
  // TypeScript Overrides
  typescriptOverrides,
  // Node Scripts Overrides
  nodeScriptsOverrides,
];

export default config;
