# MVP Scale Dataset

This folder holds a separate large synthetic dataset for teammate A's MVP proof.

Layout:

- `outputs/clean/` - large clean dataset
- `outputs/messy/` - matching messy dataset with controlled chaos
- `outputs/manifest.json` - quick summary of both outputs

Default scale used by the generator:

- 5,000 candidates
- 250 jobs
- 25,000 applications

The downstream files are generated proportionally from the funnel logic, so the row counts for interviews, offers, onboarding, and stage events will be larger than the original smoke-test files.

Run:

```bash
python backend/scripts/mvp_scale_data/generate_mvp_scale_data.py
```

Fresh seed command:

```bash
python backend/scripts/mvp_scale_data/seed_demo_data.py --dataset clean
python backend/scripts/mvp_scale_data/seed_demo_data.py --dataset messy
```

Load and reset the database through the running backend:

```bash
python backend/scripts/mvp_scale_data/load_mvp_scale_dataset.py --dataset clean --transport direct
python backend/scripts/mvp_scale_data/load_mvp_scale_dataset.py --dataset messy --transport direct
```

If you want to keep existing data and only add the new dataset:

```bash
python backend/scripts/mvp_scale_data/load_mvp_scale_dataset.py --dataset clean --skip-reset --transport direct
```
