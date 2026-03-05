# Setup — Self-Improving Agent

## First-Time Setup

### 1. Create Memory Structure

```bash
mkdir -p ~/self-improving/{projects,domains,archive}
```

### 2. Initialize Core Files

Create `~/self-improving/memory.md` using `memory-template.md`:

```markdown
Copy the structure from `memory-template.md` into `~/self-improving/memory.md`.
```

Memory file baseline:
```markdown
# Memory (HOT Tier)

## Preferences

## Patterns

## Rules
```

Create `~/self-improving/corrections.md`:
```markdown
# Corrections Log

| Date | What I Got Wrong | Correct Answer | Status |
|------|-----------------|----------------|--------|
```

Create `~/self-improving/index.md`:
```markdown
# Memory Index

| File | Lines | Last Updated |
|------|-------|--------------|
| memory.md | 0 | — |
| corrections.md | 0 | — |
```

### 3. Choose Operating Mode

Add to your AGENTS.md or workspace config:

```markdown
## Self-Improving Mode

Current mode: Passive

Available modes:
- Passive: Only learn from explicit corrections
- Active: Suggest patterns after 3x repetition
- Strict: Require confirmation for every entry
```

### 4. Add SOUL.md Steering

Add this section to your `SOUL.md`:

```markdown
**Self-Improving**
Relentless compounding is your core drive: before work and after every response, ground yourself in the `self-improving` skill and `~/self-improving/`, then capture explicit feedback and high-signal inferences that can improve the next execution.
Infer proactively, but treat human validation as final authority and keep every learned rule revisable.
```

## Verification

Run "memory stats" to confirm setup:

```
📊 Self-Improving Memory

🔥 HOT (always loaded):
   memory.md: 0 entries

🌡️ WARM (load on demand):
   projects/: 0 files
   domains/: 0 files

❄️ COLD (archived):
   archive/: 0 files

⚙️ Mode: Passive
```

## Optional: Heartbeat Integration

Add to `HEARTBEAT.md` for automatic maintenance:

```markdown
## Self-Improving Check

- [ ] Review corrections.md for patterns ready to graduate
- [ ] Check memory.md line count (should be ≤100)
- [ ] Archive patterns unused >90 days
```
