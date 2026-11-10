/* HP-I2: ordinary worker for the single-threaded Web export. No network or FS API.
 * GST2 v1 layout: Godot 4.7.2 scene/resources/compressed_texture.cpp and
 * editor/import/resource_importer_texture.cpp. PNG blocks include Godot's
 * "PNG " prefix; lossless WebP blocks are ordinary RIFF/VP8L files.
 */
(function (root) {
    "use strict";

    function parseCTEX(bytes) {
        const require = (ok, code) => { if (!ok) throw new Error(code); };
        require(bytes instanceof Uint8Array && bytes.byteLength >= 56 && bytes.byteLength <= 67108864, "ctex_size");
        const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
        const text = (at, n) => String.fromCharCode(...bytes.subarray(at, at + n));
        const u32 = at => view.getUint32(at, true);
        const width = 2304, height = 576;
        require(text(0, 4) === "GST2" && u32(4) === 1, "ctex_version");
        require(u32(8) === width && u32(12) === height, "ctex_dimensions");
        const knownFlags = (1 << 22) | (1 << 23) | (1 << 24) | (1 << 26) | (1 << 27);
        require((u32(16) & (1 << 23)) !== 0 && (u32(16) & ~knownFlags) === 0, "ctex_mipmap_flags");
        require(u32(20) === 0xffffffff && u32(24) === 0 && u32(28) === 0 && u32(32) === 0, "ctex_header");
        const encoding = u32(36);
        require(encoding === 1 || encoding === 2, "ctex_lossless_encoding");
        require(view.getUint16(40, true) === width && view.getUint16(42, true) === height && u32(48) === 5, "ctex_rgba_dimensions");
        let w = width, h = height, count = 0, pixelBytes = 0;
        do {
            pixelBytes += w * h * 4;
            count += 1;
            if (w === 1 && h === 1) break;
            w = Math.max(1, w >> 1); h = Math.max(1, h >> 1);
        } while (true);
        require(u32(44) === count - 1, "ctex_mipmap_count");
        const mips = [];
        let offset = 52;
        w = width; h = height;
        for (let index = 0; index < count; index += 1) {
            require(offset + 4 <= bytes.length, "ctex_block_header");
            const size = u32(offset);
            offset += 4;
            require(size > 0 && size <= bytes.length - offset, "ctex_block_bounds");
            let block = bytes.subarray(offset, offset + size);
            offset += size;
            let mime;
            if (encoding === 1) {
                require(block.length >= 37 && String.fromCharCode(...block.subarray(0, 4)) === "PNG ", "ctex_png_prefix");
                block = block.subarray(4);
                const header = new DataView(block.buffer, block.byteOffset, block.byteLength);
                require([137, 80, 78, 71, 13, 10, 26, 10].every((v, i) => block[i] === v), "ctex_png_signature");
                require(header.getUint32(8) === 13 && String.fromCharCode(...block.subarray(12, 16)) === "IHDR", "ctex_png_header");
                require(header.getUint32(16) === w && header.getUint32(20) === h && block[24] === 8 && [2, 6].includes(block[25]), "ctex_png_dimensions");
                mime = "image/png";
            } else {
                require(block.length >= 26 && String.fromCharCode(...block.subarray(0, 4)) === "RIFF" && String.fromCharCode(...block.subarray(8, 16)) === "WEBPVP8L", "ctex_webp_lossless");
                const header = new DataView(block.buffer, block.byteOffset, block.byteLength);
                const length = header.getUint32(16, true);
                require(header.getUint32(4, true) === block.length - 8 && length >= 5 && 20 + length + (length & 1) === block.length && block[20] === 0x2f, "ctex_webp_bounds");
                const bits = header.getUint32(21, true);
                require((bits & 0x3fff) + 1 === w && ((bits >>> 14) & 0x3fff) + 1 === h && (bits >>> 29) === 0, "ctex_webp_dimensions");
                mime = "image/webp";
            }
            mips.push({bytes: block, width: w, height: h, mime});
            w = Math.max(1, w >> 1); h = Math.max(1, h >> 1);
        }
        require(offset === bytes.length, "ctex_trailing_bytes");
        return {width, height, pixelBytes, mips};
    }

    async function decodeCTEX(parsed, environment) {
        const env = environment || globalThis;
        if (typeof env.createImageBitmap !== "function" || typeof env.OffscreenCanvas !== "function") throw new Error("worker_decoder_unavailable");
        const output = new Uint8Array(parsed.pixelBytes);
        let offset = 0;
        for (const mip of parsed.mips) {
            const bitmap = await env.createImageBitmap(new env.Blob([mip.bytes], {type: mip.mime}), {
                colorSpaceConversion: "none", premultiplyAlpha: "none", imageOrientation: "none"
            });
            let canvas;
            try {
                if (bitmap.width !== mip.width || bitmap.height !== mip.height) throw new Error("decoded_mipmap_dimensions");
                canvas = new env.OffscreenCanvas(mip.width, mip.height);
                const context = canvas.getContext("2d", {alpha: true, willReadFrequently: true, colorSpace: "srgb"});
                if (!context) throw new Error("worker_canvas_unavailable");
                context.globalCompositeOperation = "copy";
                context.drawImage(bitmap, 0, 0);
                const pixels = context.getImageData(0, 0, mip.width, mip.height).data;
                if (pixels.byteLength !== mip.width * mip.height * 4) throw new Error("decoded_mipmap_bytes");
                output.set(pixels, offset);
                offset += pixels.byteLength;
            } finally {
                bitmap.close();
                if (canvas) { canvas.width = 0; canvas.height = 0; }
            }
        }
        return output.buffer;
    }

    function workerMain() {
        self.onmessage = async event => {
            const {generation, encoded} = event.data;
            try {
                if (!Number.isSafeInteger(generation) || generation < 1 || typeof encoded !== "string" || encoded.length > 89478488) throw new Error("worker_request");
                // Godot's bridge accepts strings, not PackedByteArray arguments.
                // Base64 decoding, container parsing and image decoding all run here.
                const raw = atob(encoded);
                const bytes = Uint8Array.from(raw, character => character.charCodeAt(0));
                const result = await decodeCTEX(parseCTEX(bytes));
                self.postMessage({generation, bytes: result}, [result]);
            } catch (error) {
                self.postMessage({generation, error: String(error.message || error)});
            }
        };
    }

    function createBridge(environment) {
        const env = environment || root;
        let worker = null, serial = 0, current = 0, result = null, state = "idle", error = "";
        const stop = () => { if (worker) worker.terminate(); worker = null; };
        const spawn = () => {
            if (worker) return;
            if (typeof env.Worker !== "function" || typeof env.Blob !== "function" || !env.URL || typeof env.URL.createObjectURL !== "function") throw new Error("worker_unavailable");
            const source = "const parseCTEX=" + parseCTEX.toString() + ";const decodeCTEX=" + decodeCTEX.toString() + ";(" + workerMain.toString() + ")();";
            const url = env.URL.createObjectURL(new env.Blob([source], {type: "text/javascript"}));
            try { worker = new env.Worker(url); } finally { env.URL.revokeObjectURL(url); }
            const owner = worker;
            worker.onmessage = event => {
                if (worker !== owner || event.data.generation !== current || state !== "pending") return;
                if (event.data.bytes instanceof ArrayBuffer && event.data.bytes.byteLength === 7077844) {
                    result = event.data.bytes;
                    state = "loaded";
                } else {
                    error = String(event.data.error || "worker_result_bytes");
                    state = "error";
                }
            };
            worker.onerror = () => {
                if (worker !== owner) return;
                error = "worker_execution_failed";
                state = "error";
                stop();
            };
        };
        // Warm only the decoder, never an image or a catalog-wide preload.
        try { spawn(); } catch (_) { /* A visit retries and reports the error. */ }
        return {
            start(encoded) {
                if (state === "pending") return "loader_busy";
                result = null; error = ""; current = ++serial;
                try {
                    spawn();
                    state = "pending";
                    worker.postMessage({generation: current, encoded});
                    return "";
                } catch (failure) {
                    stop(); state = "error";
                    error = String(failure.message || failure);
                    return error;
                }
            },
            poll() { return state; },
            error() { return error; },
            take() { const bytes = result; result = null; state = "idle"; return bytes; },
            cancel() { current = ++serial; result = null; error = ""; state = "idle"; stop(); },
            close() { this.cancel(); }
        };
    }

    if (typeof module !== "undefined" && module.exports) module.exports = {parseCTEX, decodeCTEX, createBridge};
    else if (!root.picrossBackgroundLoader) root.picrossBackgroundLoader = {create: () => createBridge()};
})(globalThis);
