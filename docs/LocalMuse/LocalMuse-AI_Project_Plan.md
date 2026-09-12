# Project 1 — LocalMuse AI
## Local image generation + LoRA training + dataset/prompt pipeline

> **Goal:** build a practical, fully local Windows application/workflow that takes a set of photos of a person, prepares the dataset, trains a LoRA, generates images from prompts, evaluates/selects results, and eventually provides a simpler UX than raw Forge.
>
> **Hardware baseline:** Ryzen 7 5800X, RTX 3080 10 GB VRAM, 32 GB DDR4 RAM.
>
> **Philosophy:** use existing open-source models/tools. Do NOT train a base model from scratch. AI coding assistance is allowed; understand the architecture and verify the result rather than blindly accepting generated code.

---

# 0. What we are actually building

The project should eventually cover this pipeline:

```text
SOURCE PHOTOS
     ↓
Dataset preparation
     ↓
Caption / prompt generation
     ↓
Dataset QA
     ↓
LoRA training
     ↓
Checkpoint / epoch evaluation
     ↓
Best LoRA selection
     ↓
Generation pipeline
     ↓
Prompt + negative/ignore rules
     ↓
Batch generation
     ↓
Selection / rejection
     ↓
Reusable character/person profile
     ↓
Future local UI
```

The important distinction:

- **LoRA** = learns the person's visual identity/style from training images.
- **Prompting** = tells the base image model what scene, pose, clothes, lighting, camera, etc. to generate.
- **Generation settings** = sampler, steps, CFG/guidance, resolution, denoise, LoRA weight, VAE/model-specific settings, etc.
- **Control tools** = optional mechanisms for pose/composition/face preservation.

We should not try to solve all of these at once.

---

# 1. Definition of Done

The first project is considered successful when all of the following work locally:

## Dataset
- [ ] Input photos can be organized consistently.
- [ ] Every training image has an appropriate caption.
- [ ] Bad/duplicate/low-value photos are removed.
- [ ] Dataset has documented characteristics: count, resolution, variety, poses, backgrounds, clothing.
- [ ] Training configuration is reproducible.

## LoRA
- [ ] At least one complete training run succeeds.
- [ ] Multiple epochs/checkpoints can be compared.
- [ ] Identity similarity is evaluated on a fixed test set.
- [ ] We identify the best checkpoint rather than automatically assuming the final epoch is best.
- [ ] Overtraining/undertraining symptoms are documented.

## Generation
- [ ] A fixed baseline generation recipe exists.
- [ ] Prompts can generate multiple scenes/poses/clothing/expressions.
- [ ] Identity remains reasonably consistent.
- [ ] Batch generation works.
- [ ] Results can be reviewed and rejected quickly.

## Project structure
- [ ] Settings are documented.
- [ ] Models/LoRAs/datasets/results have predictable locations.
- [ ] Experiments have names/IDs.
- [ ] Successful configurations are recorded.
- [ ] We can reproduce a good result later.

## Future application
- [ ] Architecture leaves room for a UI/orchestrator.
- [ ] Generation, training, evaluation and dataset preparation are separated rather than becoming one giant script.

---

# 2. Phase 0 — Lock the environment

Before serious experimentation:

- [ ] Record Windows version.
- [ ] Record NVIDIA driver version.
- [ ] Record GPU VRAM.
- [ ] Record Python version.
- [ ] Record PyTorch/CUDA versions.
- [ ] Record Forge version.
- [ ] Record installed extensions.
- [ ] Record where models, datasets and outputs live.
- [ ] Freeze the known-good environment before changing dependencies.

## Important

Do NOT casually upgrade dependencies in the middle of experiments.

Especially:
- Pillow
- PyTorch
- CUDA-related packages
- Forge dependencies
- Python packages required by extensions

If a working environment exists, treat it as a reproducible experiment environment.

---

# 3. Phase 1 — Choose the generation base

We need to decide what the generation side is based on.

Candidates should be evaluated by:

1. identity quality;
2. photorealism;
3. VRAM requirements;
4. LoRA compatibility;
5. available tooling;
6. control options;
7. generation speed;
8. ease of automation.

