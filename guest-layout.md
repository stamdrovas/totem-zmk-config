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

The manifest tracks ZMK `main`, not a locked commit. No existing ZMK/Zephyr west
workspace was found in the searched local locations. A temporary upstream source
checkout was fetched for inspection at
`4dd95d7840eb3d5a3f59bb29fbf1ab054715ef85`; app/VERSION reports 0.3.0.
That checkout is **not** an initialized Zephyr build workspace or a deployed
firmware revision. Future CI may resolve a different main revision.

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

A temporary Python environment supplied west 1.5.0. Both regular-half commands
were attempted, with source `/tmp/totem-guest-zmk/app`, board `xiao_ble//zmk`,
shields `totem_left` / `totem_right`, build directories
`/tmp/totem-guest-left` / `/tmp/totem-guest-right`, and this worktree's config.
Both stopped before compilation: `west: unknown command "build"; do you need to
run this inside a workspace?`. No Zephyr dependency workspace/SDK, ninja or
arm-zephyr-eabi-gcc was available in the inspected environment. Docker exists,
but `docker info` failed because its daemon socket is unavailable. No daemon,
OS setting, browser, flashing operation or reset build was started. There is no
compiled DTS, UF2 or passing firmware build to report.

## Pending authorized device acceptance

All actual device acceptance remains pending, even if a later build passes:

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
