const { spawnSync } = require("node:child_process");
const path = require("node:path");

const root = path.join(__dirname, "..");
const prologFile = path.join(root, "prolog", "rutas.pl");

const checks = [
  {
    name: "Base de conocimiento con minimo 10 ciudades",
    goal: "ciudades(Ciudades), length(Ciudades, Total), Total >= 10"
  },
  {
    name: "Distancias representadas mediante hechos conexion/3",
    goal: "conexion(guatemala, antigua, 45)"
  },
  {
    name: "Busqueda de rutas entre ciudades",
    goal: "ruta(guatemala, quetzaltenango, Ruta, Distancia), Ruta = [guatemala, antigua, chimaltenango, quetzaltenango], Distancia =:= 230"
  },
  {
    name: "Prevencion de ciclos en rutas",
    goal: "\\+ (ruta(guatemala, quetzaltenango, Ruta, _), sort(Ruta, Unicas), length(Ruta, TotalRuta), length(Unicas, TotalUnicas), TotalRuta =\\= TotalUnicas)"
  },
  {
    name: "Calculo correcto de distancia total",
    goal: "ruta(guatemala, quetzaltenango, [guatemala, antigua, chimaltenango, quetzaltenango], 230)"
  },
  {
    name: "Determinacion automatica de ruta mas corta",
    goal: "ruta_mas_corta(guatemala, quetzaltenango, [guatemala, antigua, chimaltenango, quetzaltenango], 230)"
  },
  {
    name: "Todas las rutas posibles se ordenan por distancia",
    goal: "rutas_posibles(guatemala, quetzaltenango, [[D1,_],[D2,_]|_]), D1 =< D2"
  },
  {
    name: "Agregar nuevas ciudades y conexiones en Prolog",
    goal: "agregar_conexion(ciudad_prueba_a, ciudad_prueba_b, 12), conexion_existente(ciudad_prueba_a, ciudad_prueba_b), ruta_mas_corta(ciudad_prueba_a, ciudad_prueba_b, [ciudad_prueba_a, ciudad_prueba_b], 12)"
  }
];

function runGoal(goal) {
  const result = spawnSync("swipl", [
    "-q",
    "-s",
    prologFile,
    "-g",
    `${goal}, halt.`
  ], {
    cwd: root,
    encoding: "utf8"
  });

  return {
    ok: result.status === 0,
    stderr: result.stderr.trim()
  };
}

let failures = 0;

console.log("Verificacion de rubrica Practica 1\n");

for (const check of checks) {
  const result = runGoal(check.goal);
  const icon = result.ok ? "OK" : "ERROR";
  console.log(`[${icon}] ${check.name}`);

  if (!result.ok) {
    failures += 1;
    if (result.stderr) console.log(result.stderr);
  }
}

if (failures > 0) {
  console.error(`\n${failures} verificacion(es) fallaron.`);
  process.exit(1);
}

console.log("\nTodas las verificaciones de Prolog pasaron.");
