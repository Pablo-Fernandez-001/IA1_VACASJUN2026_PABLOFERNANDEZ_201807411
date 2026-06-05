const { spawn, spawnSync } = require("node:child_process");
const http = require("node:http");
const path = require("node:path");

const ROOT = path.join(__dirname, "..");
const BACKEND_URL = "http://127.0.0.1:8000";
const FRONTEND_URL = "http://127.0.0.1:5500";
const startedProcesses = [];

function cleanEnv() {
  const env = Object.fromEntries(
    Object.entries(process.env).filter(([key, value]) => key && !key.startsWith("=") && value !== undefined)
  );
  delete env.ELECTRON_RUN_AS_NODE;
  return env;
}

function get(url, timeoutMs = 2500) {
  return new Promise((resolve, reject) => {
    const request = http.get(url, { timeout: timeoutMs }, (response) => {
      let body = "";
      response.setEncoding("utf8");
      response.on("data", (chunk) => {
        body += chunk;
      });
      response.on("end", () => {
        resolve({ statusCode: response.statusCode, body });
      });
    });

    request.on("timeout", () => {
      request.destroy(new Error(`Timeout esperando ${url}`));
    });
    request.on("error", reject);
  });
}

async function backendReady() {
  try {
    const response = await get(`${BACKEND_URL}/`);
    return response.statusCode === 200 && response.body.includes("API funcionando correctamente");
  } catch {
    return false;
  }
}

async function frontendReady() {
  try {
    const response = await get(FRONTEND_URL);
    return response.statusCode === 200 && response.body.includes("Ruta Inteligente GT");
  } catch {
    return false;
  }
}

async function waitFor(label, predicate, timeoutMs = 60000) {
  const started = Date.now();

  while (Date.now() - started < timeoutMs) {
    if (await predicate()) return;
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  throw new Error(`No se pudo iniciar ${label} antes de ${timeoutMs / 1000}s.`);
}

function runNpmScript(scriptName) {
  const npmCli = process.env.npm_execpath;
  const command = npmCli ? process.execPath : process.platform === "win32" ? "npm.cmd" : "npm";
  const args = npmCli ? [npmCli, "run", scriptName] : ["run", scriptName];
  const child = spawn(command, args, {
    cwd: ROOT,
    env: cleanEnv(),
    stdio: "inherit"
  });

  startedProcesses.push(child);
  return child;
}

function runNodeScript(scriptName, args = []) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [path.join(__dirname, scriptName), ...args], {
      cwd: ROOT,
      env: cleanEnv(),
      stdio: "inherit"
    });

    child.on("exit", (code) => resolve(code ?? 1));
  });
}

function stopStartedProcesses() {
  for (const child of startedProcesses.reverse()) {
    if (!child.pid || child.exitCode !== null) continue;

    if (process.platform === "win32") {
      spawnSync("taskkill", ["/pid", String(child.pid), "/T", "/F"], { stdio: "ignore" });
    } else {
      child.kill("SIGTERM");
    }
  }
}

async function main() {
  try {
    if (await backendReady()) {
      console.log(`Backend ya disponible en ${BACKEND_URL}`);
    } else {
      console.log(`Levantando backend en ${BACKEND_URL}`);
      runNpmScript("backend");
      await waitFor("backend", backendReady);
    }

    if (await frontendReady()) {
      console.log(`Frontend ya disponible en ${FRONTEND_URL}`);
    } else {
      console.log(`Levantando frontend en ${FRONTEND_URL}`);
      runNpmScript("frontend");
      await waitFor("frontend", frontendReady);
    }

    const code = await runNodeScript("cypress-env.js", ["run"]);
    process.exitCode = code;
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  } finally {
    stopStartedProcesses();
  }
}

main();
