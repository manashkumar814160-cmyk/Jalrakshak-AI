# Judge questions and honest answers

**Does it measure soil moisture?** No. It estimates root-zone depletion from weather, crop/soil assumptions, irrigation logs and optional farmer observations.

**Why is there no ML accuracy score?** No suitable real historical training set is bundled. We do not invent training data or metrics. The optional surface-moisture forecast remains unavailable until it can be trained and evaluated against a time-ordered holdout and persistence baseline.

**Is water saved guaranteed?** No. There is no field trial. Any future comparison is a simulation against an explicitly stated baseline.

**What happens when the weather API is down?** The app tries a successful local response cache, then clearly labelled bundled sample data; offline mode goes directly to sample data.

**Why are rice results less reliable?** Paddy rice commonly uses standing water and needs a different water-management model than this simplified root-zone balance.

**What must happen before real-world use?** Validate assumptions with local agronomists and field data, review Telugu and Hindi translations, verify live integrations, and test recommendations on representative farms.