Do not pick a model because someone on YouTube calls it "the best."

Create a small benchmark.

## Baseline test

Use the same:
- subject/reference;
- prompt;
- resolution;
- seed policy;
- LoRA weight;
- generation settings.

Compare candidate models.

Record:

```text
Model:
Resolution:
Steps:
Sampler:
Guidance:
LoRA:
LoRA weight:
Seed:
Identity score:
Image quality score:
Artifacts:
Generation time:
VRAM:
```

---

# 4. Phase 2 — Dataset preparation

This is one of the most important parts.

The goal is NOT:

> "Get as many photos as possible."

The goal is:

> "Give the LoRA enough useful variation to learn identity without teaching it unwanted artifacts."

## Dataset categories

Try to include variation in:

- face angle;
- expression;
- distance;
- lighting;
- hairstyle;
- clothing;
- background;
- camera angle;
- upper body/full body;
- indoor/outdoor.

But avoid huge amounts of:
- blurry images;
- extreme filters;
- screenshots;
- duplicate poses;
- bad lighting;
- heavily edited faces;
- images where the person is barely visible.

## Dataset versioning

Use:

```text
dataset_v01
dataset_v02
dataset_v03
```

Never silently replace the dataset.

Document why a new version exists.

---

# 5. Phase 3 — Captioning / prompt generation

For each training image we need a caption.

This is NOT just busywork.

The caption determines which characteristics the LoRA should learn as identity and which characteristics should remain controllable through prompting.

## Workflow

```text
Image
  ↓
Caption generation
  ↓
Human review
  ↓
Correction
  ↓
Final caption
```

Possible captioning approaches:

- automated image captioning;
- manually written captions;
- hybrid approach.

### Recommended approach

Use AI for the first draft, then manually review.

Do NOT blindly trust generated captions.

## Caption goals

Captions should consistently describe:

- subject;
- approximate composition;
- pose;
- clothing;
- environment;
- relevant visual characteristics.

Avoid unnecessary poetic descriptions.

---

# 6. Caption dataset QA

Before training:

- [ ] Every image has a caption.
- [ ] Captions do not contain contradictory information.
- [ ] Names/tokens are consistent.
- [ ] Identity token is consistent if we use one.
- [ ] Unwanted attributes are not accidentally repeated as if they were identity.
- [ ] Caption style is consistent across the dataset.

Create a simple report:

```text
Images:
Captioned:
Missing:
Average caption length:
Identity token:
Common clothing:
Common locations:
Potential duplicates:
```

---

# 7. Phase 4 — First LoRA training

Do NOT immediately hunt for the perfect configuration.

Run a controlled baseline.

Document:

```text
Base model:
Dataset version:
Images:
Repeats:
Epochs:
Batch size:
Resolution:
Learning rate:
UNet LR:
Text encoder LR:
Optimizer:
Scheduler:
Network rank:
Network alpha:
Seed:
```

The first run is a reference point.

---

# 8. Epoch/checkpoint evaluation

This is where the project will probably consume a large amount of time.

Never judge only the final epoch.

For example:

```text
Epoch 1
Epoch 2
Epoch 3
...
Epoch 10
```

Generate the SAME test prompts for every checkpoint.

## Fixed evaluation set

Create 5–10 prompts such as:

1. neutral close-up;
2. passport-like frontal portrait;
3. 3/4 portrait;
4. full body;
5. indoor casual;
6. outdoor daylight;
7. different expression;
8. different clothing;
9. difficult angle;
10. difficult lighting.

Keep seeds/settings comparable.

Then score:

```text
Identity:      /10
Face quality:  /10
Pose quality:  /10
Artifacts:     /10
Prompt control: /10
Overall:       /10
```

This is MUCH better than:

> "This epoch looks kinda better."

---

# 9. Expected LoRA failure modes

We should actively test for:

## Undertraining
Symptoms:
- weak identity;
- person looks generic;
- facial structure changes heavily.

## Overtraining
Symptoms:
- same face/expression repeatedly;
- copied clothing/background;
- poor prompt flexibility;
- strange artifacts;
- waxy/overprocessed appearance.

