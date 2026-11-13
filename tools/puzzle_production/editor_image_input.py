"""Read-only validation of prepared editor images; never an image producer."""
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from .authoring_package import require
from .contract import InvalidInput, exact_keys, integer
from . import catalog_io as io, reveal_source

PROFILE = "picross-prepared-background-png2304-v1"


def validate_background(raw):
    """Validate every original byte and decoded pixel without writing a rendition."""
    from PIL import Image, ImageFile, __version__
    from . import background_assets
    from .background_contract import BackgroundError
    from .image_normalization import normalize_bytes
    require(__version__ == background_assets.PILLOW_VERSION,
            "Prepared image validation requires Pillow " + background_assets.PILLOW_VERSION)
    require(isinstance(raw, bytes) and 0 < len(raw) <= reveal_source.IMAGE_LIMIT, "Background exceeds 32 MiB")
    require(not ImageFile.LOAD_TRUNCATED_IMAGES, "Strict PNG decoding was disabled")
    try:
        background_assets._png(raw, SimpleNamespace(check=io.tick))
        with Image.open(BytesIO(raw), formats=("PNG",)) as framing:
            framing.verify()
        with Image.open(BytesIO(raw), formats=("PNG",)) as probe:
            require(probe.size == (2304, 576), "Prepared background must be exactly 2304 x 576")
            require(getattr(probe, "n_frames", 1) == 1, "Animated background is unsupported")
            require(probe.getexif().get(274, 1) == 1, "Prepared background must already be correctly oriented")
            require("icc_profile" not in probe.info or bool(probe.info["icc_profile"]), "Empty PNG ICC profile")
            if "srgb" in probe.info:
                require(probe.info["srgb"] in (0, 1, 2, 3), "Invalid PNG sRGB intent")
            if "gamma" in probe.info:
                require(abs(probe.info["gamma"] - 0.45455) <= 0.0001, "Prepared background gamma must be sRGB-compatible")
            if "chromaticity" in probe.info:
                expected = (0.3127, 0.3290, 0.6400, 0.3300, 0.3000, 0.6000, 0.1500, 0.0600)
                require(len(probe.info["chromaticity"]) == 8 and
                        all(abs(a - b) <= 0.00002 for a, b in zip(probe.info["chromaticity"], expected)),
                        "Prepared background chromaticity must be sRGB-compatible")
        with Image.open(BytesIO(raw), formats=("PNG",)) as source:
            source.load()
            pixels = source.convert("RGBA")
            diagnostic = background_assets._diagnostic(pixels)
            # The existing color decoder is used only as an independent check.
            # If an ICC transform would change any pixel, direct import rejects it.
            normalized, metadata, original = normalize_bytes(raw, max_bytes=reveal_source.IMAGE_LIMIT,
                                                             max_axis=8192, max_pixels=8_000_000)
            require(metadata["orientation"] == 1 and normalized.tobytes() == pixels.tobytes() and original == raw,
                    "Prepared background would require color/orientation conversion")
        io.tick()
        return {"profile": PROFILE, **diagnostic, "sha256": io.checksum(raw), "bytes": len(raw)}
    except (BackgroundError, OSError, ValueError, SyntaxError) as exc:
        raise InvalidInput("Invalid prepared background: " + str(exc)) from exc


def read_ref(root, value):
    exact_keys(value, {"file", "sha256", "bytes"})
    from .authoring_package import relative, sha
    relative(value["file"])
    sha(value["sha256"])
    integer(value["bytes"], 1, reveal_source.IMAGE_LIMIT, "image bytes")
    raw = io.read(root, value["file"], reveal_source.IMAGE_LIMIT)
    require(len(raw) == value["bytes"] and io.checksum(raw) == value["sha256"], "Image input hash/size differs")
    return raw


def reveal_input(root, value, entry):
    from .target_adapter import validate_reveal
    raw = read_ref(root, value)
    path = io.safe(root, value["file"])
    require(path.suffix in (".png", ".svg"), "Prepared reveal requires PNG or bounded SVG")
    validate_reveal(path, entry["production"]["width"], entry["production"]["height"])
    require(read_ref(root, value) == raw, "Reveal changed during validation")
    return raw


def background_input(root, value):
    require(Path(value["file"]).suffix == ".png", "Prepared background requires a .png file")
    raw = read_ref(root, value)
    validate_background(raw)
    require(read_ref(root, value) == raw, "Background changed during validation")
    return raw
