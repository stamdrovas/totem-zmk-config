# Guest Brazilian ABNT2

Two guest views are appended without renumbering the owner's layers or forty
typing positions: Guest 5, transparent private request 6, Guest Symbols 7.
The maintained right slider is event 40 and uses momentary Guest on every layer.
The left slider remains unscanned. Intended electrical closure selects Guest;
opening selects personal. **D7 against row D1 and the closed detent are inferred,
not electrically verified.** No physical switch direction is asserted.

## Reading and using the guest sheet

`totem-guest-layers.svg` and `.pdf` show the typist's view using the existing
printable physical layout, not full-size ABNT2 spacing. `Cmd` means Command.
Left thumbs: Ctrl / Space / Command; right: Backspace / Space / Enter.
Select the host's **Brazilian ABNT2** input source before testing; this firmware
sends HID positions, not Unicode. No host configuration is changed by the tools.

Tap either guest Space for Space. Hold 200 ms, or press another key while held,
for view 02 (Symbols). Release the activating Space to return. On Symbols the
other Space types Space; it does not take over the hold. Dedicated left Shift
supplies the small `Sft` legends. Dead accents precede the vowel; accent + Space
is the literal test. Shift+6 is dead diaeresis. Already shifted convenience
symbols do not promise another output with physical Shift.

Change modes with character/modifier keys released. Source configuration makes
Symbols conditional on both Guest and the private request, so Guest-off removes
Symbols even while the activating Space remains held. Actual held-key release
safety and both-thumb ordering still require hardware acceptance.

## Rendering and preservation

Install the existing pipeline dependencies: keymap-drawer, svglib, reportlab.
`tools/draw-guest-layers.sh` writes only the separate guest SVG/PDF. It reuses the
normal parser, ABNT2 legend configuration, printable geometry, drawer and PDF
converter. Guest-only labels/CSS are applied after projection; no private page,
slider key or personal combos appear in the guest sheet.

`tools/draw-layers.sh` projects to the original five layers and forty keys.
The workflow compares canonical normal inputs with the push's before revision:
normal keymap bindings, behavior/conditional/combo definitions, drawer config,
print geometry and info.json. Guest nodes/defines and event-40 bindings are
excluded. A guest-only edit skips the normal converter; a real normal input
change redraws automatically. Missing/zero/unavailable before history retains
normal artifacts and reports that a manual normal redraw is required. The
workflow_dispatch `redraw_normal` input explicitly authorizes that redraw.

Baseline repository commit: `23a19d5e3c880ee22c243d3dfbf3ff77730d1a30`.
Measured canonical normal SHA-256 before and after this implementation:
`4723a84ab60c14b52f688d64fd6714f90c6a2e77d152ee7541e305f7710f44e6`.
Normal artifacts were not regenerated; original/final SHA-256:

- PDF: `633c5a4ac7e01f944274a1a2c81f120932c82870a6f621773466fe25922b454e`
- SVG: `4be2503c9e5552ba651f819a2b64db027ef6c2d573685c0b60bce54dec951d50`

## Local source/build evidence (not hardware acceptance)

The repository manifest still tracks ZMK `main`, not a locked commit. Authorized
Docker verification compiled the previously inspected ZMK revision
`4dd95d7840eb3d5a3f59bb29fbf1ab054715ef85` (app/VERSION 0.3.0), with resolved
Zephyr `10ba6d0cb38bc3d258775d27982f707599320085` (4.1.0). This is a verified
build revision, **not** a deployed firmware revision. Future CI may resolve a
different main revision or dependency branch.

Measured source at that revision:

- `app/src/matrix_transform.c:45-66,90-110` builds the map lookup from the declared
  eleven columns and adds the per-half column offset, independently of scan
  column count. This supports, but does not compile-prove, the asymmetric scan.
- `app/src/combo.c:162-179` filters candidates by highest active layer. Inferred:
  BASE-only combos are isolated under Guest/request/Symbols; transitions and
  already-pending combos still need device tests.
- `app/src/conditional_layer.c:91-121` reevaluates the conjunction and deactivates
  its target when prerequisites are absent.
- `app/src/keymap.c:65-68` records the press-time layer state for releases;
  `app/src/behaviors/behavior_hold_tap.c:337-352,642-675` selects hold on timeout
  or another key down and releases its recorded active hold-tap instance.
- Bluetooth peripheral `service.c:230-258` sends full position state on events;
  central `central.c:564-570` subscribes to notifications, and `191-212` releases
  stored peripheral positions on disconnect. **Inferred risk:** reconnecting
  with the slider held may not restore mode until a subsequent peripheral event,
  possibly after a typing key. OFF→ON recovery is not proven.

Measured Docker build verification supersedes the earlier uninitialized-west
and stopped-daemon blockers. Installed Docker Desktop was started with approval.
The repository's reusable workflow and upstream workflow at the inspected source
both specify `zmkfirmware/zmk-build-arm:stable`; the current upstream workflow
fetched through GitHub also matched that inspected workflow byte-for-byte.
The build used its native `linux/arm64` image pinned by platform manifest digest
`sha256:53dfd031cf2b532a3ba2762c62dad402ee76ac6fa5928e7b4ec820cfbe312cde`.
Measured tools: Zephyr SDK 0.16.9, arm-zephyr-eabi GCC 12.2.0, GNU ld 2.38,
west 1.5.0, CMake 3.31.6, Ninja 1.11.1 and Python 3.12.3. No global toolchain
was installed; source and config were mounted read-only, with a separate writable
scratch workspace. The repository manifest was not changed to pin the build.

