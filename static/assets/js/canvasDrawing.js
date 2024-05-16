class CanvasDrawing {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext("2d");
        this.painting = false;
        this.undoStack = [];

        // Event listeners
        this.canvas.addEventListener("mousedown", this.startPosition.bind(this));
        this.canvas.addEventListener("mouseup", this.endPosition.bind(this));
        this.canvas.addEventListener("mousemove", this.draw.bind(this));
        this.canvas.addEventListener("touchstart", this.startPosition.bind(this));
        this.canvas.addEventListener("touchend", this.endPosition.bind(this));
        this.canvas.addEventListener("touchmove", this.draw.bind(this));
        this.canvas.addEventListener("touchmove", (e) => e.preventDefault());
        this.canvas.addEventListener("mousewheel", this.preventScroll.bind(this));

        // Event listener para detectar cuando el cursor sale del canvas
        this.canvas.addEventListener("mouseleave", () => {
            this.painting = false;
        });

        // Buttons
        document
            .getElementById(`${canvasId}-btn-clear`)
            .addEventListener("click", this.clearCanvas.bind(this));
        document
            .getElementById(`${canvasId}-btn-undo`)
            .addEventListener("click", this.undo.bind(this));
    }

    startPosition(e) {
        this.painting = true;
        this.draw(e);
        this.drawDot(e);
    }

    endPosition() {
        this.painting = false;
        this.ctx.beginPath();
        this.undoStack.push(this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height));
    }

    draw(e) {
        if (!this.painting) return;

        const rect = this.canvas.getBoundingClientRect();
        let x, y;

        if (e.type === "mousemove") {
            x = e.clientX - rect.left;
            y = e.clientY - rect.top;
        } else if (e.type === "touchmove") {
            x = e.touches[0].clientX - rect.left;
            y = e.touches[0].clientY - rect.top;
        }

        this.ctx.lineWidth = 2;
        this.ctx.lineCap = "round";
        this.ctx.strokeStyle = "#000";

        this.ctx.lineTo(x, y);
        this.ctx.stroke();
        this.ctx.beginPath();
        this.ctx.moveTo(x, y);
    }

    drawDot(e) {
        const rect = this.canvas.getBoundingClientRect();
        let x, y;

        if (e.type === "touchstart" || e.type === "touchmove") {
            x = e.touches[0].clientX - rect.left;
            y = e.touches[0].clientY - rect.top;
        } else {
            x = e.clientX - rect.left;
            y = e.clientY - rect.top;
        }

        this.ctx.fillStyle = "#000";
        this.ctx.beginPath();
        this.ctx.arc(x, y, 0.9, 0, Math.PI * 2);
        this.ctx.fill();
    }

    // Método para verificar si el canvas tiene al menos un dibujo
    hasDrawing() {
        // Comprueba si el array de trazos tiene algún elemento
        return this.undoStack.length > 0;
    }

    undo() {
        if (this.undoStack.length > 0) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            for (let i = 0; i < this.undoStack.length - 1; i++) {
                this.ctx.putImageData(this.undoStack[i], 0, 0);
            }
            this.undoStack.pop();
        }
    }

    // Método para limpiar el canvas
    clearCanvas() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.undoStack = [];
    }

    getCanvas() {
        return this.canvas;
    }

    getCanvasBlob() {
        return new Promise((resolve, reject) => {
            this.canvas.toBlob((blob) => {
                if (blob) {
                    resolve(blob);
                } else {
                    reject(new Error("Error al obtener el blob del canvas"));
                }
            });
        });
    }

    preventScroll(e) {
        if (e.deltaY < 0 && this.canvas.scrollTop === 0) {
            e.preventDefault();
        } else if (
            e.deltaY > 0 &&
            this.canvas.scrollTop >= this.canvas.scrollHeight - this.canvas.offsetHeight
        ) {
            e.preventDefault();
        }
    }
}
