import os
import sys
import unittest
import pandas as pd

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.routes.analytics import get_funnel, get_reasons, get_dropoff
from backend.routes.candidates import get_candidate
from backend.routes.upload import upload_entity_file, trigger_full_pipeline

class TestUploadPipeline(unittest.TestCase):
    
    def test_01_analytics_funnel_route(self):
        import asyncio
        funnel_data = asyncio.run(get_funnel())
        self.assertIsInstance(funnel_data, list)
        self.assertGreater(len(funnel_data), 0)
        print("\n [OK] Analytics Funnel Endpoint Route Verified:")
        for stage in funnel_data:
            print(f"   - {stage['stage']}: {stage['candidate_count']} candidates (Conversion: {stage.get('stage_conversion_pct')}%, Drop-off: {stage.get('stage_dropoff_pct')}%)")

    def test_02_candidate_lookup_route(self):
        import asyncio
        candidate_data = asyncio.run(get_candidate("C1001"))
        self.assertEqual(candidate_data["candidate_id"], "C1001")
        self.assertEqual(candidate_data["department"], "IT")
        print("\n [OK] Candidate Lookup Route Verified: C1001 (Backend Developer) journey retrieved.")

    def test_03_trigger_pipeline_route(self):
        import asyncio
        res = asyncio.run(trigger_full_pipeline())
        self.assertEqual(res["status"], "success")
        print("\n [OK] Pipeline Trigger Route Verified: Successfully ran full Data Science engine!")

    def test_04_reasons_and_dropoff_routes(self):
        import asyncio
        reasons_data = asyncio.run(get_reasons())
        self.assertIsInstance(reasons_data, list)
        self.assertGreater(len(reasons_data), 0)
        print("\n [OK] Analytics Reasons Endpoint Route Verified:")
        for r in reasons_data:
            print(f"   - {r['reason']}: {r['count']} ({r['percentage']}%)")
            
        dropoff_data = asyncio.run(get_dropoff())
        self.assertIsInstance(dropoff_data, dict)
        self.assertIn("detailed_reasons", dropoff_data)
        self.assertIn("department_reasons", dropoff_data)
        self.assertIn("stage_reasons", dropoff_data)
        self.assertGreater(len(dropoff_data["detailed_reasons"]), 0)
        print(" [OK] Analytics Dropoff Endpoint Route Verified successfully!")

if __name__ == "__main__":
    unittest.main()

