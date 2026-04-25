# Dead Make.com Scenarios — Manual Cleanup List

**Phase 3D-H1.** Cannot query Make.com API for live `isinvalid: true` list (`MAKE_API_TOKEN` absent). The IDs below come from the runbook's pre-confirmed inventory; the state should be re-verified in the Make.com UI before deletion.

**Do not automate deletion.** Confirm each scenario is dead + unrelated to the static-image flow (scenarios 4261294, 4261143, 4261296) before removing.

| Scenario ID | Notes (per runbook) |
|---|---|
| 4263862 | V5/V7 video variant, 100% error rate |
| 4263863 | V5/V7 video variant, 100% error rate |
| 4263864 | V5/V7 video variant, 100% error rate |
| 4669524 | V5/V7 video variant, 100% error rate |
| 4671823 | V5/V7 video variant, 100% error rate |
| 4671827 | V5/V7 video variant, 100% error rate |
| 4732882 | V5/V7 video variant, 100% error rate |
| 4732899 | V5/V7 video variant, 100% error rate |
| 4732903 | V5/V7 video variant, 100% error rate |

**Also leave untouched (out of scope, but may be deletable):**
- Video Pin Poster v6 (x3): `4726262`, `4726259`, `4726264` — last ran 2026-04-13; Late API keys expired so these won't post even if triggered. Video is OUT OF SCOPE for this fix.

## Recommended procedure for Tall

1. Open `https://us2.make.com/1686661/scenarios`.
2. For each ID above, confirm `isinvalid: true` or zero successful executions in the last 30 days.
3. Delete (three-dot menu → Delete). Deleting inactive scenarios does not affect ops quota.
4. Video scenarios (`4726262/9/4`): leave until Late API keys are refreshed OR a decision is made to retire the video pipeline entirely.
