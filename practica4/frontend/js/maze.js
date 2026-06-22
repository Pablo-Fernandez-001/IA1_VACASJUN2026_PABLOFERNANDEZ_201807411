(function () {
  "use strict";

  const keyOf = (point) => `${point.row},${point.col}`;

  class MazeBoard {
    constructor(element, onChange) {
      this.element = element;
      this.onChange = onChange;
      this.mode = "obstacle";
      this.mouseDown = false;
      this.visualTimer = null;
      this.create(10, 10);
      this.bindPointerEvents();
    }

    create(rows, cols) {
      this.rows = rows;
      this.cols = cols;
      this.start = { row: 0, col: 0 };
      this.goal = { row: rows - 1, col: cols - 1 };
      this.obstacles = new Set();
      this.visited = new Set();
      this.path = new Set();
      this.render();
      this.changed();
    }

    bindPointerEvents() {
      this.element.addEventListener("mousedown", (event) => {
        const cell = event.target.closest(".maze-cell");
        if (!cell) return;
        this.mouseDown = true;
        this.editCell(cell, false);
      });
      this.element.addEventListener("mouseover", (event) => {
        const cell = event.target.closest(".maze-cell");
        if (this.mouseDown && cell && this.mode === "obstacle") this.editCell(cell, true);
      });
      this.element.addEventListener("mousemove", (event) => {
        const cell = event.target.closest(".maze-cell");
        if (cell) {
          this.element.dispatchEvent(new CustomEvent("cellhover", {
            detail: { row: Number(cell.dataset.row), col: Number(cell.dataset.col) },
          }));
        }
      });
      window.addEventListener("mouseup", () => { this.mouseDown = false; });
    }

    editCell(cell, dragging) {
      const point = { row: Number(cell.dataset.row), col: Number(cell.dataset.col) };
      const key = keyOf(point);
      this.clearVisualization();
      if (this.mode === "obstacle") {
        if (key === keyOf(this.start) || key === keyOf(this.goal)) return;
        if (dragging) this.obstacles.add(key);
        else if (this.obstacles.has(key)) this.obstacles.delete(key);
        else this.obstacles.add(key);
      } else if (this.mode === "start") {
        this.obstacles.delete(key);
        this.start = point;
      } else if (this.mode === "goal") {
        this.obstacles.delete(key);
        this.goal = point;
      }
      this.paintAll();
      this.changed();
    }

    setMode(mode) {
      this.mode = mode;
    }

    load(example) {
      this.rows = example.rows;
      this.cols = example.cols;
      this.start = { ...example.start };
      this.goal = { ...example.goal };
      this.obstacles = new Set(example.obstacles.map(keyOf));
      this.visited = new Set();
      this.path = new Set();
      this.render();
      this.changed();
    }

    clearObstacles() {
      this.obstacles.clear();
      this.clearVisualization();
      this.paintAll();
      this.changed();
    }

    clearVisualization() {
      if (this.visualTimer) window.clearTimeout(this.visualTimer);
      this.clearRover();
      this.visited.clear();
      this.path.clear();
      this.element.removeAttribute("data-algorithm");
      this.paintAll();
    }

    getPayload() {
      return {
        rows: this.rows,
        cols: this.cols,
        start: { ...this.start },
        goal: { ...this.goal },
        obstacles: [...this.obstacles].map((key) => {
          const [row, col] = key.split(",").map(Number);
          return { row, col };
        }),
      };
    }

    async visualize(result, onProgress = null) {
      this.clearVisualization();
      this.element.dataset.algorithm = result.algorithm.toLowerCase();
      const delay = Math.max(4, Math.min(28, 650 / Math.max(result.visited_nodes.length, 1)));
      for (const [index, point] of result.visited_nodes.entries()) {
        this.visited.add(keyOf(point));
        this.paintCell(point);
        if (onProgress) onProgress({
          phase: "exploration",
          algorithm: result.algorithm,
          point,
          current: index + 1,
          total: result.visited_nodes.length,
        });
        await new Promise((resolve) => { this.visualTimer = window.setTimeout(resolve, delay); });
      }
      result.path.forEach((point) => this.path.add(keyOf(point)));
      this.paintAll();
      if (onProgress) onProgress({
        phase: "route-ready",
        algorithm: result.algorithm,
        point: result.path[0] || null,
        current: 0,
        total: result.path.length,
      });
    }

    clearRover() {
      this.element.querySelectorAll(".rover-token").forEach((token) => token.remove());
      this.element.classList.remove("has-active-rover");
    }

    placeRover(point, previous = null) {
      this.clearRover();
      const cell = this.element.querySelector(`[data-row="${point.row}"][data-col="${point.col}"]`);
      if (!cell) return;
      let heading = 0;
      if (previous) {
        const rowDelta = point.row - previous.row;
        const colDelta = point.col - previous.col;
        if (colDelta > 0) heading = 90;
        else if (rowDelta > 0) heading = 180;
        else if (colDelta < 0) heading = -90;
      }
      const token = document.createElement("span");
      token.className = "rover-token";
      token.style.setProperty("--heading", `${heading}deg`);
      token.setAttribute("aria-hidden", "true");
      cell.appendChild(token);
      this.element.classList.add("has-active-rover");
    }

    render() {
      this.element.innerHTML = "";
      this.element.style.setProperty("--rows", this.rows);
      this.element.style.setProperty("--cols", this.cols);
      const fragment = document.createDocumentFragment();
      for (let row = 0; row < this.rows; row += 1) {
        for (let col = 0; col < this.cols; col += 1) {
          const cell = document.createElement("button");
          cell.type = "button";
          cell.className = "maze-cell";
          cell.dataset.row = row;
          cell.dataset.col = col;
          cell.setAttribute("role", "gridcell");
          fragment.appendChild(cell);
        }
      }
      this.element.appendChild(fragment);
      this.renderAxes();
      this.paintAll();
    }

    renderAxes() {
      const columnAxis = document.querySelector("#columnAxis");
      const rowAxis = document.querySelector("#rowAxis");
      if (!columnAxis || !rowAxis) return;
      columnAxis.innerHTML = "";
      rowAxis.innerHTML = "";
      columnAxis.style.gridTemplateColumns = `repeat(${this.cols}, 1fr)`;
      rowAxis.style.gridTemplateRows = `repeat(${this.rows}, 1fr)`;
      const columnStep = this.cols > 16 ? 5 : this.cols > 10 ? 2 : 1;
      const rowStep = this.rows > 16 ? 5 : this.rows > 10 ? 2 : 1;
      for (let col = 0; col < this.cols; col += 1) {
        const label = document.createElement("span");
        label.textContent = col % columnStep === 0 ? String(col).padStart(2, "0") : "";
        columnAxis.appendChild(label);
      }
      for (let row = 0; row < this.rows; row += 1) {
        const label = document.createElement("span");
        label.textContent = row % rowStep === 0 ? String(row).padStart(2, "0") : "";
        rowAxis.appendChild(label);
      }
    }

    paintCell(point) {
      const cell = this.element.querySelector(`[data-row="${point.row}"][data-col="${point.col}"]`);
      if (cell) this.paint(cell);
    }

    paintAll() {
      this.element.querySelectorAll(".maze-cell").forEach((cell) => this.paint(cell));
    }

    paint(cell) {
      const point = { row: Number(cell.dataset.row), col: Number(cell.dataset.col) };
      const key = keyOf(point);
      const classes = ["maze-cell"];
      let label = `Fila ${point.row}, columna ${point.col}, libre`;
      if (this.visited.has(key)) { classes.push("is-visited"); label = label.replace("libre", "explorada"); }
      if (this.path.has(key)) { classes.push("is-path"); label = label.replace(/libre|explorada/, "ruta"); }
      if (this.obstacles.has(key)) { classes.push("is-obstacle"); label = label.replace(/libre|explorada|ruta/, "obstáculo"); }
      if (key === keyOf(this.start)) { classes.push("is-start"); label = `Fila ${point.row}, columna ${point.col}, inicio`; }
      if (key === keyOf(this.goal)) { classes.push("is-goal"); label = `Fila ${point.row}, columna ${point.col}, destino`; }
      if (key === keyOf(this.start) && key === keyOf(this.goal)) classes.push("is-start-goal");
      cell.className = classes.join(" ");
      cell.setAttribute("aria-label", label);
      cell.textContent = classes.includes("is-start-goal") ? "◎" : classes.includes("is-start") ? "S" : classes.includes("is-goal") ? "G" : "";
    }

    changed() {
      if (this.onChange) this.onChange(this.getPayload());
      this.element.dispatchEvent(new CustomEvent("mazechange"));
    }
  }

  window.MazeBoard = MazeBoard;
})();