Measured retained footprint: the host evidence/workspace directory occupies
3.0 GiB (`du -sh`), including 44 MiB left and 38 MiB right build directories.
Docker reports the pulled image as 660,952,676 bytes via image inspection and
2.97 GB via its image listing; these are different storage accounting views,
not a measured network-transfer total. Its SDK/toolchain is contained in that
image, not installed on macOS. The stopped `totem-guest-build` container retains
2,355,200 writable bytes. The image, dependency workspace and build caches are
retained for reuse; Docker Desktop remains started, but the build container is
exited. No unrelated container/image/volume/cache was removed. Cleanup can remove
that stopped container and the scratch directory, then the pinned image when no
longer needed; no broad Docker prune is required or authorized by this work.

Host evidence directory: `/tmp/totem-guest-docker/` (temporary, not committed).
`build.sh` records the reproducible container-side setup and commands;
`resolved-west.yml` freezes active dependencies and `resolved-commits.txt` lists
the manifest revisions. The source clone is `zmk/`, with its west workspace rooted
there. From `/work/zmk` in the container, the exact successful build commands were
`west build -s app -d /work/build-left -b xiao_ble//zmk -- -DSHIELD=totem_left -DZMK_CONFIG=/config`
and
`west build -s app -d /work/build-right -b xiao_ble//zmk -- -DSHIELD=totem_right -DZMK_CONFIG=/config`.
`/config` was this worktree's config directory, read-only; `/work` was the host
evidence directory. `build-left.log` / `build-right.log` contain the complete
build logs, with exit status 0 recorded in the corresponding `.exit` files.
Both produced host-accessible `build-{left,right}/zephyr/zmk.uf2`, `zmk.elf`,
`zephyr.dts`, `.config` and `edt.pickle` files. No firmware-source fix was needed.

Measured linker usage (788 KiB flash and 256 KiB RAM available):

| Half | Flash | RAM |
|---|---:|---:|
| Left / central | 248,976 B (30.86%) | 63,944 B (24.39%) |
| Right / peripheral | 197,276 B (24.45%) | 41,984 B (16.02%) |

Measured checks against **both generated DTS and parsed compiled EDT** passed;
`check_compiled.py`, `compiled-checks.log` and `compiled-checks.json` retain the
assertions/results in the evidence directory:

- Transform columns 11, event map 41, final entry `RC(1,10)` at event 40.
- Eight layers with 41 bindings each; every event-40 binding is momentary Guest 5.
- Left scan D4,D5,D10,D9,D8 (five columns, offset 0), with no D7/left-slider scan.
  Right scan D8,D9,D10,D5,D4,D7 (six columns, offset 5); D7 resolves to GPIO1.12
  and local column 5 maps to global column 10. Electrical closure is still untested.
- Guest conditional `if-layers = <5 6>`, `then-layer = <7>`; guest hold-tap is
  hold-preferred, 200 ms, quick-tap 0 and require-prior-idle 0. Both Guest Spaces
  use that behavior and both Symbols Spaces use plain key press.

Builds pass but are not warning-free: both report deprecated KSCAN; left reports
upstream tap-dance discarded-const warnings; right reports shared USB and central
battery fetching/proxy options resolving to disabled because this half is a
peripheral. These were recorded, not changed outside guest scope. All 16 diagram
and preservation tests passed using the existing temporary Python environment
with its executables on PATH; shell syntax and `git diff --check` passed. Normal
PDF/SVG hashes remained the values above. No flashing, reset build, push, host
input-source change or hardware acceptance was performed.

## Pending authorized device acceptance

All actual device acceptance remains pending despite both passing builds:

- Continuity D7/D1, closed detent, switch events, right-only scanning.
- Actual Brazilian ABNT2 HID output: lowercase/uppercase including ç/Ç; all
  accents and literal/shifted accents; slash/question, backslash/pipe,
  brackets/braces, quote/double quote, comma/period shifts, semicolon/colon,
  all number-row outputs and dead diaeresis.
- Either Space, rapid typing, immediate hold+number, long/repeated/double taps,
  other-Space typing, both thumb orders and release orders, no extra Space or
  stuck layer, unchanged personal Space/Nav timing.
- Slider from every personal layer and both guest views; keys/modifiers held
  across mode changes; no stuck HID key, guest leak or unexpected combos.
- Central/right restart, boot with slider closed, reconnect and wake; prove any
  recovery procedure. Measure sleep/current with the switch closed before
  claiming unchanged power or battery life. Sleep was not disabled.

Do not treat the intended maintained-switch semantics as hardware-ready until
these tests pass. Deeper transport/state synchronization, if needed, requires a
separate scope decision rather than substituting a toggle or another layout.
