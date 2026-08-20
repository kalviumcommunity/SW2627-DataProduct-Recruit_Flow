import os
import sys
import unittest
import pandas as pd

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.routes.analytics import get_funnel
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

if __name__ == "__main__":
    unittest.main()
