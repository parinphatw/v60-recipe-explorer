"""Browser regression tests. Run with Python + playwright (chromium installed)."""
import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright

URL = os.environ.get('V60_TEST_URL', Path(__file__).resolve().parents[1].joinpath('index.html').as_uri())

class NeoRecipeTests(unittest.TestCase):
    def test_neo_published_baseline_and_scaled_schedule(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 390, 'height': 844})
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(URL)
            neo = page.locator('#methodPills [data-val="neo"]')
            self.assertEqual(neo.count(), 1, 'NEO needs its own method control')
            neo.click()
            self.assertIn('Kurasu', page.locator('#recipeTitle').inner_text())
            self.assertEqual(page.locator('#doseSlider').input_value(), '12')
            self.assertEqual(page.locator('#stTotal').inner_text(), '200 g')
            self.assertEqual(page.locator('#tempSlider').input_value(), '91')
            self.assertEqual(page.locator('#ratioWrap').is_visible(), False)
            self.assertIn('Not published', page.locator('#stTime').inner_text())
            self.assertEqual(page.locator('#schedule .total').all_inner_texts(), ['+40g · 40g', '+60g · 100g', '+50g · 150g', '+50g · 200g'])
            self.assertIn('7.2', page.locator('#stGrindRef').inner_text())
            self.assertIn('not a calibrated', page.locator('#promptText').inner_text())
            self.assertEqual(page.locator('#refsList a').count(), 2)
            self.assertFalse(page.locator('#grpBean').is_visible())
            self.assertFalse(page.locator('#grpAcidity').is_visible())
            page.locator('#doseSlider').evaluate('(e) => {e.value=18; e.dispatchEvent(new Event("input", {bubbles:true}));}')
            self.assertEqual(page.locator('#stTotal').inner_text(), '300 g')
            self.assertIn('app-scaled', page.locator('#recipeDescr').inner_text())
            self.assertEqual(page.locator('#schedule .total').all_inner_texts(), ['+60g · 60g', '+90g · 150g', '+75g · 225g', '+75g · 300g'])
            self.assertIn('not published', page.locator('#promptText').inner_text().lower())
            self.assertEqual(errors, [])
            browser.close()

    def test_neo_iced_provenance_and_method_transitions(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 390, 'height': 844})
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(URL)
            page.locator('#methodPills [data-val="neo"]').click()
            page.locator('#brewStylePills [data-val="iced"]').click()
            self.assertIn('NEO', page.locator('#recipeTitle').inner_text())
            self.assertIn('house adaptation', page.locator('#recipeDescr').inner_text())
            self.assertEqual(page.locator('#iceAmount').inner_text(), '45 g')
            self.assertIn('180 g hot water', page.locator('#iceDetail').inner_text())
            self.assertIn('not Kurasu', page.locator('#promptText').inner_text())
            page.locator('#doseSlider').evaluate('(e) => {e.value=20; e.dispatchEvent(new Event("input", {bubbles:true}));}')
            self.assertEqual(page.locator('#iceAmount').inner_text(), '60 g')
            self.assertIn('240 g hot water', page.locator('#iceDetail').inner_text())
            page.locator('#brewStylePills [data-val="hot"]').click()
            self.assertEqual(page.locator('#stTotal').inner_text(), '200 g')
            self.assertFalse(page.locator('#iceCallout').is_visible())
            page.get_by_role('button', name='Washed Default', exact=True).click()
            self.assertIn('Washed', page.locator('#recipeTitle').inner_text())
            self.assertTrue(page.locator('#grpBean').is_visible())
            for method in ['v60', 'origami', 'aeropress', 'neo']:
                page.locator(f'#methodPills [data-val="{method}"]').click()
                if method == 'origami':
                    for filter_name in ['cone', 'wave']:
                        page.locator(f'#origamiFilterPills [data-val="{filter_name}"]').click()
                        self.assertIn(filter_name.capitalize(), page.locator('#recipeTitle').inner_text())
                for style in ['iced', 'hot']:
                    page.locator(f'#brewStylePills [data-val="{style}"]').click()
                    self.assertNotIn('NaN', page.locator('#recipeGuide').inner_text())
                    self.assertEqual(page.locator('#iceCallout').is_visible(), style == 'iced')
            page.get_by_role('button', name='V60 NEO · Kurasu', exact=True).click()
            self.assertEqual(page.locator('#stTotal').inner_text(), '200 g')
            self.assertEqual(page.evaluate('document.documentElement.scrollWidth > innerWidth'), False)
            self.assertEqual(errors, [])
            browser.close()

if __name__ == '__main__':
    unittest.main()