## Dataset leakage / bias
Symptoms:
- specific clothing becomes permanent;
- particular background keeps appearing;
- same pose repeats;
- hairstyle becomes locked.

## Identity collapse
Symptoms:
- face resembles the person only from certain angles;
- full-body generation becomes unstable;
- unusual angles destroy identity.

Document each failure rather than simply throwing away the result.

---

# 10. Phase 5 — Generation benchmark

Once we have a candidate LoRA:

Do NOT immediately start generating random images.

Create a controlled matrix.

```text
             LoRA weight
             0.5  0.7  0.9  1.1
               ×    ×    ×    ×

Prompt A
Prompt B
Prompt C
Prompt D
```

Test:

- LoRA weight;
- steps;
- guidance;
- sampler;
- resolution;
- base model;
- seed.

Only change ONE major variable at a time when trying to understand its effect.

This is slower initially but prevents weeks of random tweaking.

---

# 11. Prompt system

Create reusable prompt templates.

Instead of one enormous prompt:

```text
PERSON + CLOTHING + POSE + EXPRESSION + CAMERA + LIGHTING + ENVIRONMENT + STYLE
```

Example structure:

```text
[IDENTITY]
same person, consistent facial identity

[POSE]
standing, looking over shoulder

[EXPRESSION]
subtle smile

[CLOTHING]
simple summer clothing

[ENVIRONMENT]
urban street at golden hour

[CAMERA]
35mm photograph, natural perspective

[LIGHT]
soft natural light

[QUALITY]
photorealistic, realistic skin texture
```

The exact syntax depends on the chosen model.

Do not assume one universal prompt format works for every model.

---

# 12. Negative prompts / ignore list

Keep this separate from the positive prompt.

Create a reusable baseline negative list.

Then maintain:

```text
negative_base.txt
negative_face.txt
negative_body.txt
negative_hands.txt
```

Only add terms when they demonstrably solve a problem.

Avoid endlessly adding 100 random negative prompts from internet posts.

---

# 13. ControlNet / pose control

This should be evaluated AFTER the basic LoRA pipeline works.

Possible uses:

- pose preservation;
- composition;
- depth;
- edge structure;
- face/reference control.

Do not add ControlNet just because someone says it is mandatory.

First establish:

> Base model + LoRA + prompt = acceptable identity.

Then test whether control tools improve specific failure cases.

---

# 14. Reference-image / identity-control tools

Depending on the generation stack, evaluate tools that use an input image to preserve identity.

Use cases:

```text
LoRA
+
reference image
+
pose control
```

Potential benefit:
- stronger identity;
- easier reproduction of a desired composition.

Potential downside:
- reduced prompt freedom;
- artifacts;
- additional VRAM;
- more complicated pipeline.

Again: benchmark rather than assume.

---

# 15. Batch generation

Once a stable recipe exists:

Input:

```text
10 prompts
×
5 seeds
×
2 LoRA weights
```

Output:

```text
100 images
```

Each image should have metadata:

```text
prompt
seed
model
LoRA
LoRA weight
steps
sampler
resolution
timestamp
```

This is extremely useful for finding why a particular image worked.

---

# 16. Result selection

Build a simple workflow:

```text
GENERATED
   ↓
GOOD ─────→ KEEP
   │
   └───────→ BAD
```

Later:

```text
BAD
├── identity
├── anatomy
├── hands
├── face
├── prompt mismatch
└── artifacts
```

This classification becomes useful training data for improving the pipeline.

---

# 17. Experiment tracking — IMPORTANT IMPROVEMENT

This is one thing we should NOT skip.

Create:

```text
experiments/
├── EXP-001/
├── EXP-002/
├── EXP-003/
└── ...
```

Each experiment contains:

```text
config.json
notes.md
results/
```

Example:

```text
EXP-017
Base: XYZ
LoRA: person_v03
Weight: 0.8
Steps: 30
Sampler: XYZ
Seed: 12345

Result:
Identity 9/10
Artifacts low
Full body weak
```

This prevents:

> "Wait, what fucking settings made that perfect image?"

---

