"use strict";
// Real production module with controlled Worker/Canvas APIs. No browser claims.
const assert = require("node:assert/strict");
const vm = require("node:vm");
const {parseCTEX, decodeCTEX, createBridge} = require(process.argv[2]);

const sizes = [[2304,576],[1152,288],[576,144],[288,72],[144,36],[72,18],[36,9],[18,4],[9,2],[4,1],[2,1],[1,1]];
const expectedBytes = sizes.reduce((sum, [w,h]) => sum + w*h*4, 0);
function container(encoding = 1) {
    const blocks = sizes.map(([w,h]) => {
        if (encoding === 1) {
            // Minimal codec header: decoding is deliberately a separate seam.
            const bytes = Buffer.alloc(37);
            bytes.write("PNG ");
            bytes.set([137,80,78,71,13,10,26,10],4);
            bytes.writeUInt32BE(13,12); bytes.write("IHDR",16);
            bytes.writeUInt32BE(w,20); bytes.writeUInt32BE(h,24);
            bytes[28] = 8; bytes[29] = 6;
            return bytes;
        }
        const bytes = Buffer.alloc(26);
        bytes.write("RIFF"); bytes.writeUInt32LE(18,4); bytes.write("WEBPVP8L",8);
        bytes.writeUInt32LE(5,16); bytes[20] = 0x2f;
        bytes.writeUInt32LE((w-1) | ((h-1)<<14) | (1<<28),21);
        return bytes;
    });
    const bytes = Buffer.alloc(52 + blocks.reduce((sum, b) => sum+b.length+4,0));
    bytes.write("GST2"); bytes.writeUInt32LE(1,4);
    bytes.writeUInt32LE(2304,8); bytes.writeUInt32LE(576,12);
    bytes.writeUInt32LE(1<<23,16); bytes.writeUInt32LE(0xffffffff,20);
    bytes.writeUInt32LE(encoding,36); bytes.writeUInt16LE(2304,40); bytes.writeUInt16LE(576,42);
    bytes.writeUInt32LE(11,44); bytes.writeUInt32LE(5,48);
    let offset = 52;
    for (const block of blocks) {
        bytes.writeUInt32LE(block.length,offset); bytes.set(block,offset+4); offset += block.length+4;
    }
    return new Uint8Array(bytes);
}

