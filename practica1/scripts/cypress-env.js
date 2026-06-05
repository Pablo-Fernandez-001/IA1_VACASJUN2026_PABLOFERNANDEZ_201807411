const { spawn } = require("node:child_process");
const path = require("node:path");

const args = process.argv.slice(2);
const cypressRoot = path.dirname(require.resolve("cypress/package.json"));
const cypressCli = path.join(cypressRoot, "bin", "cypress");
const env = Object.fromEntries(
  Object.entries(process.env).filter(([key, value]) => key && !key.startsWith("=") && value !== undefined)
);

delete env.ELECTRON_RUN_AS_NODE;

const child = spawn(process.execPath, [cypressCli, ...args], {
  env,
  stdio: "inherit",
  shell: false
});

child.on("exit", (code) => {
  process.exit(code ?? 1);
});
