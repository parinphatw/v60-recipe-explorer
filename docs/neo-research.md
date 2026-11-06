# V60 NEO recipe provenance

## Research method

Hermes Mixture of Agents (`moa`, preset `default`) was invoked for the initial research and again for evidence synthesis, with two reference/advisor slots and an aggregator. Both advisor slots used the same configured model: independent contributions, not model diversity. Advisor output was treated as guidance, not source verification.

The shipped recipe was checked against Kurasu's original product-page recipe accordion in a live browser. HARIO Europe's original NEO article was also inspected. A direct HTTP request to Kurasu returned 403; browser retrieval exposed the actual accordion content. No brewing/taste test was performed.

## Published hot baseline

Source: [Kurasu — HARIO V60 Dripper NEO](https://kurasu.live/collections/brewing-gear/products/hario-v60-dripper-neo), “Kurasu Recipe” section.

- Light-roasted single origin, 12 g coffee, 200 ml water, 91°C.
- Medium-coarse; Fellow Ode Gen 2 setting 7.2; HARIO paper filter.
- Cumulative targets: 40 ml at 0:00; 100 ml during 0:40–1:10; 150 ml during 1:10–1:40; 200 ml with the final pour beginning at 1:40.
- No total completion time is specified. The app must not call 1:40 the completion time.
- This is the regular percolation recipe, not the separate SWITCH recipe.

Source: [HARIO Europe — V60 Dripper NEO](https://www.hario-europe.com/blogs/hario-community/v60-dripper-neo).

HARIO describes NEO's distinct ribbed Tritan design and compatibility with matching V60 filter paper. This is product guidance, not attribution for Kurasu's numeric recipe.

## App choices, not published claims

- Treat ml as approximately grams for practical scale brewing.
- Preserve the exact baseline ratio as `200 / 12`, not rounded `16.7`.
- Other doses proportionally scale water amounts. Retained timings are a starting point, not validated timings at every dose.
- K-Ultra guidance is qualitative only; Ode 7.2 is not a calibrated K-Ultra conversion.
- The iced NEO option is an untested house adaptation of the app's existing flash-brew structure: 15 g coffee, 180 g hot water, 45 g ice, 94°C. It is not a published Kurasu or HARIO iced recipe. No guaranteed finish time or chilling performance is claimed.
- Other advisor-suggested recipes were not shipped without independent verification.

## Browser regression tests

The static app has no runtime dependencies. Tests use a separate Python environment with Playwright and Chromium:

```sh
python3 -m venv /path/to/test-env
/path/to/test-env/bin/pip install playwright
/path/to/test-env/bin/playwright install chromium
/path/to/test-env/bin/python -m unittest discover -s tests -v
```

By default tests open the local HTML file. To verify a local HTTP server or deployed site, set `V60_TEST_URL` to that exact URL. Tests cover the published baseline, scaling, source/prompt consistency, iced provenance and water accounting, mobile overflow, preset reset, and cross-method hot/iced transitions. Page exceptions fail the tests.
