"""NEO + SWITCH source recipe and valve-event browser regressions."""
import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright

URL = os.environ.get('V60_TEST_URL', Path(__file__).resolve().parents[1].joinpath('index.html').as_uri())

class NeoSwitchTests(unittest.TestCase):
    def test_switch_published_recipe_valves_and_scaling(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 390, 'height': 844})
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(URL)
            page.locator('#methodPills [data-val="neo"]').click()
            selector = page.locator('#neoSetupPills [data-val="switch"]')
            self.assertEqual(selector.count(), 1, 'NEO needs a SWITCH-base setup option')
            selector.click()
            self.assertIn('NEO + SWITCH', page.locator('#recipeTitle').inner_text())
            self.assertEqual(page.locator('#doseSlider').input_value(), '16')
            self.assertEqual(page.locator('#stTotal').inner_text(), '240 g')
            self.assertEqual(page.locator('#tempSlider').input_value(), '90.5')
            self.assertEqual(page.locator('#tempSlider').get_attribute('step'), '0.5')
            self.assertEqual(page.locator('#stTemp').inner_text(), '90.5 °C')
            self.assertEqual(page.locator('#stTimeLbl').inner_text().lower(), 'last checkpoint')
            self.assertIn('2:30', page.locator('#stTime').inner_text())
            self.assertIn('CLOSED', page.locator('#valveCallout').inner_text())
            self.assertIn('0:40', page.locator('#valveCallout').inner_text())
            self.assertIn('8.0', page.locator('#stGrindRef').inner_text())
            self.assertIn('SWITCH', page.locator('#refsList').inner_text())
            self.assertEqual(page.locator('#schedule .time').all_inner_texts(), ['0:00', '0:00', '0:40', '0:50', '1:30', '2:00', '2:30'])
            labels = page.locator('#schedule .lbl').all_inner_texts()
            self.assertIn('CLOSE', labels[0])
            self.assertIn('swirl 5', labels[1])
            self.assertIn('OPEN', labels[2])
            self.assertIn('center', labels[5])
            self.assertIn('CLOSE', labels[-1])
            self.assertEqual(page.locator('#schedule .total').all_inner_texts(), ['0g', '+50g · 50g', '50g', '+70g · 120g', '+80g · 200g', '+40g · 240g', '240g'])
            self.assertIn('later reopening is not specified', page.locator('#promptText').inner_text())
            page.locator('#doseSlider').evaluate('(e) => { e.value=13; e.dispatchEvent(new Event("input", {bubbles:true})); }')
            self.assertEqual(page.locator('#stTotal').inner_text(), '195 g')
            self.assertIn('app-scaled', page.locator('#recipeDescr').inner_text())
            self.assertEqual(page.locator('#schedule .total').all_inner_texts(), ['0g', '+41g · 41g', '41g', '+57g · 98g', '+65g · 163g', '+32g · 195g', '195g'])
            self.assertIn('Use the app-scaled', page.locator('#stAgit').inner_text())
            self.assertIn('customized', page.locator('#promptText').inner_text())
            self.assertEqual(errors, [])
            self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'))
            browser.close()

    def test_switch_iced_open_valve_and_setup_transitions(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 390, 'height': 844})
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(URL)
            page.get_by_role('button', name='NEO + SWITCH · Kurasu', exact=True).click()
            page.locator('#tempSlider').evaluate('(e) => {e.value=91.5; e.dispatchEvent(new Event("input", {bubbles:true}));}')
            self.assertEqual(page.locator('#tempVal').inner_text(), '91.5 °C')
            self.assertIn('Temperature customized', page.locator('#recipeDescr').inner_text())
            self.assertIn('91.5 °C', page.locator('#promptText').inner_text())
            page.locator('#brewStylePills [data-val="iced"]').click()
            self.assertIn('NEO + SWITCH', page.locator('#recipeTitle').inner_text())
            self.assertIn('house adaptation', page.locator('#recipeDescr').inner_text())
            self.assertIn('OPEN throughout', page.locator('#valveCallout').inner_text())
            self.assertIn('OPEN throughout', page.locator('#promptText').inner_text())
            self.assertIn('OPEN throughout', page.locator('#stAgit').inner_text())
            self.assertNotIn('CLOSE', page.locator('#schedule').inner_text())
            self.assertEqual(page.locator('#iceAmount').inner_text(), '45 g')
            self.assertEqual(page.locator('#stTotal').inner_text(), '225 g')
            self.assertEqual(page.locator('#schedule .total').all_inner_texts()[-1], '+65g · 180g')
            page.locator('#doseSlider').evaluate('(e) => {e.value=20; e.dispatchEvent(new Event("input", {bubbles:true}));}')
            self.assertEqual(page.locator('#iceAmount').inner_text(), '60 g')
            self.assertIn('240 g hot water', page.locator('#iceDetail').inner_text())
            page.locator('#brewStylePills [data-val="hot"]').click()
            self.assertEqual(page.locator('#tempSlider').input_value(), '90.5')
            self.assertEqual(page.locator('#stTotal').inner_text(), '240 g')
            self.assertIn('CLOSE', page.locator('#schedule').inner_text())
            page.get_by_role('button', name='V60 NEO · Kurasu', exact=True).click()
            self.assertEqual(page.locator('#neoSetupPills .active').get_attribute('data-val'), 'percolation')
            self.assertFalse(page.locator('#valveCallout').is_visible())
            self.assertEqual(page.locator('#stTotal').inner_text(), '200 g')
            self.assertEqual(page.locator('#tempSlider').input_value(), '91')
            names = page.locator('#presets button').all_text_contents()
            for name in names:
                page.get_by_role('button', name='NEO + SWITCH · Kurasu', exact=True).click()
                page.get_by_role('button', name=name, exact=True).click()
                self.assertNotIn('NaN', page.locator('#recipeGuide').inner_text(), name)
                active_neo = page.locator('#methodPills .active').get_attribute('data-val') == 'neo'
                self.assertEqual(page.locator('#grpNeoSetup').is_visible(), active_neo)
                self.assertEqual(page.locator('#valveCallout').is_visible(), name == 'NEO + SWITCH · Kurasu')
                self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'), name)
            self.assertEqual(errors, [])
            browser.close()

if __name__ == '__main__':
    unittest.main()