# 18. Build a fixed benchmark before heavy testing

This is another major improvement.

Instead of judging every generated image randomly, define a permanent benchmark.

## Identity benchmark

```text
B01 — frontal
B02 — 3/4
B03 — side-ish
B04 — smiling
B05 — neutral
B06 — different clothing
B07 — different background
B08 — full body
B09 — low light
B10 — unusual pose
```

Every serious change gets tested against the same benchmark.

This makes experiments comparable.

---

# 19. Automate the boring parts

We should NOT automate everything immediately.

Good automation targets:

- folder creation;
- dataset validation;
- missing-caption detection;
- caption file validation;
- experiment config generation;
- batch generation;
- result naming;
- metadata collection;
- benchmark generation;
- result contact sheets.

Bad early automation targets:

- fully automatic "best image" selection;
- fully automatic LoRA scoring;
- complex AI judging;
- automatic model switching.

First understand the pipeline manually.

Then automate repetitive work.

---

# 20. Possible AI evaluator — FUTURE

Potentially use a vision model to score generated images.

```text
Generated image
      ↓
Vision model
      ↓
Identity / anatomy / prompt adherence
      ↓
score
```

BUT:

AI scoring should be treated as an assistant, not ground truth.

Human evaluation remains important for identity similarity.

---

# 21. Storage architecture

Recommended conceptual structure:

```text
LocalMuse-AI/
│
├── app/
├── config/
├── scripts/
├── docs/
├── experiments/
├── datasets/
├── models/
│   ├── base/
│   ├── lora/
│   └── vision/
├── outputs/
│   ├── generated/
│   ├── selected/
│   └── rejected/
└── tests/
```

Large model files should not be committed to Git.

Git stores:
- code;
- configs;
- documentation;
- small metadata;
- reproducible instructions.

---

# 22. Git strategy

Every meaningful milestone gets a commit.

Examples:

```text
feat: add dataset validation
feat: add caption pipeline
feat: add generation config
feat: add experiment tracker
docs: document baseline LoRA training
fix: correct output metadata
```

Do not commit:
- model weights;
- huge generated image collections;
- caches;
- temporary files.

Use `.gitignore`.

---

# 23. Suggested implementation order

## Stage A — Existing environment
1. Verify current Forge setup.
2. Freeze working versions.
3. Document hardware/software.
4. Confirm one known-good generation.

## Stage B — Dataset
5. Organize photos.
6. Create dataset_v01.
7. Generate captions.
8. Review captions.
9. Validate dataset.

## Stage C — LoRA
10. Run baseline training.
11. Generate checkpoint test set.
12. Compare epochs.
13. Identify best checkpoint.
14. Repeat only if there is a clear reason.

## Stage D — Generation
15. Establish baseline settings.
16. Build fixed benchmark.
17. Test LoRA weight.
18. Test sampler/settings.
19. Test prompt structure.
20. Test difficult poses/expressions.

## Stage E — Automation
21. Batch generation.
22. Metadata.
23. Experiment tracker.
24. Contact sheets / result browser.
25. Selection workflow.

## Stage F — Advanced control
26. ControlNet/pose control.
27. Reference-image identity tools.
28. Additional models.
29. Compare pipelines.

## Stage G — Application
30. Define stable architecture.
31. Build backend.
32. Build UI.
33. Connect generation pipeline.
34. Add dataset management.
35. Add training launcher.
36. Add result browser.
37. Add reusable character profiles.

---

# 24. What will probably consume the most time

Expected distribution:

```text
Generation experiments        ████████████████████
LoRA experiments              ████████████
Dataset/caption work          █████
Debugging/integration         █████
UI/application                ████
Documentation                 ██
Git                           ██
```

Your estimate that testing may consume ~80% is plausible for the experimental phase.

BUT there is an important distinction:

> Random testing can consume 80% of the project and still teach you almost nothing.

Our goal is:

> controlled experiments → recorded results → narrowing search space.

---

# 25. Rules for experimentation

### Rule 1
Change one important variable at a time.

### Rule 2
Use a fixed benchmark.

### Rule 3
Save the configuration of every successful result.