async function main() {
    for (const encoding of [1,2]) {
        const parsed = parseCTEX(container(encoding));
        assert.deepEqual(parsed.mips.map(m => [m.width,m.height]),sizes);
        assert.equal(parsed.pixelBytes,expectedBytes);
        assert.equal(parsed.mips[0].mime,encoding===1 ? "image/png" : "image/webp");
    }
    const changes = [
        [0,0], [4,2], [8,1], [12,1], [16,1], [18,0], [20,0], [24,1], [28,1], [32,1],
        [36,0], [40,1], [42,1], [44,1], [48,4], [52,0], [53,255], [56,0], [60,0],
        [72,0], [76,1], [80,1], [84,16],
    ];
    for (const [at,value] of changes) {
        const bytes = container(); bytes[at] = value;
        assert.throws(() => parseCTEX(bytes),undefined,"container mutation at "+at);
    }
    assert.throws(() => parseCTEX(container().subarray(0,30)),/ctex_size/);
    assert.throws(() => parseCTEX(container().subarray(0,container().length-1)),/ctex_block_bounds/);
    assert.throws(() => parseCTEX(new Uint8Array([...container(),0])),/ctex_trailing_bytes/);
    const wrongWebP = container(2); wrongWebP[71] = " ".charCodeAt(0);
    assert.throws(() => parseCTEX(wrongWebP),/ctex_webp_lossless/);
    const oversized = container(2); oversized[77] = 0;
    assert.throws(() => parseCTEX(oversized),/ctex_webp_dimensions/);

    let decoded = 0, closed = 0;
    const decoder = {
        Blob,
        async createImageBitmap(blob, options) {
            assert.equal(options.colorSpaceConversion,"none");
            assert.equal(options.premultiplyAlpha,"none");
            assert.equal(options.imageOrientation,"none");
            assert.equal(blob.type,"image/png");
            const index = decoded++;
            return {width:sizes[index][0],height:sizes[index][1],index,close(){closed++;}};
        },
        OffscreenCanvas: class {
            constructor(w,h) { this.width=w; this.height=h; }
            getContext(type,options) {
                assert.equal(type,"2d"); assert.equal(options.alpha,true);
                let value=0;
                return {drawImage(bitmap){value=bitmap.index+1;},getImageData:(_x,_y,w,h)=>({data:new Uint8ClampedArray(w*h*4).fill(value)})};
            }
        }
    };
    let resolved=false;
    const decoding=decodeCTEX(parseCTEX(container()),decoder).then(value=>{resolved=true;return value;});
    assert.equal(resolved,false,"async decoder never completes inline");
    const pixels=new Uint8Array(await decoding);
    assert.equal(pixels.length,expectedBytes); assert.equal(closed,12);
    let offset=0;
    for(let index=0;index<sizes.length;index++){
        assert.equal(pixels[offset],index+1);
        offset += sizes[index][0]*sizes[index][1]*4;
        assert.equal(pixels[offset-1],index+1);
    }
    await assert.rejects(decodeCTEX(parseCTEX(container()),{}),/worker_decoder_unavailable/);
    const failedDecoder={...decoder,createImageBitmap:async()=>{throw Error("corrupt_image");}};
    await assert.rejects(decodeCTEX(parseCTEX(container()),failedDecoder),/corrupt_image/);

    const workers=[], urls=[], revoked=[], blobs=[];
    const environment={
        Blob,
        URL:{createObjectURL(blob){blobs.push(blob);const url="blob:test-"+urls.length;urls.push(url);return url;},revokeObjectURL(url){revoked.push(url);}},
        Worker:class{
            constructor(url){this.url=url;this.terminated=false;workers.push(this);}
            postMessage(request){this.request=request;}
            terminate(){this.terminated=true;}
            emit(message){this.onmessage({data:message});}
        }
    };
    const bridge=createBridge(environment);
    assert.equal(workers.length,1,"warm decoder loads no image");
    assert.equal(workers[0].request,undefined);
    assert.equal(bridge.start("first"),""); assert.equal(bridge.poll(),"pending");
    assert.equal(bridge.start("second"),"loader_busy");
    const first=workers[0], oldGeneration=first.request.generation;
    first.emit({generation:oldGeneration+1,bytes:new ArrayBuffer(expectedBytes)});
    assert.equal(bridge.poll(),"pending","wrong request cannot publish");
    first.emit({generation:oldGeneration,bytes:new ArrayBuffer(expectedBytes)});
    assert.equal(bridge.poll(),"loaded"); assert.equal(bridge.take().byteLength,expectedBytes);
    assert.equal(bridge.poll(),"idle"); assert.equal(bridge.take(),null,"result is released, not cached");
    bridge.start("before-cancel"); const staleGeneration=first.request.generation;
    bridge.cancel(); assert(first.terminated); assert.equal(bridge.poll(),"idle");
    bridge.start("new-visit"); assert.equal(workers.length,2);
    first.emit({generation:staleGeneration,bytes:new ArrayBuffer(expectedBytes)});
    assert.equal(bridge.poll(),"pending","old worker callback is ignored");
    const second=workers[1];
    second.emit({generation:second.request.generation,error:"controlled_failure"});
    assert.equal(bridge.poll(),"error"); assert.equal(bridge.error(),"controlled_failure");
    bridge.start("bad-length"); second.emit({generation:second.request.generation,bytes:new ArrayBuffer(1)});
    assert.equal(bridge.error(),"worker_result_bytes");
    bridge.close(); assert(second.terminated); assert.deepEqual(urls,revoked,"every Blob URL revoked");
    const missingEnv={...environment,Worker:undefined};
    const missing=createBridge(missingEnv);
    assert.equal(missing.start("unsupported"),"worker_unavailable");
    missingEnv.Worker=environment.Worker;
    assert.equal(missing.start("retry"),"","unsupported visit is not a permanent blanket skip");
    missing.close();

    // Execute the exact serialized Worker source too, with controlled codecs.
    decoded=0; closed=0;
    let reply=null, transfer=null;
    const scope={self:{postMessage(value,buffers){reply=value;transfer=buffers;}},atob,Uint8Array,DataView,ArrayBuffer,Blob,createImageBitmap:decoder.createImageBitmap,OffscreenCanvas:decoder.OffscreenCanvas};
    vm.runInNewContext(await blobs[0].text(),scope);
    await scope.self.onmessage({data:{generation:42,encoded:Buffer.from(container()).toString("base64")}});
    assert.equal(reply.generation,42); assert.equal(reply.error,undefined);
    assert.equal(reply.bytes.byteLength,expectedBytes); assert.equal(transfer[0],reply.bytes);
    await scope.self.onmessage({data:{generation:43,encoded:"not_base64!"}});
    assert.equal(reply.generation,43); assert.equal(typeof reply.error,"string");
    console.log("PASS background container, asynchronous ownership, cancellation and pixels");
}
main().catch(error=>{console.error(error);process.exitCode=1;});
