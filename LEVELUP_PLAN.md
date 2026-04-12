# Level Maxing Plan (Parallel Tracks)

Goal: finish foundations in parallel, then project phase.

## Source Courses (fixed)
- ML/DL track source: `Complete Machine Learning, NLP, MLOps & Deployment` (Udemy)
- Agentic track source: `Complete Agentic AI Bootcamp with LangGraph and LangChain` (Udemy)
- Rule: these 2 are primary learning sources; no extra random course hopping.

## Tracks
- Track A: Agentic AI course completion (from your LangGraph/LangChain Udemy)
- Track B: ML core completion (filtered from your ML+NLP+MLOps Udemy)
- Track C: Backend polishing (FastAPI production basics)
- Track D: DSA daily consistency

## ML Course Filter (what to do vs defer)
- Do now: preprocessing, EDA basics, regression, classification, metrics, feature engineering, pipelines, model persistence, basic NLP
- Do light now: deployment basics that support your backend integration
- Defer for later: deep DS theory blocks not needed for AI engineer projects, very deep DL internals, full MLOps depth

## Time Split (daily)
- Agentic AI: 60 min
- Backend polish: 60 min
- DSA: 45 min (2 questions)
- ML core: 60 min on alternate days, 30 min light revision on non-ML days
- Log: 10 min

## Completion Criteria (clear end conditions)
- Agentic AI done when: all core + advanced LangGraph/LangChain sections complete + 2 runnable mini builds + README notes
- ML done when: filtered ML path complete from the course + 3 notebooks (regression, classification, NLP) with metric comparison
- Backend done when: auth + CRUD + DB migrations + caching + tests + Docker + deployed URL
- DSA done when: 120 total actions = 80 quality solves + 40 revisions

## Execution Rule (important)
- Do not wait for all courses to finish before building.
- Every 2 weeks, ship one mini implementation (1-2 day scope).
- Full projects still start after Week 8, but mini ships happen during prep.

## 8-Week Roadmap

### Weeks 1-2 (Foundation Close)
- Agentic AI: finish pending core sections and start advanced LangGraph modules
- ML: course sections on preprocessing, train/val/test, regression, classification, metrics
- Backend: FastAPI structure, SQLAlchemy, auth basics (JWT)
- DSA: 4 questions/day, 5 days/week target
- Mini ship: one small FastAPI + single AI endpoint demo

### Weeks 3-4 (Skill Consolidation)
- Agentic AI: 1 mini agent from course concepts (tool + memory + graph)
- ML: course sections on feature engineering, pipelines, model persistence, intro NLP
- Backend: CRUD + Alembic + Redis cache + error handling
- DSA: continue daily, start timed medium sets
- Mini ship: one agent workflow with logs and retry handling

### Weeks 5-6 (Readiness Check)
- Agentic AI: 1 more mini build with multi-step workflow
- ML: end-to-end notebook (data -> model -> eval) using filtered course modules
- Backend: tests (10+), Dockerize, API docs cleanup
- DSA: revise wrong questions list
- Mini ship: backend API with tests + Docker run proof

### Weeks 7-8 (Project Launch Prep)
- Finish all pending modules in Tracks A/B/C
- DSA total should reach 120 target
- Prepare project specs for full build phase
- Mini ship: pre-project spike (choose stack + architecture doc)

## After Week 8: Project Phase
- Build 2 serious projects (not demo)
- Project 1: AI + Backend integrated app
- Project 2: one domain project (your choice) with proper deployment

## Today Task (Day 1)
- [ ] Agentic AI: complete 1 pending LangGraph topic
- [ ] ML: complete 1 module (preprocessing or regression)
- [ ] Backend: create `FASTAPI/ship-api/` + `/health` + DB connect
- [ ] DSA: solve 2 questions (1 easy, 1 medium)
- [ ] Fill day log

## Daily Log Template
```
Date:
- Agentic AI done:
- ML done:
- Backend done:
- DSA done:
- Blocker:
- Next day first task:
```

## Weekly Scorecard (Sunday)
- Agentic AI progress: __ / 10
- ML progress: __ / 10
- Backend progress: __ / 10
- DSA consistency: __ / 10
- Total score: __ / 40
- Keep / Change for next week:

## Weekly Discipline Add-ons
- Buffer Day (1 day/week): only revision + backlog clear
- Kill List (weekly): topics/tools to pause next week
- Artifact Check (weekly): links/paths to what was actually shipped

## Weekly Artifact Template
```
Week __
- Shipped artifact 1:
- Shipped artifact 2:
- Repo path(s):
- Demo proof (screenshot/video/link):
```