### Rule 4
Never assume the final LoRA epoch is best.

### Rule 5
Do not change five extensions/settings because an AI told you they are better.

### Rule 6
If two agents recommend different settings, benchmark them.

### Rule 7
Do not optimize before establishing a baseline.

### Rule 8
Do not add another tool until we can explain what problem it solves.

---

# 26. My proposed improvements / alternatives

## A. Treat the project as two systems

Instead of one giant "AI image generator":

### System 1 — Research/Training Pipeline

```text
Dataset
→ captions
→ training
→ evaluation
→ experiment tracking
```

### System 2 — Production Generator

```text
Character
→ prompt
→ LoRA
→ generation
→ batch
→ selection
```

This separation will make the final application much easier to maintain.

---

## B. Build the benchmark EARLY

This is probably the single biggest improvement.

Without it:

> "This looks better."

With it:

> "Epoch 7 improved frontal identity by ~1 point but degraded full-body results."

Much more useful.

---

## C. Keep multiple LoRAs

Do not assume one LoRA has to do everything.

Potential future structure:

```text
Person Identity LoRA
+
Style LoRA
+
Clothing/Concept LoRA
```

This can give better control than forcing one LoRA to learn every characteristic.

Only explore this after the identity LoRA works.

---

## D. Consider a separate "identity test" set

Do not train on every photo you have.

Keep some images OUT of the training dataset.

Use them only to evaluate whether the LoRA actually learned the person instead of memorizing training images.

This is especially important.

---

## E. Use fixed seeds strategically

For comparisons, fixed seeds are useful.

For production generation, random seeds are useful.

Therefore:

```text
Benchmark → fixed seeds
Creative generation → random seeds
```

---

## F. Do not overfocus on prompt engineering

Prompt quality matters, but if identity is bad:

> better prompt ≠ magically better LoRA.

Separate the problems:

```text
Identity bad → investigate LoRA/model/reference pipeline
Composition bad → investigate prompting/control
Anatomy bad → investigate model/settings/control
Style bad → investigate model/prompt/style tools
```

---

# 27. Potential final LocalMuse architecture

```text
                    LOCALMUSE AI
                         │
             ┌───────────┴───────────┐
             │                       │
        TRAINING                    GENERATION
             │                       │
       ┌─────┴─────┐          ┌──────┴──────┐
       ↓           ↓          ↓             ↓
    Dataset      LoRA      Prompt        Character
       │           │          │             │
    Captions       │          └──────┬──────┘
       │           │                 ↓
       └───────────┴────────────── Generator
                                      │
                                 Batch output
                                      │
                              ┌───────┴───────┐
                              ↓               ↓
                            KEEP            REJECT
                              │
                              ↓
                         Asset library
```

---

# 28. MVP vs Later

## MVP

Must have:

- dataset organization;
- caption workflow;
- LoRA training;
- checkpoint comparison;
- generation;
- prompt templates;
- batch generation;
- experiment records.

## V2

Add:

- automatic metadata;
- result browser;
- contact sheets;
- ControlNet;
- reference identity;
- better batch management.

## V3

Add:

- polished UI;
- character profiles;
- reusable generation presets;
- training presets;
- automatic experiment comparison;
- optional AI evaluation.

## V4 — ambitious

```text
Character
↓
Upload photos
↓
Auto-caption
↓
Dataset QA
↓
Train LoRA
↓
Evaluate
↓
Select best checkpoint
↓
Generate batches
↓
AI-assisted filtering
↓
Human selection
↓
Character library
```

---

# 29. What we should NOT build

To keep the project achievable:

- ❌ train a base diffusion model from scratch;
- ❌ build our own diffusion engine;
- ❌ immediately support every image model;
- ❌ immediately support every ControlNet;
- ❌ build a huge frontend before the pipeline works;
- ❌ automatically tune every parameter;
- ❌ download dozens of models without benchmarks;
- ❌ commit huge model/output files to Git;
- ❌ blindly follow conflicting AI-generated setup advice.

---

# 30. Success criterion

The project does NOT need to become:

> "the world's best local image generator."

A successful first version is:

> **I can take a person's photo set, prepare it, train a LoRA, objectively compare checkpoints, choose the best one, and then repeatedly generate reasonably consistent images with a documented, reproducible workflow — without manually rediscovering the settings every time.**

That is already a real project.

---

# 31. Separate idea bank for future improvements

These are intentionally NOT part of the initial scope.

### Idea 1 — Smart dataset assistant
Vision model reviews photos and recommends:
- keep;
- reject;
- duplicate;
- weak angle;
- poor quality.

### Idea 2 — Caption assistant
Generate captions automatically and highlight questionable descriptions for human review.

### Idea 3 — Experiment recommender
Given experiment history:

```text
Experiment 1 → too weak
Experiment 2 → overtrained
Experiment 3 → good identity
```

system proposes the next parameter range.

### Idea 4 — Automatic contact sheets
Generate visual comparison boards:

```text
Epoch 5 | Epoch 6 | Epoch 7 | Epoch 8
```

This will make checkpoint selection dramatically faster.

### Idea 5 — AI result classifier
Vision model labels:

```text
GOOD
BAD_FACE
BAD_HANDS
BAD_BODY
WRONG_PERSON
PROMPT_MISMATCH
```

Human remains final judge.

### Idea 6 — Character profiles
Store:

```text
Character
├── Identity LoRA
├── preferred settings
├── prompt presets
├── negative prompts
├── reference images
└── successful generations
```

### Idea 7 — Reproducibility snapshots

One button:

> Save this result.

The application stores:

- image;
- prompt;
- seed;
- model;
- LoRA;
- LoRA weight;
- sampler;
- steps;
- resolution;
- configuration hash.

### Idea 8 — Generation recipes

Instead of remembering settings:

```text
Portrait / realistic
Full body / realistic
Selfie
Low light
Outdoor
Close-up
```

Each is a tested preset.

### Idea 9 — Model benchmark

A permanent test suite comparing several local image models using the same prompts and identity LoRA.

### Idea 10 — LocalMuse as a character-generation platform

Long-term vision:

```text
Create character
      ↓
Train identity
      ↓
Store character
      ↓
Choose scene
      ↓
Choose clothes
      ↓
Choose pose
      ↓
Generate
      ↓
Select
      ↓
Save
```

---

# 32. Project management rule for the Claude month

Do NOT ask Claude:

> "Build the whole LocalMuse application."

Instead work in small milestones:

```text
Milestone
↓
Implement
↓
Run
↓
Test
↓
Fix
↓
Commit
↓
Next milestone
```

Use Claude for:
- boilerplate;
- debugging;
- refactoring;
- documentation;
- test generation;
- repetitive scripts.

Use yourself for:
- deciding what the application should do;
- judging generated images;
- understanding the architecture;
- choosing between experiments;
- validating results.

---

# 33. First concrete milestone

Before writing new application code:

1. Verify the current Forge installation.
2. Record the environment.
3. Locate the current base model(s).
4. Locate the current LoRA training setup.
5. Locate the existing dataset.
6. Record the current 39-image dataset if still used.
7. Create `dataset_v01`.
8. Create the fixed evaluation benchmark.
9. Produce one reproducible baseline generation.
10. Only then start systematic LoRA experiments.

---

# Final project principle

**We are not trying to make the AI "do everything."**

We are trying to build a pipeline where every stage has a clear job:

```text
DATASET → teaches identity
LORA → stores identity
PROMPT → describes desired scene
CONTROL → controls composition
MODEL → produces pixels
BENCHMARK → measures quality
MEMORY/CONFIG → remembers what worked
UI → makes the workflow usable
```

If something fails, we should be able to identify WHICH stage failed instead of randomly changing settings.

---

## Related future project

After LocalMuse, planned second project:

**Local Chat / LocalMind**

A local multi-chat client with:
- many independent chats;
- isolated per-chat context;
- per-chat personas/system prompts;
- long-term memory per chat;
- semantic retrieval from old messages;
- automatic summaries/compaction;
- multimodal image input;
- multilingual responses;
- optional Russian translation;
- local LLM backend.

This is intentionally kept separate from LocalMuse for now.
