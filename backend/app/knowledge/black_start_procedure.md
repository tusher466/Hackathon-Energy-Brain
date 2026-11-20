# Black Start Procedure - Energy Brain Knowledge Base

## Overview
Black start is the process of restoring power after total or partial blackout without external grid support. Requires black-start capable units (hydro, diesel, gas turbines, batteries).

## Standard Sequence (IEC 61968 / IEEE 1547 aligned)
1. **Identify cranking source**: Hydro unit G1-Hydro is primary black-start capable. Verify fuel/water, battery start.
2. **Energize cranking path**: Close breaker to substation S1. Use battery Batt-1 for voltage reference and reactive support. Check voltage 0.95-1.05pu.
3. **Crank non-black-start units**: From energized bus, start G2-Gas. Synchronize via angular check <10deg. Frequency target 50.0Hz +/-0.5Hz.
4. **Load pickup in blocks**: Critical loads first (industrial L1), 5MW blocks max 10% of online generation. Maintain frequency above 49.5Hz. If frequency dips below 49.5Hz, pause pickup and shed non-critical.
5. **Network expansion**: Energize S2, S3 downstream. Pick up commercial loads L2. Defer EV fleet charging until frequency stable >49.8Hz for 10 min.
6. **Final restoration**: Residential L3 last, full load synchronization.

## Protection Checks Each Step
- Overcurrent relay: <1.2 pu for 5 sec
- Frequency relay: trip if <47.5Hz
- Voltage: maintain 0.95-1.05pu, use Batt-1 STATCOM.

## Bangladesh Context
Evening peak high, use deferrable loads. Dhaka grid carbon high, prioritize hydro.

## Germany/EU Context
Higher renewable penetration, watch for voltage flicker during PV reconnection. Use day-ahead price signal to defer.

## US PJM Context
LMP volatility during black start. Follow PJM Manual 36.

## Human-in-the-Loop
LLM or copilot MUST NOT directly control breakers. Operator approves each step. Log approval with timestamp.

## Failure Modes
- Hydro fails to start: fallback diesel D1.
- Frequency collapse during load pickup: shed last block, retry after 5 min.
- Battery SoC low: reduce voltage setpoint.
